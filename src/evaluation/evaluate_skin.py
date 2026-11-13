
from pathlib import Path

import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score
)
from torch.utils.data import DataLoader

from src.datasets.skin_dataset import SkinDataset, CLASS_NAMES
from src.preprocessing.skin_transforms import eval_transforms
from src.models.skin_model import build_skin_model


DEVICE = torch.device("cpu")
torch.set_num_threads(2)

CHECKPOINT = Path("checkpoints/skin_efficientnet_best.pth")
OUTPUT_DIR = Path("notebooks/eda_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not CHECKPOINT.exists():
    raise FileNotFoundError(
        f"Model checkpoint not found: {CHECKPOINT}"
    )

# Load the validation dataset.
# Test data remains untouched until final evaluation.
dataset = SkinDataset(
    csv_path="data/splits/skin/val.csv",
    image_dir="data/skin/images",
    transform=eval_transforms
)

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

# Load saved checkpoint
checkpoint = torch.load(
    CHECKPOINT,
    map_location=DEVICE,
    weights_only=True
)

saved_classes = checkpoint["class_names"]

if saved_classes != CLASS_NAMES:
    raise ValueError("Checkpoint class order does not match dataset")

model = build_skin_model(
    num_classes=len(CLASS_NAMES),
    pretrained=False
)

model.load_state_dict(checkpoint["model_state_dict"])
model.to(DEVICE)
model.eval()

all_true = []
all_pred = []

with torch.no_grad():
    for images, labels in loader:
        images = images.to(DEVICE)

        outputs = model(images)
        predictions = outputs.argmax(dim=1)

        all_true.extend(labels.numpy())
        all_pred.extend(predictions.cpu().numpy())

all_true = np.array(all_true)
all_pred = np.array(all_pred)

print("\n===== SKIN MODEL VALIDATION =====")

print("Validation accuracy:",
      round(accuracy_score(all_true, all_pred), 4))

print("Balanced accuracy:",
      round(balanced_accuracy_score(all_true, all_pred), 4))

print("Macro F1:",
      round(f1_score(
          all_true, all_pred,
          labels=list(range(len(CLASS_NAMES))),
          average="macro",
          zero_division=0
      ), 4))

print("\nClassification Report:\n")

print(classification_report(
    all_true,
    all_pred,
    labels=list(range(len(CLASS_NAMES))),
    target_names=CLASS_NAMES,
    zero_division=0
))

cm = confusion_matrix(
    all_true,
    all_pred,
    labels=list(range(len(CLASS_NAMES)))
)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=CLASS_NAMES
)

fig, ax = plt.subplots(figsize=(8, 7))
display.plot(ax=ax, cmap="Blues", values_format="d")
plt.title("Skin Lesion Validation Confusion Matrix")
plt.tight_layout()

output_path = OUTPUT_DIR / "skin_validation_confusion_matrix.png"
plt.savefig(output_path, dpi=150)
plt.close()

print("Confusion matrix saved to:", output_path)

print("\n===== VALIDATION COMPLETED =====")
