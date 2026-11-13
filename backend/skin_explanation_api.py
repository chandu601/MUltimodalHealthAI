import base64
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import torch

from PIL import Image

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from backend.model_loader import load_models
from backend.image_validator import validate_image_type

from backend.prediction_api import (
    load_image,
    parse_metadata,
    encode_metadata,
    SKIN_NUMERIC,
    SKIN_CATEGORICAL,
    SKIN_CLASSES,
)

from src.preprocessing.skin_transforms import (
    eval_transforms,
)

from src.explainability.skin_gradcam import (
    SkinGradCAM,
)


# ==================================================
# 1. CONFIGURATION
# ==================================================

router = APIRouter(
    prefix="/explain",
    tags=["Skin Explainability"],
)

ROOT = Path(__file__).resolve().parents[1]

CLASS_NAMES = list(SKIN_CLASSES)

IG_STEPS = 24

MEAN = np.array(
    [0.485, 0.456, 0.406],
    dtype=np.float32,
)

STD = np.array(
    [0.229, 0.224, 0.225],
    dtype=np.float32,
)


# ==================================================
# 2. IMAGE HELPERS
# ==================================================

def recover_rgb_image(image_tensor):
    """
    Reverse ImageNet normalization for visualization.
    """

    image = (
        image_tensor[0]
        .detach()
        .cpu()
        .permute(1, 2, 0)
        .numpy()
    )

    image = image * STD + MEAN

    image = np.clip(image, 0.0, 1.0)

    return image


