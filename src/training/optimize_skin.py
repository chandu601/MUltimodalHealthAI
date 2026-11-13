from pathlib import Path
import csv
import random

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, f1_score

from src.datasets.skin_dataset import SkinDataset, CLASS_NAMES
from src.preprocessing.skin_transforms import (
    train_transforms,
    eval_transforms
)
from src.models.skin_model import build_skin_model


# ==========================================
# 1. CONFIGURATION
# ==========================================

SEED = 42
EPOCHS = 8
PATIENCE = 3
BATCH_SIZE = 8
LEARNING_RATE = 0.0003

DEVICE = torch.device("cpu")
torch.set_num_threads(2)

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

CHECKPOINT_DIR = Path("checkpoints")
RESULTS_DIR = Path("notebooks/training_outputs")

CHECKPOINT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_PATH = (
    CHECKPOINT_DIR / "skin_efficientnet_baseline.pth"
)

BEST_PATH = (
    CHECKPOINT_DIR / "skin_efficientnet_best.pth"
)

HISTORY_PATH = RESULTS_DIR / "skin_optimization_history.csv"


# ==========================================
# 2. LOAD DATASETS
# ==========================================

train_csv = "data/splits/skin/train.csv"
val_csv = "data/splits/skin/val.csv"
image_dir = "data/skin/images"

train_dataset = SkinDataset(
    train_csv, image_dir, train_transforms
)

val_dataset = SkinDataset(
    val_csv, image_dir, eval_transforms
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

print("Training images:", len(train_dataset))
print("Validation images:", len(val_dataset))


# ==========================================
# 3. CLASS-WEIGHTED LOSS
# ==========================================

train_df = pd.read_csv(train_csv)

counts = np.array([
    (train_df["diagnostic"] == name).sum()
    for name in CLASS_NAMES
])

if np.any(counts == 0):
    raise ValueError("Training split has a missing class")

weights = len(train_df) / (len(CLASS_NAMES) * counts)

class_weights = torch.tensor(
    weights, dtype=torch.float32, device=DEVICE
)

criterion = nn.CrossEntropyLoss(weight=class_weights)


# ==========================================
# 4. LOAD SAVED BASELINE
# ==========================================

if not BASELINE_PATH.exists():
    raise FileNotFoundError(
        f"Baseline checkpoint missing: {BASELINE_PATH}"
    )

checkpoint = torch.load(
    BASELINE_PATH,
    map_location=DEVICE,
    weights_only=True
)

if checkpoint["class_names"] != CLASS_NAMES:
    raise ValueError("Checkpoint class order mismatch")

model = build_skin_model(
    num_classes=len(CLASS_NAMES),
    pretrained=False
).to(DEVICE)

model.load_state_dict(checkpoint["model_state_dict"])

# Keep pretrained feature extraction frozen
for parameter in model.features.parameters():
    parameter.requires_grad = False

baseline_f1 = float(checkpoint["val_macro_f1"])
best_f1 = baseline_f1

print("\nBaseline Macro F1:", round(baseline_f1, 4))

# ==========================================
# 5. OPTIMIZER AND SCHEDULER
# ==========================================

optimizer = torch.optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=LEARNING_RATE
)

scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="max",
    factor=0.5,
    patience=1
)


# ==========================================
# 6. TRAINING FUNCTION
# ==========================================

def train_one_epoch():
    model.train()
    model.features.eval()

    total_loss = 0.0

    for batch_number, (images, labels) in enumerate(
        train_loader, start=1
    ):
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)

        if batch_number % 40 == 0:
            print(
                f"Batch {batch_number}/{len(train_loader)}",
                flush=True
            )

    return total_loss / len(train_dataset)


# ==========================================
# 7. VALIDATION FUNCTION
# ==========================================

@torch.no_grad()
def validate():
    model.eval()

    true_labels = []
    predictions = []

    for images, labels in val_loader:
        images = images.to(DEVICE)

        outputs = model(images)
        predicted = outputs.argmax(dim=1)

        true_labels.extend(labels.tolist())
        predictions.extend(predicted.cpu().tolist())

    accuracy = accuracy_score(
        true_labels, predictions
    )

    macro_f1 = f1_score(
        true_labels,
        predictions,
        labels=list(range(len(CLASS_NAMES))),
        average="macro",
        zero_division=0
    )

    return accuracy, macro_f1


# ==========================================
# 8. OPTIMIZATION LOOP
# ==========================================

history = []
epochs_without_improvement = 0
improved = False

print("\n===== OPTIMIZATION STARTED =====")

for epoch in range(1, EPOCHS + 1):
    print(f"\nEpoch {epoch}/{EPOCHS}", flush=True)

    train_loss = train_one_epoch()
    val_accuracy, val_f1 = validate()

    scheduler.step(val_f1)

    current_lr = optimizer.param_groups[0]["lr"]

    print(f"Training Loss: {train_loss:.4f}")
    print(f"Validation Accuracy: {val_accuracy:.4f}")
    print(f"Validation Macro F1: {val_f1:.4f}")
    print(f"Learning Rate: {current_lr:.6f}")

    history.append({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_accuracy": val_accuracy,
        "val_macro_f1": val_f1,
        "learning_rate": current_lr
    })

    # Save history after every epoch
    with open(HISTORY_PATH, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=history[0].keys()
        )
        writer.writeheader()
        writer.writerows(history)

    if val_f1 > best_f1 + 0.0001:
        best_f1 = val_f1
        epochs_without_improvement = 0
        improved = True

        torch.save({
            "model_state_dict": model.state_dict(),
            "class_names": CLASS_NAMES,
            "epoch": epoch,
            "val_macro_f1": best_f1,
            "image_size": 224
        }, BEST_PATH)

        print("Improved model saved!")

    else:
        epochs_without_improvement += 1
        print("No improvement over best validation score.")

    if epochs_without_improvement >= PATIENCE:
        print("\nEarly stopping triggered.")
        break


# ==========================================
# 9. FINAL SUMMARY
# ==========================================

print("\n===== OPTIMIZATION COMPLETED =====")
print(f"Baseline Macro F1: {baseline_f1:.4f}")
print(f"Best Macro F1: {best_f1:.4f}")
print(f"New checkpoint saved: {improved}")
print(f"Training history: {HISTORY_PATH}")

if not improved:
    print("Original best checkpoint was preserved.")
