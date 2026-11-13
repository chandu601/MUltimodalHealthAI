from pathlib import Path
import csv
import random

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score
)

from src.datasets.skin_multimodal_dataset import (
    SkinMultimodalDataset
)
from src.datasets.skin_dataset import CLASS_NAMES
from src.preprocessing.skin_transforms import (
    train_transforms,
    eval_transforms
)
from src.models.skin_multimodal_model import (
    SkinMultimodalModel
)


# ==========================================
# 1. CONFIGURATION
# ==========================================

SEED = 42
BATCH_SIZE = 8
EPOCHS = 8
PATIENCE = 3
LEARNING_RATE = 0.0003

DEVICE = torch.device("cpu")
torch.set_num_threads(2)

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

DATA_DIR = Path("data/processed/skin")
CHECKPOINT_DIR = Path("checkpoints")
RESULTS_DIR = Path("notebooks/training_outputs")

CHECKPOINT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = (
    CHECKPOINT_DIR / "skin_multimodal_best.pth"
)

HISTORY_PATH = (
    RESULTS_DIR / "skin_multimodal_history.csv"
)

TRAIN_CSV = "data/splits/skin/train.csv"
VAL_CSV = "data/splits/skin/val.csv"
IMAGE_DIR = "data/skin/images"


# ==========================================
# 2. VERIFY IMAGE-CLINICAL ALIGNMENT
# ==========================================

# Regenerate clinical features from the saved
# preprocessor and original CSV row order.
# This checks that .npy files have not been
# accidentally reordered or modified.

preprocessor = joblib.load(
    DATA_DIR / "clinical_preprocessor.joblib"
)

numeric_cols = ["age", "diameter_1", "diameter_2"]

categorical_cols = [
    "gender", "region", "itch", "grew",
    "hurt", "changed", "bleed",
    "elevation", "skin_cancer_history"
]

feature_cols = numeric_cols + categorical_cols


def verify_clinical_features(csv_path, npy_path):

    df = pd.read_csv(csv_path)
    features = df[feature_cols].copy()

    for col in numeric_cols:
        features[col] = pd.to_numeric(
            features[col], errors="coerce"
        )

    for col in categorical_cols:
        features[col] = (
            features[col]
            .fillna("Missing")
            .astype(str)
        )

    regenerated = preprocessor.transform(features)

    if hasattr(regenerated, "toarray"):
        regenerated = regenerated.toarray()

    regenerated = np.asarray(
        regenerated, dtype=np.float32
    )

    saved = np.load(npy_path, allow_pickle=False)

    if regenerated.shape != saved.shape:
        raise ValueError(
            f"Shape mismatch for {npy_path}"
        )

    if not np.allclose(
        regenerated, saved, atol=1e-5, rtol=1e-5
    ):
        raise ValueError(
            f"Clinical data alignment mismatch: {npy_path}"
        )

    print(f"Clinical alignment verified: {npy_path}")


verify_clinical_features(
    TRAIN_CSV,
    DATA_DIR / "train_clinical.npy"
)

verify_clinical_features(
    VAL_CSV,
    DATA_DIR / "val_clinical.npy"
)


# ==========================================
# 3. LOAD MULTIMODAL DATASETS
# ==========================================

train_dataset = SkinMultimodalDataset(
    csv_path=TRAIN_CSV,
    image_dir=IMAGE_DIR,
    clinical_path=DATA_DIR / "train_clinical.npy",
    transform=train_transforms
)

val_dataset = SkinMultimodalDataset(
    csv_path=VAL_CSV,
    image_dir=IMAGE_DIR,
    clinical_path=DATA_DIR / "val_clinical.npy",
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

clinical_dim = train_dataset.clinical.shape[1]

assert clinical_dim == val_dataset.clinical.shape[1]

print("\n===== MULTIMODAL DATASET =====")
print("Training images:", len(train_dataset))
print("Validation images:", len(val_dataset))
print("Clinical features:", clinical_dim)


# ==========================================
# 4. CLASS-WEIGHTED LOSS
# ==========================================

train_df = pd.read_csv(TRAIN_CSV)

counts = np.array([
    (train_df["diagnostic"] == name).sum()
    for name in CLASS_NAMES
])

if np.any(counts == 0):
    raise ValueError("Missing class in training data")

weights = len(train_df) / (
    len(CLASS_NAMES) * counts
)

class_weights = torch.tensor(
    weights,
    dtype=torch.float32,
    device=DEVICE
)

criterion = nn.CrossEntropyLoss(
    weight=class_weights
)

print("Class counts:", counts)
print("Class weights:", weights.round(3))


# ==========================================
# 5. BUILD MULTIMODAL MODEL
# ==========================================

model = SkinMultimodalModel(
    clinical_dim=clinical_dim,
    num_classes=len(CLASS_NAMES),
    image_checkpoint=(
        "checkpoints/skin_efficientnet_baseline.pth"
    )
).to(DEVICE)

optimizer = torch.optim.Adam(
    filter(
        lambda p: p.requires_grad,
        model.parameters()
    ),
    lr=LEARNING_RATE
)

scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="max",
    factor=0.5,
    patience=1
)

