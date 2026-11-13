from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt

from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

from src.datasets.skin_dataset import CLASS_NAMES
from src.datasets.skin_multimodal_dataset import (
    SkinMultimodalDataset
)
from src.models.skin_multimodal_model import (
    SkinMultimodalModel
)
from src.preprocessing.skin_transforms import eval_transforms


# Configuration
DEVICE = torch.device("cpu")
torch.set_num_threads(2)

CHECKPOINT_PATH = Path(
    "checkpoints/skin_multimodal_best.pth"
)

OUTPUT_DIR = Path("notebooks/eda_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load validation data
dataset = SkinMultimodalDataset(
    csv_path="data/splits/skin/val.csv",
    image_dir="data/skin/images",
    clinical_path="data/processed/skin/val_clinical.npy",
    transform=eval_transforms
)

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

# Load checkpoint
checkpoint = torch.load(
    CHECKPOINT_PATH,
    map_location=DEVICE,
    weights_only=True
)

if checkpoint["class_names"] != CLASS_NAMES:
    raise ValueError("Class order mismatch")

clinical_dim = checkpoint["clinical_dim"]

if clinical_dim != dataset.clinical.shape[1]:
    raise ValueError("Clinical feature dimension mismatch")

model = SkinMultimodalModel(
    clinical_dim=clinical_dim,
    num_classes=len(CLASS_NAMES),
    image_checkpoint=(
        "checkpoints/skin_efficientnet_baseline.pth"
    )
)

model.load_state_dict(checkpoint["model_state_dict"])
model.to(DEVICE)
model.eval()

true_labels = []
predicted_labels = []

# Inference
with torch.no_grad():
    for images, clinical, labels in loader:
        images = images.to(DEVICE)
        clinical = clinical.to(DEVICE)

        outputs = model(images, clinical)
        predictions = outputs.argmax(dim=1)

        true_labels.extend(labels.tolist())
        predicted_labels.extend(
            predictions.cpu().tolist()
        )

true_labels = np.array(true_labels)
predicted_labels = np.array(predicted_labels)

# Metrics
print("\n===== MULTIMODAL VALIDATION RESULTS =====")

accuracy = accuracy_score(
    true_labels, predicted_labels
)

balanced_acc = balanced_accuracy_score(
    true_labels, predicted_labels
)

macro_f1 = f1_score(
    true_labels,
    predicted_labels,
    labels=list(range(len(CLASS_NAMES))),
    average="macro",
    zero_division=0
)

print(f"Accuracy: {accuracy:.4f}")
print(f"Balanced Accuracy: {balanced_acc:.4f}")
print(f"Macro F1: {macro_f1:.4f}")

print("\nClassification Report:\n")

print(classification_report(
    true_labels,
    predicted_labels,
    labels=list(range(len(CLASS_NAMES))),
    target_names=CLASS_NAMES,
    zero_division=0
))

# Confusion matrix
cm = confusion_matrix(
    true_labels,
    predicted_labels,
    labels=list(range(len(CLASS_NAMES)))
)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=CLASS_NAMES
)

fig, ax = plt.subplots(figsize=(9, 7))
disp.plot(
    ax=ax,
    cmap="Blues",
    values_format="d"
)

ax.set_title("Multimodal Skin Model - Validation")
plt.tight_layout()

plot_path = (
    OUTPUT_DIR /
    "skin_multimodal_confusion_matrix.png"
)

plt.savefig(plot_path, dpi=150)
plt.close()

print("\nConfusion matrix saved:", plot_path)
print("===== EVALUATION COMPLETED =====")
