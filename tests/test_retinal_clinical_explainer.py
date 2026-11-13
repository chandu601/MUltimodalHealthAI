from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)
from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)
from src.preprocessing.retinal_transforms import (
    eval_transforms
)
from src.explainability.retinal_clinical_explainer import (
    RetinalClinicalExplainer
)

torch.set_num_threads(2)

checkpoint = torch.load(
    "checkpoints/retinal_multimodal_best.pth",
    map_location="cpu",
    weights_only=True
)

model = RetinalMultimodalModel(
    clinical_dim=checkpoint["clinical_dim"],
    num_classes=5
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

dataset = RetinalMultimodalDataset(
    csv_path="data/splits/retinal/val.csv",
    image_dir="data/retinal/images",
    clinical_path="data/processed/retinal/val_clinical.npy",
    image_ids_path="data/processed/retinal/val_image_ids.csv",
    transform=eval_transforms
)

image, clinical, actual = dataset[0]

explainer = RetinalClinicalExplainer(model)

predicted, contributions = explainer.explain(
    image.unsqueeze(0),
    clinical.unsqueeze(0)
)

print("\n===== RETINAL CLINICAL EXPLANATION =====")
print("Actual grade:", f"DR{actual.item()}")
print("Predicted grade:", f"DR{predicted}")

for feature, value in contributions.items():
    print(f"{feature}: {value:+.4f}")

assert len(contributions) == 3
assert all(np.isfinite(v) for v in contributions.values())

output_dir = Path("notebooks/retinal_outputs")
output_dir.mkdir(parents=True, exist_ok=True)

names = list(contributions.keys())
values = list(contributions.values())

plt.figure(figsize=(8, 4))
plt.barh(names, values)
plt.axvline(0, linewidth=1)
plt.xlabel("Contribution to predicted class logit")
plt.title("Retinal Clinical Feature Attribution")
plt.tight_layout()

output_path = (
    output_dir / "retinal_clinical_explanation.png"
)
plt.savefig(output_path, dpi=150)
plt.close()

print("Saved:", output_path)
print("Retinal clinical explanation test passed!")
