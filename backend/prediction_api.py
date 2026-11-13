import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from PIL import Image, UnidentifiedImageError
from backend.image_quality_validator import validate_image_quality

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile
)

from backend.model_loader import load_models
from backend.image_validator import validate_image_type

from src.preprocessing.skin_transforms import (
    eval_transforms as skin_transforms
)

from src.preprocessing.retinal_transforms import (
    eval_transforms as retinal_transforms
)


# ==========================================
# 1. CONFIGURATION
# ==========================================

router = APIRouter(
    prefix="/predict",
    tags=["Predictions"]
)

ROOT = Path(__file__).resolve().parents[1]

MAX_FILE_SIZE = 12 * 1024 * 1024

Image.MAX_IMAGE_PIXELS = 20_000_000

SKIN_CLASSES = [
    "ACK", "BCC", "MEL",
    "NEV", "SCC", "SEK"
]

RETINAL_CLASSES = [
    "DR0", "DR1", "DR2", "DR3", "DR4"
]

SKIN_NUMERIC = [
    "age",
    "diameter_1",
    "diameter_2"
]

SKIN_CATEGORICAL = [
    "gender",
    "region",
    "itch",
    "grew",
    "hurt",
    "changed",
    "bleed",
    "elevation",
    "skin_cancer_history"
]

RETINAL_NUMERIC = ["age"]

RETINAL_CATEGORICAL = [
    "sexe",
    "type_diabete"
]


# ==========================================
# 2. PARSE CLINICAL METADATA
# ==========================================

def parse_metadata(
    raw_text,
    numeric_cols,
    categorical_cols
):

    try:
        data = json.loads(raw_text)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=422,
            detail="Clinical metadata must be valid JSON."
        )

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=422,
            detail="Clinical metadata must be a JSON object."
        )

    required = set(
        numeric_cols + categorical_cols
    )

    missing_fields = required - set(data.keys())
    extra_fields = set(data.keys()) - required

    if missing_fields or extra_fields:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Invalid clinical metadata fields.",
                "missing_fields": sorted(missing_fields),
                "unexpected_fields": sorted(extra_fields)
            }
        )

    row = {}

    # Process numerical values
    for column in numeric_cols:

        value = data[column]

        if value is None or value == "":
            row[column] = np.nan
            continue

        if isinstance(value, bool):
            raise HTTPException(
                status_code=422,
                detail=f"{column} must be numeric."
            )

        try:
            number = float(value)

        except (TypeError, ValueError):
            raise HTTPException(
                status_code=422,
                detail=f"{column} must be numeric."
            )

        if not np.isfinite(number):
            raise HTTPException(
                status_code=422,
                detail=f"{column} must be finite."
            )

        if number < 0:
            raise HTTPException(
                status_code=422,
                detail=f"{column} cannot be negative."
            )

        if column == "age" and number > 120:
            raise HTTPException(
                status_code=422,
                detail="Age must be between 0 and 120."
            )

        row[column] = number

    # Process categorical values
    for column in categorical_cols:

        value = data[column]

        if value is None or value == "":
            row[column] = "Missing"

        elif isinstance(value, (str, bool, int, float)):
            row[column] = str(value)

        else:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid value for {column}."
            )

    return pd.DataFrame(
        [row],
        columns=numeric_cols + categorical_cols
    )


# ==========================================
# 3. ENCODE CLINICAL DATA
# ==========================================

def encode_metadata(
    frame,
    preprocessor,
    categorical_cols
):

    encoder = (
        preprocessor
        .named_transformers_["categorical"]
        .named_steps["encoder"]
    )

    # Ensure submitted categories were seen
    # during training.
    for column, allowed in zip(
        categorical_cols,
        encoder.categories_
    ):

        value = frame.iloc[0][column]

        allowed_values = {
            str(item) for item in allowed
        }

        if str(value) not in allowed_values:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": (
                        f"Unsupported value for {column}."
                    ),
                    "field": column,
                    "received": str(value),
                    "allowed_values": sorted(allowed_values)
                }
            )

    try:
        encoded = preprocessor.transform(frame)

        if hasattr(encoded, "toarray"):
            encoded = encoded.toarray()

        encoded = np.asarray(
            encoded,
            dtype=np.float32
        )

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail="Unable to process clinical information."
        ) from exc

    if not np.isfinite(encoded).all():
        raise HTTPException(
            status_code=422,
            detail="Invalid encoded clinical data."
        )

    return torch.from_numpy(encoded)


# ==========================================
# 4. LOAD AND VALIDATE IMAGE FILE
# ==========================================

async def load_image(file, transform):

    if file.content_type not in {
        "image/jpeg",
        "image/png"
    }:
        raise HTTPException(
            status_code=415,
            detail="Please upload a JPG or PNG image."
        )

    content = await file.read(
        MAX_FILE_SIZE + 1
    )

    if not content:
        raise HTTPException(
            status_code=422,
            detail="The uploaded image is empty."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 12 MB."
        )

    try:
        with Image.open(
            io.BytesIO(content)
        ) as image:

            image.load()

            rgb_image = image.convert("RGB")

            image_tensor = transform(
                rgb_image
            ).unsqueeze(0)

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError
    ) as exc:

        raise HTTPException(
            status_code=422,
            detail="The uploaded image could not be read."
        ) from exc

    return image_tensor


