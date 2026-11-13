from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt

from src.datasets.skin_dataset import CLASS_NAMES
from src.datasets.skin_multimodal_dataset import SkinMultimodalDataset
from src.models.skin_multimodal_model import SkinMultimodalModel
from src.preprocessing.skin_transforms import eval_transforms
from src.explainability.skin_clinical_explainer import (
    SkinClinicalExplainer
)


torch.set_num_threads(2)

OUTPUT_DIR = Path("notebooks/eda_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

checkpoint = torch.load(
    "checkpoints/skin_multimodal_best.pth",
    map_location="cpu",
    weights_only=True
)

assert checkpoint["class_names"] == CLASS_NAMES

model = SkinMultimodalModel(
    clinical_dim=checkpoint["clinical_dim"],
    num_classes=6,
    image_checkpoint="checkpoints/skin_efficientnet_baseline.pth"
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

dataset = SkinMultimodalDataset(
    csv_path="data/splits/skin/val.csv",
    image_dir="data/skin/images",
    clinical_path="data/processed/skin/val_clinical.npy",
    transform=eval_transforms
)

image, clinical, true_label = dataset[0]

explainer = SkinClinicalExplainer(model)

result = explainer.explain(
    image.unsqueeze(0),
    clinical.unsqueeze(0),
    steps=32
)

predicted_name = CLASS_NAMES[result["predicted_class"]]
actual_name = CLASS_NAMES[true_label.item()]

contributions = result["contributions"]

assert len(contributions) == 12
assert all(np.isfinite(v) for v in contributions.values())

print("Actual:", actual_name)
print("Predicted:", predicted_name)

print("\nClinical Feature Contributions:")
for name, value in sorted(
    contributions.items(),
    key=lambda item: abs(item[1]),
    reverse=True
):
    print(f"{name:25s}: {value:+.4f}")

# Generate horizontal attribution chart
names = list(contributions.keys())
values = list(contributions.values())

order = np.argsort(np.abs(values))
names = [names[i] for i in order]
values = [values[i] for i in order]

plt.figure(figsize=(9, 6))
plt.barh(names, values)
plt.axvline(0, linewidth=1)
plt.xlabel("Contribution to predicted class logit")
plt.title(
    f"Clinical Attribution: {predicted_name}\n"
    f"Actual: {actual_name}"
)
plt.tight_layout()

output_path = (
    OUTPUT_DIR / "skin_clinical_explanation.png"
)

plt.savefig(output_path, dpi=150)
plt.close()

print("\nSaved:", output_path)
print("Clinical explainability test passed!")
