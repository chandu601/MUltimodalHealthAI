from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, f1_score

from src.datasets.skin_dataset import (
    SkinDataset,
    CLASS_NAMES,
    CLASS_TO_IDX
)

from src.preprocessing.skin_transforms import (
    train_transforms,
    eval_transforms
)

from src.models.skin_model import build_skin_model


# ==========================================
# 1. TRAINING CONFIGURATION
# ==========================================

SEED = 42
BATCH_SIZE = 8
EPOCHS = 2
LEARNING_RATE = 0.001

DEVICE = torch.device("cpu")

torch.set_num_threads(2)
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

CHECKPOINT_DIR = Path("checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. LOAD TRAINING AND VALIDATION DATA
# ==========================================

train_csv = "data/splits/skin/train.csv"
val_csv = "data/splits/skin/val.csv"
image_dir = "data/skin/images"

train_dataset = SkinDataset(
    csv_path=train_csv,
    image_dir=image_dir,
    transform=train_transforms
)

val_dataset = SkinDataset(
    csv_path=val_csv,
    image_dir=image_dir,
    transform=eval_transforms
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
# 3. HANDLE CLASS IMBALANCE
# ==========================================

train_df = pd.read_csv(train_csv)

counts = np.array([
    (train_df["diagnostic"] == name).sum()
    for name in CLASS_NAMES
])

if np.any(counts == 0):
    raise ValueError("One or more training classes have zero images")

weights = len(train_df) / (
    len(CLASS_NAMES) * counts
)

class_weights = torch.tensor(
    weights,
    dtype=torch.float32
).to(DEVICE)

print("\nClass names:", CLASS_NAMES)
print("Training class counts:", counts)
print("Class weights:", weights.round(3))


# ==========================================
# 4. BUILD EFFICIENTNET-B0 MODEL
# ==========================================

print("\nLoading pretrained EfficientNet-B0...")

model = build_skin_model(
    num_classes=len(CLASS_NAMES),
    pretrained=True
).to(DEVICE)

criterion = nn.CrossEntropyLoss(
    weight=class_weights
)

optimizer = torch.optim.Adam(
    filter(
        lambda parameter: parameter.requires_grad,
        model.parameters()
    ),
    lr=LEARNING_RATE
)

print("Model loaded successfully!")

print(
    "Trainable parameters:",
    sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )
)


# ==========================================
# 5. TRAINING FUNCTION
# ==========================================

def train_one_epoch():

    model.train()

    # Keep the frozen feature extractor in eval mode.
    # This avoids updating its BatchNorm statistics.
    model.features.eval()

    running_loss = 0.0

    for batch_idx, (images, labels) in enumerate(
        train_loader,
        start=1
    ):

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()
        optimizer.step()

        running_loss += (
            loss.item() * images.size(0)
        )

        if batch_idx % 40 == 0:
            print(
                f"Processed batch "
                f"{batch_idx}/{len(train_loader)}",
                flush=True
            )

    epoch_loss = running_loss / len(train_dataset)

    return epoch_loss


# ==========================================
# 6. VALIDATION FUNCTION
# ==========================================

@torch.no_grad()
def validate():

    model.eval()

    all_labels = []
    all_predictions = []

    for images, labels in val_loader:

        images = images.to(DEVICE)

        outputs = model(images)

        predictions = outputs.argmax(dim=1)

        all_labels.extend(
            labels.numpy().tolist()
        )

        all_predictions.extend(
            predictions.cpu().numpy().tolist()
        )

    accuracy = accuracy_score(
        all_labels,
        all_predictions
    )

    macro_f1 = f1_score(
        all_labels,
        all_predictions,
        labels=list(range(len(CLASS_NAMES))),
        average="macro",
        zero_division=0
    )

    return accuracy, macro_f1


# ==========================================
# 7. TRAIN MODEL AND SAVE BEST CHECKPOINT
# ==========================================

best_f1 = -1.0

print("\n===== SKIN MODEL TRAINING STARTED =====")

for epoch in range(EPOCHS):

    print(
        f"\nEpoch {epoch + 1}/{EPOCHS}",
        flush=True
    )

    train_loss = train_one_epoch()

    val_accuracy, val_f1 = validate()

    print(f"Training Loss: {train_loss:.4f}")
    print(f"Validation Accuracy: {val_accuracy:.4f}")
    print(f"Validation Macro F1: {val_f1:.4f}")

    if val_f1 > best_f1:

        best_f1 = val_f1

        checkpoint_path = (
            CHECKPOINT_DIR /
            "skin_efficientnet_best.pth"
        )

        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "class_names": CLASS_NAMES,
                "class_to_idx": CLASS_TO_IDX,
                "epoch": epoch + 1,
                "val_macro_f1": best_f1,
                "image_size": 224
            },
            checkpoint_path
        )

        print(
            f"Best model saved: {checkpoint_path}",
            flush=True
        )


# ==========================================
# 8. FINAL TRAINING SUMMARY
# ==========================================

print("\n===== TRAINING COMPLETED =====")

print(
    f"Best Validation Macro F1: {best_f1:.4f}"
)

print(
    "Saved model:",
    CHECKPOINT_DIR / "skin_efficientnet_best.pth"
)
