from pathlib import Path

import joblib
import torch

from src.models.skin_multimodal_model import SkinMultimodalModel
from src.models.retinal_multimodal_model import RetinalMultimodalModel


DEVICE = torch.device("cpu")
torch.set_num_threads(2)

ROOT = Path(__file__).resolve().parents[1]

_models = {}


def load_models():
    global _models

    if _models:
        return _models

    # Load skin model
    skin_checkpoint = torch.load(
        ROOT / "checkpoints/skin_multimodal_best.pth",
        map_location=DEVICE,
        weights_only=True
    )

    skin_model = SkinMultimodalModel(
        clinical_dim=skin_checkpoint["clinical_dim"],
        num_classes=6,
        image_checkpoint=str(
            ROOT / "checkpoints/skin_efficientnet_baseline.pth"
        )
    )

    skin_model.load_state_dict(
        skin_checkpoint["model_state_dict"]
    )
    skin_model.eval()

    # Load retinal model
    retinal_checkpoint = torch.load(
        ROOT / "checkpoints/retinal_multimodal_best.pth",
        map_location=DEVICE,
        weights_only=True
    )

    retinal_model = RetinalMultimodalModel(
        clinical_dim=retinal_checkpoint["clinical_dim"],
        num_classes=5,
        image_checkpoint=str(
            ROOT / "checkpoints/retinal_efficientnet_best.pth"
        )
    )

    retinal_model.load_state_dict(
        retinal_checkpoint["model_state_dict"]
    )
    retinal_model.eval()

    # Load clinical preprocessors
    skin_preprocessor = joblib.load(
        ROOT / "data/processed/skin/clinical_preprocessor.joblib"
    )

    retinal_preprocessor = joblib.load(
        ROOT / "data/processed/retinal/clinical_preprocessor.joblib"
    )

    _models = {
        "skin_model": skin_model,
        "retinal_model": retinal_model,
        "skin_preprocessor": skin_preprocessor,
        "retinal_preprocessor": retinal_preprocessor
    }

    return _models
