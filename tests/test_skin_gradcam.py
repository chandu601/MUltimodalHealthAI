from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt

from src.datasets.skin_dataset import CLASS_NAMES
from src.datasets.skin_multimodal_dataset import (
    SkinMultimodalDataset
)
from src.models.skin_multimodal_model import (
    SkinMultimodalModel
)
from src.preprocessing.skin_transforms import eval_transforms
from src.explainability.skin_gradcam import SkinGradCAM


torch.set_num_threads(2)

OUTPUT_DIR = Path("notebooks/eda_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_PATH = "checkpoints/skin_multimodal_best.pth"

checkpoint = torch.load(
    CHECKPOINT_PATH,
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

# Use validation data only
dataset = SkinMultimodalDataset(
    csv_path="data/splits/skin/val.csv",
    image_dir="data/skin/images",
    clinical_path="data/processed/skin/val_clinical.npy",
    transform=eval_transforms
)

image, clinical, true_label = dataset[0]

gradcam = SkinGradCAM(model)

result = gradcam.generate(
    image.unsqueeze(0),
    clinical.unsqueeze(0)
)

heatmap = result["heatmap"]

assert heatmap.shape == (224, 224)
assert np.isfinite(heatmap).all()

# Undo ImageNet normalization for display
mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)

original = (image * std + mean).clamp(0, 1)
original = original.permute(1, 2, 0).numpy()

predicted = CLASS_NAMES[result["predicted_class"]]
actual = CLASS_NAMES[true_label.item()]

fig, axes = plt.subplots(1, 3, figsize=(12, 4))

axes[0].imshow(original)
axes[0].set_title("Original Image")

axes[1].imshow(heatmap, cmap="jet", vmin=0, vmax=1)
axes[1].set_title("Grad-CAM Heatmap")

axes[2].imshow(original)
axes[2].imshow(
    heatmap,
    cmap="jet",
    alpha=0.4,
    vmin=0,
    vmax=1
)
axes[2].set_title("Grad-CAM Overlay")

for ax in axes:
    ax.axis("off")

fig.suptitle(
    f"Actual: {actual} | Predicted: {predicted} | "
    f"Probability: {result['probability']:.2%}"
)

plt.tight_layout()

output_path = OUTPUT_DIR / "skin_gradcam_example.png"
plt.savefig(output_path, dpi=150)
plt.close()

gradcam.close()

print("Actual class:", actual)
print("Predicted class:", predicted)
print("Model probability:", round(result["probability"], 4))
print("Heatmap shape:", heatmap.shape)
print("Visualization saved:", output_path)
print("Grad-CAM test passed!")
