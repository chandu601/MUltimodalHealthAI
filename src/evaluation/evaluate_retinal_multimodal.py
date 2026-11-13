from pathlib import Path

import torch
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    cohen_kappa_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)
from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)
from src.preprocessing.retinal_transforms import eval_transforms


# 1. Configuration
torch.set_num_threads(2)

DEVICE = torch.device("cpu")
CLASS_NAMES = ["DR0", "DR1", "DR2", "DR3", "DR4"]

OUTPUT_DIR = Path("notebooks/retinal_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# 2. Load validation dataset
dataset = RetinalMultimodalDataset(
    csv_path="data/splits/retinal/val.csv",
    image_dir="data/retinal/images",
    clinical_path="data/processed/retinal/val_clinical.npy",
    image_ids_path="data/processed/retinal/val_image_ids.csv",
    transform=eval_transforms
)

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)


# 3. Load trained multimodal checkpoint
checkpoint = torch.load(
    "checkpoints/retinal_multimodal_best.pth",
    map_location=DEVICE,
    weights_only=True
)

assert checkpoint["class_names"] == CLASS_NAMES

assert checkpoint["clinical_dim"] == dataset.clinical.shape[1]

model = RetinalMultimodalModel(
    clinical_dim=checkpoint["clinical_dim"],
    num_classes=5,
    image_checkpoint="checkpoints/retinal_efficientnet_best.pth"
)

model.load_state_dict(checkpoint["model_state_dict"])
model.to(DEVICE)
model.eval()

print("Best checkpoint epoch:", checkpoint["epoch"])


# 4. Generate predictions
true_labels = []
predicted_labels = []

with torch.no_grad():
    for images, clinical, labels in loader:

        outputs = model(
            images.to(DEVICE),
            clinical.to(DEVICE)
        )

        predictions = outputs.argmax(dim=1)

        true_labels.extend(labels.tolist())
        predicted_labels.extend(
            predictions.cpu().tolist()
        )


# 5. Compute metrics
accuracy = accuracy_score(
    true_labels, predicted_labels
)

balanced_acc = balanced_accuracy_score(
    true_labels, predicted_labels
)

macro_f1 = f1_score(
    true_labels,
    predicted_labels,
    labels=list(range(5)),
    average="macro",
    zero_division=0
)

qwk = cohen_kappa_score(
    true_labels,
    predicted_labels,
    labels=list(range(5)),
    weights="quadratic"
)

print("\n===== RETINAL MULTIMODAL VALIDATION =====")

print(f"Accuracy: {accuracy:.4f}")
print(f"Balanced Accuracy: {balanced_acc:.4f}")
print(f"Macro F1: {macro_f1:.4f}")
print(f"Quadratic Weighted Kappa: {qwk:.4f}")

print("\nClassification Report:\n")

print(classification_report(
    true_labels,
    predicted_labels,
    labels=list(range(5)),
    target_names=CLASS_NAMES,
    zero_division=0
))


# 6. Confusion matrix
cm = confusion_matrix(
    true_labels,
    predicted_labels,
    labels=list(range(5))
)

print("\nConfusion Matrix:\n", cm)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=CLASS_NAMES
)

fig, ax = plt.subplots(figsize=(8, 7))

display.plot(
    ax=ax,
    cmap="Blues",
    values_format="d"
)

ax.set_title("Retinal Multimodal Validation")
plt.tight_layout()

output_path = (
    OUTPUT_DIR / "retinal_multimodal_confusion_matrix.png"
)

plt.savefig(output_path, dpi=150)
plt.close()

print("\nSaved:", output_path)
print("Retinal multimodal evaluation completed!")
