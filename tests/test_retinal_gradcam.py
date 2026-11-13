from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)
from src.preprocessing.retinal_transforms import eval_transforms
from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)
from src.explainability.skin_gradcam import SkinGradCAM


torch.set_num_threads(2)

OUTPUT_DIR = Path("notebooks/retinal_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = ["DR0", "DR1", "DR2", "DR3", "DR4"]

# Load trained checkpoint
checkpoint = torch.load(
    "checkpoints/retinal_multimodal_best.pth",
    map_location="cpu",
    weights_only=True
)

assert checkpoint["class_names"] == CLASS_NAMES

model = RetinalMultimodalModel(
    clinical_dim=checkpoint["clinical_dim"],
    num_classes=5,
    image_checkpoint=(
        "checkpoints/retinal_efficientnet_best.pth"
    )
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Load validation dataset
dataset = RetinalMultimodalDataset(
    csv_path="data/splits/retinal/val.csv",
    image_dir="data/retinal/images",
    clinical_path="data/processed/retinal/val_clinical.npy",
    image_ids_path="data/processed/retinal/val_image_ids.csv",
    transform=eval_transforms
)

image, clinical, label = dataset[0]

# Grad-CAM works on the retinal model because
# its image encoder has the same EfficientNet structure.
gradcam = SkinGradCAM(model)

result = gradcam.generate(
    image.unsqueeze(0),
    clinical.unsqueeze(0)
)

heatmap = result["heatmap"]

assert heatmap.shape == (224, 224)
assert np.isfinite(heatmap).all()

predicted = CLASS_NAMES[result["predicted_class"]]
actual = CLASS_NAMES[label.item()]

# Undo ImageNet normalization
mean = torch.tensor(
    [0.485, 0.456, 0.406]
).view(3, 1, 1)

std = torch.tensor(
    [0.229, 0.224, 0.225]
).view(3, 1, 1)

original = (
    image * std + mean
).clamp(0, 1)

original = original.permute(
    1, 2, 0
).numpy()

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

axes[0].imshow(original)
axes[0].set_title("Original Fundus Image")

axes[1].imshow(
    heatmap,
    cmap="jet",
    vmin=0,
    vmax=1
)
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

output_path = (
    OUTPUT_DIR / "retinal_gradcam_example.png"
)

plt.savefig(output_path, dpi=150)
plt.close()

gradcam.close()

print("\n===== RETINAL GRAD-CAM RESULTS =====")
print("Actual grade:", actual)
print("Predicted grade:", predicted)
print(
    "Model probability:",
    round(result["probability"], 4)
)
print("Heatmap shape:", heatmap.shape)
print("Saved:", output_path)
print("Retinal Grad-CAM test passed!")
