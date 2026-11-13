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

from src.datasets.retinal_dataset import RetinalDataset
from src.preprocessing.retinal_transforms import eval_transforms
from src.models.retinal_model import build_retinal_model


# ====================================
# 1. CONFIGURATION
# ====================================

DEVICE = torch.device("cpu")
torch.set_num_threads(2)

CHECKPOINT_PATH = Path(
    "checkpoints/retinal_efficientnet_best.pth"
)

OUTPUT_DIR = Path("notebooks/retinal_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = ["DR0", "DR1", "DR2", "DR3", "DR4"]


# ====================================
# 2. LOAD VALIDATION DATA
# ====================================

dataset = RetinalDataset(
    csv_path="data/splits/retinal/val.csv",
    image_dir="data/retinal/images",
    transform=eval_transforms
)

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)


# ====================================
# 3. LOAD TRAINED MODEL
# ====================================

checkpoint = torch.load(
    CHECKPOINT_PATH,
    map_location=DEVICE,
    weights_only=True
)

assert checkpoint["class_names"] == CLASS_NAMES

model = build_retinal_model(
    num_classes=5,
    pretrained=False
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.to(DEVICE)
model.eval()

print("Checkpoint epoch:", checkpoint["epoch"])


# ====================================
# 4. PREDICTIONS
# ====================================

true_labels = []
predicted_labels = []

with torch.no_grad():

    for images, labels in loader:

        images = images.to(DEVICE)

        outputs = model(images)

        predictions = outputs.argmax(dim=1)

        true_labels.extend(labels.tolist())
        predicted_labels.extend(
            predictions.cpu().tolist()
        )


# ====================================
# 5. EVALUATION METRICS
# ====================================

print("\n===== RETINAL VALIDATION RESULTS =====")

accuracy = accuracy_score(
    true_labels,
    predicted_labels
)

balanced_acc = balanced_accuracy_score(
    true_labels,
    predicted_labels
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


# ====================================
# 6. CONFUSION MATRIX
# ====================================

cm = confusion_matrix(
    true_labels,
    predicted_labels,
    labels=list(range(5))
)

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

plt.title("Retinal DR Validation Confusion Matrix")
plt.tight_layout()

output_path = (
    OUTPUT_DIR / "retinal_confusion_matrix.png"
)

plt.savefig(output_path, dpi=150)
plt.close()

print("\nConfusion matrix saved:", output_path)
print("===== EVALUATION COMPLETED =====")
