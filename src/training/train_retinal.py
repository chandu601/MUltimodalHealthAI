from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    cohen_kappa_score
)

from src.datasets.retinal_dataset import RetinalDataset
from src.preprocessing.retinal_transforms import (
    train_transforms,
    eval_transforms
)
from src.models.retinal_model import build_retinal_model


# ======================================
# 1. CONFIGURATION
# ======================================

SEED = 42
BATCH_SIZE = 8
EPOCHS = 2
LEARNING_RATE = 0.001
NUM_CLASSES = 5

DEVICE = torch.device("cpu")
torch.set_num_threads(2)

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

CHECKPOINT_DIR = Path("checkpoints")
RESULTS_DIR = Path("notebooks/retinal_outputs")

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

CHECKPOINT_PATH = (
    CHECKPOINT_DIR / "retinal_efficientnet_best.pth"
)

HISTORY_PATH = (
    RESULTS_DIR / "retinal_training_history.csv"
)

TRAIN_CSV = "data/splits/retinal/train.csv"
VAL_CSV = "data/splits/retinal/val.csv"
IMAGE_DIR = "data/retinal/images"


# ======================================
# 2. LOAD DATASETS
# ======================================

train_dataset = RetinalDataset(
    TRAIN_CSV,
    IMAGE_DIR,
    train_transforms
)

val_dataset = RetinalDataset(
    VAL_CSV,
    IMAGE_DIR,
    eval_transforms
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


# ======================================
# 3. CLASS WEIGHTS
# ======================================

train_df = pd.read_csv(TRAIN_CSV)

counts = np.array([
    (train_df["classe"] == i).sum()
    for i in range(NUM_CLASSES)
])

if np.any(counts == 0):
    raise ValueError("A DR class has no training examples")

weights = len(train_df) / (NUM_CLASSES * counts)

class_weights = torch.tensor(
    weights,
    dtype=torch.float32,
    device=DEVICE
)

print("Class counts:", counts)
print("Class weights:", weights.round(3))


# ======================================
# 4. BUILD MODEL
# ======================================

model = build_retinal_model(
    num_classes=NUM_CLASSES,
    pretrained=True
).to(DEVICE)

criterion = nn.CrossEntropyLoss(
    weight=class_weights
)

optimizer = torch.optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=LEARNING_RATE
)

print("\nRetinal EfficientNet-B0 initialized")
print(
    "Trainable parameters:",
    sum(p.numel() for p in model.parameters()
        if p.requires_grad)
)


# ======================================
# 5. TRAIN ONE EPOCH
# ======================================

def train_one_epoch():
    model.train()

    # Preserve frozen backbone BatchNorm statistics
    model.features.eval()

    total_loss = 0.0

    for batch_idx, (images, labels) in enumerate(
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

        if batch_idx % 50 == 0:
            print(
                f"Processed batch {batch_idx}/{len(train_loader)}",
                flush=True
            )

    return total_loss / len(train_dataset)


# ======================================
# 6. VALIDATION
# ======================================

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

    accuracy = accuracy_score(true_labels, predictions)

    balanced_acc = balanced_accuracy_score(
        true_labels, predictions
    )

    macro_f1 = f1_score(
        true_labels,
        predictions,
        labels=list(range(NUM_CLASSES)),
        average="macro",
        zero_division=0
    )

    quadratic_kappa = cohen_kappa_score(
        true_labels,
        predictions,
        labels=list(range(NUM_CLASSES)),
        weights="quadratic"
    )

    return accuracy, balanced_acc, macro_f1, quadratic_kappa


# ======================================
# 7. TRAINING LOOP
# ======================================

best_f1 = -1.0
history = []

print("\n===== RETINAL TRAINING STARTED =====")

for epoch in range(1, EPOCHS + 1):

    print(f"\nEpoch {epoch}/{EPOCHS}", flush=True)

    train_loss = train_one_epoch()

    accuracy, balanced_acc, macro_f1, qwk = validate()

    print(f"Training loss: {train_loss:.4f}")
    print(f"Validation accuracy: {accuracy:.4f}")
    print(f"Balanced accuracy: {balanced_acc:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Quadratic weighted kappa: {qwk:.4f}")

    history.append({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_accuracy": accuracy,
        "val_balanced_accuracy": balanced_acc,
        "val_macro_f1": macro_f1,
        "val_quadratic_kappa": qwk
    })

    pd.DataFrame(history).to_csv(
        HISTORY_PATH,
        index=False
    )

    if macro_f1 > best_f1:
        best_f1 = macro_f1

        torch.save({
            "model_state_dict": model.state_dict(),
            "num_classes": NUM_CLASSES,
            "class_names": [
                "DR0", "DR1", "DR2", "DR3", "DR4"
            ],
            "epoch": epoch,
            "val_accuracy": accuracy,
            "val_macro_f1": macro_f1,
            "val_quadratic_kappa": qwk,
            "image_size": 224
        }, CHECKPOINT_PATH)

        print("Best retinal model saved!")


print("\n===== TRAINING COMPLETED =====")
print(f"Best validation macro F1: {best_f1:.4f}")
print("Checkpoint:", CHECKPOINT_PATH)
print("History:", HISTORY_PATH)
