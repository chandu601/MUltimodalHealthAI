import base64
import io

import numpy as np
import torch
import matplotlib.pyplot as plt

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile
)

from backend.model_loader import load_models
from backend.image_validator import validate_image_type

from backend.prediction_api import (
    load_image,
    parse_metadata,
    encode_metadata,
    RETINAL_NUMERIC,
    RETINAL_CATEGORICAL
)

from src.preprocessing.retinal_transforms import (
    eval_transforms
)

from src.explainability.skin_gradcam import (
    SkinGradCAM
)

from src.explainability.retinal_clinical_explainer import (
    RetinalClinicalExplainer
)


router = APIRouter(
    prefix="/explain",
    tags=["Explainability"]
)

CLASS_NAMES = ["DR0", "DR1", "DR2", "DR3", "DR4"]


@router.post("/retinal")
async def explain_retinal(
    file: UploadFile = File(...),
    metadata: str = Form(...)
):

    # 1. Decode the uploaded fundus image
    image_tensor = await load_image(
        file, eval_transforms
    )

    # 2. Validate image type
    validation = validate_image_type(
        image_tensor,
        expected_type="retinal"
    )

    if not validation["accepted"]:
        raise HTTPException(
            status_code=422,
            detail={
                "message": (
                    "The image could not be verified as "
                    "a suitable retinal image."
                ),
                "reason": validation["reason"]
            }
        )

    # 3. Load the model and preprocessor
    models = load_models()

    model = models["retinal_model"]
    preprocessor = models["retinal_preprocessor"]

    # 4. Process patient clinical information
    clinical_frame = parse_metadata(
        metadata,
        RETINAL_NUMERIC,
        RETINAL_CATEGORICAL
    )

    clinical_tensor = encode_metadata(
        clinical_frame,
        preprocessor,
        RETINAL_CATEGORICAL
    )

    # 5. Generate Grad-CAM
    # Do not use torch.inference_mode() here.
    gradcam = SkinGradCAM(model)

    try:
        result = gradcam.generate(
            image_tensor,
            clinical_tensor
        )
    finally:
        gradcam.close()

    heatmap = result["heatmap"]

    # 6. Generate clinical attributions
    clinical_explainer = RetinalClinicalExplainer(
        model
    )

    _, contributions = clinical_explainer.explain(
        image_tensor,
        clinical_tensor
    )

    # 7. Recover original RGB image for display
    mean = torch.tensor(
        [0.485, 0.456, 0.406]
    ).view(3, 1, 1)

    std = torch.tensor(
        [0.229, 0.224, 0.225]
    ).view(3, 1, 1)

    original = (
        image_tensor[0].detach() * std + mean
    ).clamp(0, 1)

    original = original.permute(
        1, 2, 0
    ).cpu().numpy()

    # 8. Create overlay
    fig, ax = plt.subplots(figsize=(5, 5))

    ax.imshow(original)

    ax.imshow(
        heatmap,
        cmap="jet",
        alpha=0.4,
        vmin=0,
        vmax=1
    )

    ax.axis("off")

    buffer = io.BytesIO()

    try:
        fig.savefig(
            buffer,
            format="png",
            dpi=120,
            bbox_inches="tight",
            pad_inches=0
        )
    finally:
        plt.close(fig)

    buffer.seek(0)

    encoded_image = base64.b64encode(
        buffer.read()
    ).decode("utf-8")

    predicted_class = CLASS_NAMES[
        result["predicted_class"]
    ]

    return {
        "screening_type": "retinal",
        "predicted_class": predicted_class,
        "visual_explanation": encoded_image,
        "visual_explanation_format": "png",
        "clinical_contributions": {
            name: round(float(value), 4)
            for name, value in contributions.items()
        },
        "disclaimer": (
            "These explanations describe model "
            "behavior, not medically verified disease "
            "regions or causal clinical risk factors."
        )
    }
