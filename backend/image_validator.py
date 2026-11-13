from functools import lru_cache
from pathlib import Path

import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0

ROOT = Path(__file__).resolve().parents[1]

CHECKPOINT_PATH = (
    ROOT / "checkpoints/image_type_best.pth"
)

# Provisional threshold. Not yet validated
# on external or unrelated images.
MIN_CONFIDENCE = 0.95

torch.set_num_threads(2)


@lru_cache(maxsize=1)
def load_image_validator():
    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location="cpu",
        weights_only=True
    )

    class_names = checkpoint["class_names"]

    if class_names != ["skin", "retinal"]:
        raise ValueError(
            "Unexpected image-type class order"
        )

    model = efficientnet_b0(weights=None)

    in_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        in_features, 2
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    return model


@torch.inference_mode()
def validate_image_type(image_tensor, expected_type):
    if expected_type not in {"skin", "retinal"}:
        raise ValueError("Unsupported screening type")

    model = load_image_validator()

    logits = model(image_tensor)

    probabilities = torch.softmax(
        logits, dim=1
    )[0]

    confidence, predicted_index = probabilities.max(
        dim=0
    )

    classes = ["skin", "retinal"]

    detected_type = classes[int(predicted_index)]
    confidence = float(confidence)

    accepted = (
        detected_type == expected_type
        and confidence >= MIN_CONFIDENCE
    )

    return {
        "accepted": accepted,
        "detected_type": detected_type,
        "score": round(confidence, 4),
        "reason": (
            "accepted"
            if accepted
            else (
                "image_type_mismatch"
                if detected_type != expected_type
                else "uncertain_image_type"
            )
        )
    }