print("\nMultimodal model initialized!")


# ==========================================
# 6. TRAINING FUNCTION
# ==========================================

def train_one_epoch():

    model.train()
    running_loss = 0.0

    for batch_idx, (images, clinical, labels) in enumerate(
        train_loader, start=1
    ):

        images = images.to(DEVICE)
        clinical = clinical.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images, clinical)

        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

        if batch_idx % 40 == 0:
            print(
                f"Processed batch {batch_idx}/"
                f"{len(train_loader)}",
                flush=True
            )

    return running_loss / len(train_dataset)


# ==========================================
# 7. VALIDATION FUNCTION
# ==========================================

@torch.no_grad()
def validate():

    model.eval()

    all_true = []
    all_pred = []

    for images, clinical, labels in val_loader:

        images = images.to(DEVICE)
        clinical = clinical.to(DEVICE)

        outputs = model(images, clinical)
        predictions = outputs.argmax(dim=1)

        all_true.extend(labels.tolist())
        all_pred.extend(predictions.cpu().tolist())

    accuracy = accuracy_score(all_true, all_pred)

    balanced_acc = balanced_accuracy_score(
        all_true, all_pred
    )

    macro_f1 = f1_score(
        all_true,
        all_pred,
        labels=list(range(len(CLASS_NAMES))),
        average="macro",
        zero_division=0
    )

    return accuracy, balanced_acc, macro_f1


# ==========================================
# 8. TRAINING LOOP
# ==========================================

best_f1 = -1.0
epochs_without_improvement = 0
history = []

print("\n===== MULTIMODAL TRAINING STARTED =====")

for epoch in range(1, EPOCHS + 1):

    print(f"\nEpoch {epoch}/{EPOCHS}", flush=True)

    train_loss = train_one_epoch()

    val_acc, val_bal_acc, val_f1 = validate()

    scheduler.step(val_f1)

    lr = optimizer.param_groups[0]["lr"]

    print(f"Training loss: {train_loss:.4f}")
    print(f"Validation accuracy: {val_acc:.4f}")
    print(f"Balanced accuracy: {val_bal_acc:.4f}")
    print(f"Validation macro F1: {val_f1:.4f}")
    print(f"Learning rate: {lr:.6f}")

    history.append({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_accuracy": val_acc,
        "val_balanced_accuracy": val_bal_acc,
        "val_macro_f1": val_f1,
        "learning_rate": lr
    })

    pd.DataFrame(history).to_csv(
        HISTORY_PATH, index=False
    )

    if val_f1 > best_f1 + 0.0001:

        best_f1 = val_f1
        epochs_without_improvement = 0

        torch.save({
            "model_state_dict": model.state_dict(),
            "class_names": CLASS_NAMES,
            "clinical_dim": clinical_dim,
            "epoch": epoch,
            "val_macro_f1": best_f1,
            "val_accuracy": val_acc,
            "val_balanced_accuracy": val_bal_acc,
            "image_size": 224
        }, MODEL_PATH)

        print("Best multimodal checkpoint saved!")

    else:
        epochs_without_improvement += 1

    if epochs_without_improvement >= PATIENCE:
        print("Early stopping triggered.")
        break


# ==========================================
# 9. FINAL SUMMARY
# ==========================================

print("\n===== MULTIMODAL TRAINING COMPLETED =====")
print(f"Best validation macro F1: {best_f1:.4f}")
print(f"Checkpoint saved: {MODEL_PATH}")
print(f"Training history: {HISTORY_PATH}")