# ==========================================
# 5. APPLY TEMPERATURE CALIBRATION
# ==========================================

def calibrated_probabilities(
    logits,
    calibration_filename,
    expected_classes
):

    calibration_path = (
        ROOT / "checkpoints" / calibration_filename
    )

    temperature = 1.0
    calibration_applied = False

    if calibration_path.exists():

        with calibration_path.open(
            "r", encoding="utf-8"
        ) as handle:

            config = json.load(handle)

        saved_classes = config.get("class_names")

        if saved_classes != expected_classes:
            raise RuntimeError(
                "Calibration class order mismatch."
            )

        temperature = float(
            config["temperature"]
        )

        if (
            not np.isfinite(temperature)
            or temperature <= 0
        ):
            raise RuntimeError(
                "Invalid calibration temperature."
            )

        calibration_applied = True

    probabilities = torch.softmax(
        logits / temperature,
        dim=1
    )[0]

    return (
        probabilities.detach().cpu().tolist(),
        calibration_applied
    )


# ==========================================
# 6. MAIN PREDICTION FUNCTION
# ==========================================

async def predict(
    kind,
    file,
    metadata
):

    if kind == "skin":

        numeric_cols = SKIN_NUMERIC
        categorical_cols = SKIN_CATEGORICAL

        class_names = SKIN_CLASSES
        transform = skin_transforms

        model_key = "skin_model"
        preprocessor_key = "skin_preprocessor"

        calibration_file = "skin_temperature.json"

    elif kind == "retinal":

        numeric_cols = RETINAL_NUMERIC
        categorical_cols = RETINAL_CATEGORICAL

        class_names = RETINAL_CLASSES
        transform = retinal_transforms

        model_key = "retinal_model"
        preprocessor_key = "retinal_preprocessor"

        calibration_file = "retinal_temperature.json"

    else:
        raise HTTPException(
            status_code=404,
            detail="Unknown screening type."
        )

    # Step A: Decode the uploaded image
    image_tensor = await load_image(
        file,
        transform
    )

    # Step B: Verify skin or retinal image type
    validation = validate_image_type(
        image_tensor,
        expected_type=kind
    )

    if not validation["accepted"]:

        if validation["reason"] == "image_type_mismatch":
            message = (
                "The uploaded image appears to belong "
                "to a different screening category. "
                "Please check the image and selected "
                "screening type."
            )

        else:
            message = (
                "The image type could not be verified "
                "with sufficient certainty. Please "
                "upload a suitable medical image."
            )

        raise HTTPException(
            status_code=422,
            detail={
                "error": "image_validation_failed",
                "message": message,
                "reason": validation["reason"]
            }
        )

    # Experimental image-quality assessment.
    # Generate warnings only; never reject here.
    await file.seek(0)

    try:
        with Image.open(file.file) as image:
            image_quality = validate_image_quality(
                image.convert("RGB")
            )
    finally:
        await file.seek(0)


    # Step C: Parse the clinical information
    clinical_frame = parse_metadata(
        metadata,
        numeric_cols,
        categorical_cols
    )

    # Step D: Load both trained models and
    # their associated preprocessors
    models = load_models()

    model = models[model_key]

    preprocessor = models[
        preprocessor_key
    ]

    # Step E: Encode clinical information
    clinical_tensor = encode_metadata(
        clinical_frame,
        preprocessor,
        categorical_cols
    )

    # Step F: Run disease classification
    model.eval()

    with torch.inference_mode():

        logits = model(
            image_tensor,
            clinical_tensor
        )

    # Step G: Calculate class probabilities
    probabilities, calibrated = (
        calibrated_probabilities(
            logits,
            calibration_file,
            class_names
        )
    )

    predicted_index = int(
        np.argmax(probabilities)
    )

    predicted_class = class_names[
        predicted_index
    ]

    # Step H: Return response
    return {
        "screening_type": kind,
        "image_quality": {
            **image_quality,
            "mode": "experimental_warning_only"
        },

        "predicted_class": predicted_class,

        "predicted_index": predicted_index,

        "model_probability": round(
            float(probabilities[predicted_index]),
            4
        ),

        "calibration_applied": calibrated,

        "image_type_validated": True,

        "class_probabilities": {
            name: round(float(probability), 4)
            for name, probability in zip(
                class_names,
                probabilities
            )
        },

        "disclaimer": (
            "Experimental AI screening result. "
            "This is not a medical diagnosis. "
            "Predictions and probabilities are not "
            "clinically validated. "
            "Please consult a qualified clinician."
        )
    }


# ==========================================
# 7. SKIN PREDICTION ENDPOINT
# ==========================================

@router.post("/skin")
async def predict_skin(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):

    return await predict(
        kind="skin",
        file=file,
        metadata=metadata
    )


# ==========================================
# 8. RETINAL PREDICTION ENDPOINT
# ==========================================

@router.post("/retinal")
async def predict_retinal(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):

    return await predict(
        kind="retinal",
        file=file,
        metadata=metadata
    )