def prepare_heatmap(heatmap, height, width):
    """
    Convert Grad-CAM output into a 2D heatmap
    with the same dimensions as the input image.
    """

    if isinstance(heatmap, torch.Tensor):
        heatmap = (
            heatmap.detach().cpu().numpy()
        )

    heatmap = np.asarray(
        heatmap,
        dtype=np.float32,
    ).squeeze()

    if heatmap.ndim != 2:
        raise RuntimeError(
            "Grad-CAM did not return a 2D heatmap."
        )

    heatmap = np.nan_to_num(
        heatmap,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    heatmap = np.clip(heatmap, 0.0, None)

    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    if heatmap.shape != (height, width):

        heatmap_image = Image.fromarray(
            heatmap,
            mode="F",
        )

        heatmap_image = heatmap_image.resize(
            (width, height),
            Image.Resampling.BILINEAR,
        )

        heatmap = np.asarray(
            heatmap_image,
            dtype=np.float32,
        )

    return np.clip(
        heatmap,
        0.0,
        1.0,
    )


def create_gradcam_image(
    image_tensor,
    heatmap,
):
    """
    Create a PNG overlay and return Base64 text.
    """

    original = recover_rgb_image(
        image_tensor
    )

    height, width = original.shape[:2]

    heatmap = prepare_heatmap(
        heatmap,
        height,
        width,
    )

    figure, axis = plt.subplots(
        figsize=(5, 5),
    )

    axis.imshow(original)

    axis.imshow(
        heatmap,
        cmap="jet",
        alpha=0.4,
        vmin=0,
        vmax=1,
    )

    axis.axis("off")

    buffer = io.BytesIO()

    try:
        figure.savefig(
            buffer,
            format="png",
            dpi=120,
            bbox_inches="tight",
            pad_inches=0,
        )

    finally:
        plt.close(figure)

    buffer.seek(0)

    return base64.b64encode(
        buffer.read()
    ).decode("utf-8")


# ==================================================
# 3. CLINICAL FEATURE NAMES
# ==================================================

def get_clinical_feature_names(
    preprocessor,
    feature_count,
):
    """
    Obtain the output feature names from the
    fitted training preprocessor.
    """

    try:

        names = list(
            preprocessor.get_feature_names_out()
        )

    except (AttributeError, ValueError, TypeError):

        names = [
            f"feature_{index}"
            for index in range(feature_count)
        ]

    if len(names) != feature_count:

        raise RuntimeError(
            "Clinical feature names and dimensions "
            "do not match."
        )

    return [
        str(name)
        for name in names
    ]


def group_feature_contributions(feature_names, attributions):
    columns = SKIN_NUMERIC + SKIN_CATEGORICAL
    groups = {column: 0.0 for column in columns}

    if len(feature_names) != len(attributions):
        raise ValueError("Feature count mismatch.")

    unmatched = []

    for feature, value in zip(feature_names, attributions):
        name = str(feature).split("__", 1)[-1]

        if name.startswith("missingindicator_"):
            name = name[len("missingindicator_"):]

        match = next(
            (
                column for column in sorted(
                    columns, key=len, reverse=True
                )
                if name == column
                or name.startswith(column + "_")
            ),
            None
        )

        if match is None:
            unmatched.append(str(feature))
        else:
            groups[match] += float(value)

    if unmatched:
        raise RuntimeError(
            "Unmapped features: " + ", ".join(unmatched)
        )

    return {
        key: round(value, 6)
        for key, value in groups.items()
    }



def clinical_integrated_gradients(
    model,
    image_tensor,
    clinical_tensor,
    target_class,
    steps=IG_STEPS,
):
    """
    Integrated Gradients with respect to the
    clinical input only.

    The image remains fixed.

    Baseline: all-zero encoded feature vector.

    Scores: uncalibrated model logits.
    """

    model.eval()

    original = clinical_tensor.detach()

    baseline = torch.zeros_like(original)

    difference = original - baseline

    total_gradient = torch.zeros_like(original)

    # Trapezoidal integration approximation.
    for step in range(steps + 1):

        alpha = step / steps

        interpolated = (
            baseline + alpha * difference
        )

        interpolated = (
            interpolated.detach()
            .requires_grad_(True)
        )

        with torch.enable_grad():

            logits = model(
                image_tensor,
                interpolated,
            )

            target_score = logits[
                0,
                target_class,
            ]

            gradient = torch.autograd.grad(
                outputs=target_score,
                inputs=interpolated,
                retain_graph=False,
                create_graph=False,
            )[0]

        weight = (
            0.5
            if step in (0, steps)
            else 1.0
        )

        total_gradient += (
            weight * gradient.detach()
        )

    average_gradient = (
        total_gradient / steps
    )

    attributions = (
        difference * average_gradient
    )

    return (
        attributions[0]
        .detach()
        .cpu()
        .numpy()
    )


# ==================================================
# 5. SKIN EXPLANATION ENDPOINT
# ==================================================

@router.post("/skin")
async def explain_skin(
    file: UploadFile = File(...),
    metadata: str = Form(...),
):

    # ------------------------------------------
    # A. Load image
    # ------------------------------------------

    image_tensor = await load_image(
        file,
        eval_transforms,
    )

    # ------------------------------------------
    # B. Validate image type
    # ------------------------------------------

    validation = validate_image_type(
        image_tensor,
        expected_type="skin",
    )

    if not validation["accepted"]:

        raise HTTPException(
            status_code=422,
            detail={
                "error": "image_validation_failed",
                "message": (
                    "The uploaded image was not accepted "
                    "as a skin image. Please check the "
                    "selected screening type and image."
                ),
                "reason": validation["reason"],
            },
        )

    # ------------------------------------------
    # C. Load existing trained skin model
    # ------------------------------------------

    models = load_models()

    model = models["skin_model"]

    preprocessor = models[
        "skin_preprocessor"
    ]

    model.eval()

    # ------------------------------------------
    # D. Preprocess clinical information
    # ------------------------------------------

    clinical_frame = parse_metadata(
        metadata,
        SKIN_NUMERIC,
        SKIN_CATEGORICAL,
    )

    clinical_tensor = encode_metadata(
        clinical_frame,
        preprocessor,
        SKIN_CATEGORICAL,
    )

    # ------------------------------------------
    # E. Obtain predicted class
    # ------------------------------------------

    with torch.no_grad():

        logits = model(
            image_tensor,
            clinical_tensor,
        )

        target_class = int(
            logits.argmax(dim=1).item()
        )

    # ------------------------------------------
    # F. Generate skin Grad-CAM
    # ------------------------------------------

    gradcam = SkinGradCAM(model)

    try:

        with torch.enable_grad():

            cam_result = gradcam.generate(
                image_tensor,
                clinical_tensor,
                target_class=target_class,
            )

    finally:

        gradcam.close()

    heatmap = cam_result["heatmap"]

    encoded_overlay = create_gradcam_image(
        image_tensor,
        heatmap,
    )

    # ------------------------------------------
    # G. Clinical Integrated Gradients
    # ------------------------------------------

    attributions = clinical_integrated_gradients(
        model,
        image_tensor,
        clinical_tensor,
        target_class,
    )

    names = get_clinical_feature_names(
        preprocessor,
        len(attributions),
    )

    grouped_contributions = (
        group_feature_contributions(
            names,
            attributions,
        )
    )

    # ------------------------------------------
    # H. Return explanation
    # ------------------------------------------

    return {
        "screening_type": "skin",

        "predicted_class": CLASS_NAMES[
            target_class
        ],

        "predicted_index": target_class,

        "visual_explanation": encoded_overlay,

        "visual_explanation_format": "png",

        "clinical_contributions": (
            grouped_contributions
        ),

        "attribution_method": (
            "Integrated Gradients"
        ),

        "attribution_baseline": (
            "All-zero encoded clinical vector"
        ),

        "disclaimer": (
            "Experimental research explanation only. "
            "Grad-CAM highlights model-influential "
            "image regions, not confirmed lesions. "
            "Clinical contributions are relative "
            "logit attributions, not medical risk "
            "estimates or causal explanations. "
            "This system is not clinically validated."
        ),
    }
