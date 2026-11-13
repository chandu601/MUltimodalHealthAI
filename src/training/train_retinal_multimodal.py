from pathlib import Path
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
    f1_score,
    cohen_kappa_score
)

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)
from src.preprocessing.retinal_transforms import (
    train_transforms,
    eval_transforms
)
from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)


# =====================================
# 1. CONFIGURATION
# =====================================

SEED = 42
BATCH_SIZE = 8
EPOCHS = 8
PATIENCE = 3
LEARNING_RATE = 0.0003
NUM_CLASSES = 5

DEVICE = torch.device("cpu")
torch.set_num_threads(2)

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

SPLIT_DIR = Path("data/splits/retinal")
PROCESSED_DIR = Path("data/processed/retinal")
IMAGE_DIR = Path("data/retinal/images")

CHECKPOINT_DIR = Path("checkpoints")
RESULTS_DIR = Path("notebooks/retinal_outputs")

CHECKPOINT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = (
    CHECKPOINT_DIR / "retinal_multimodal_best.pth"
)

HISTORY_PATH = (
    RESULTS_DIR / "retinal_multimodal_history.csv"
)


# =====================================
# 2. VERIFY CLINICAL FEATURES
# =====================================

preprocessor = joblib.load(
    PROCESSED_DIR / "clinical_preprocessor.joblib"
)


def verify_features(split):
    csv_path = SPLIT_DIR / f"{split}.csv"
    npy_path = (
        PROCESSED_DIR / f"{split}_clinical.npy"
    )

    df = pd.read_csv(
        csv_path, dtype={"image_id": str}
    )

    features = df[
        ["age", "sexe", "type_diabete"]
    ].copy()

    features["age"] = pd.to_numeric(
        features["age"], errors="coerce"
    )

    for col in ["sexe", "type_diabete"]:
        features[col] = (
            features[col]
            .astype("string")
            .fillna("Missing")
            .astype(str)
        )

    regenerated = preprocessor.transform(features)

    if hasattr(regenerated, "toarray"):
        regenerated = regenerated.toarray()

    regenerated = np.asarray(
        regenerated, dtype=np.float32
    )

    saved = np.load(
        npy_path, allow_pickle=False
    )

    if not np.array_equal(
        regenerated.shape, saved.shape
    ):
        raise ValueError(
            f"{split}: clinical feature shape mismatch"
        )

    if not np.allclose(
        regenerated, saved, atol=1e-5
    ):
        raise ValueError(
            f"{split}: clinical feature alignment mismatch"
        )

    print(f"{split} clinical features verified")


verify_features("train")
verify_features("val")


# =====================================
# 3. LOAD DATASETS
# =====================================

def create_dataset(split, transform):
    return RetinalMultimodalDataset(
        csv_path=SPLIT_DIR / f"{split}.csv",
        image_dir=IMAGE_DIR,
        clinical_path=(
            PROCESSED_DIR / f"{split}_clinical.npy"
        ),
        image_ids_path=(
            PROCESSED_DIR / f"{split}_image_ids.csv"
        ),
        transform=transform
    )


train_dataset = create_dataset(
    "train", train_transforms
)

val_dataset = create_dataset(
    "val", eval_transforms
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

print("\n===== RETINAL MULTIMODAL DATA =====")
print("Training samples:", len(train_dataset))
print("Validation samples:", len(val_dataset))
print("Clinical features:", clinical_dim)


# =====================================
# 4. CLASS-WEIGHTED LOSS
# =====================================

train_df = pd.read_csv(
    SPLIT_DIR / "train.csv"
)

counts = np.array([
    (train_df["classe"] == grade).sum()
    for grade in range(NUM_CLASSES)
])

if np.any(counts == 0):
    raise ValueError("Missing DR grade in training set")

weights = len(train_df) / (
    NUM_CLASSES * counts
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


# =====================================
# 5. BUILD MODEL
# =====================================

model = RetinalMultimodalModel(
    clinical_dim=clinical_dim,
    num_classes=NUM_CLASSES,
    image_checkpoint=(
        "checkpoints/retinal_efficientnet_best.pth"
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

print("\nRetinal multimodal model initialized")


# =====================================
# 6. TRAINING
# =====================================

def train_one_epoch():
    model.train()

    total_loss = 0.0

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

        total_loss += loss.item() * images.size(0)

        if batch_idx % 50 == 0:
            print(
                f"Processed batch {batch_idx}/"
                f"{len(train_loader)}",
                flush=True
            )

    return total_loss / len(train_dataset)


# =====================================
# 7. VALIDATION
# =====================================

@torch.no_grad()
def validate():
    model.eval()

    true_labels = []
    predicted_labels = []

    for images, clinical, labels in val_loader:
        images = images.to(DEVICE)
        clinical = clinical.to(DEVICE)

        outputs = model(images, clinical)
        predictions = outputs.argmax(dim=1)

        true_labels.extend(labels.tolist())
        predicted_labels.extend(
            predictions.cpu().tolist()
        )

    accuracy = accuracy_score(
        true_labels, predicted_labels
    )

    balanced_accuracy = balanced_accuracy_score(
        true_labels, predicted_labels
    )

    macro_f1 = f1_score(
        true_labels,
        predicted_labels,
        labels=list(range(NUM_CLASSES)),
        average="macro",
        zero_division=0
    )

    qwk = cohen_kappa_score(
        true_labels,
        predicted_labels,
        labels=list(range(NUM_CLASSES)),
        weights="quadratic"
    )

    return accuracy, balanced_accuracy, macro_f1, qwk


# =====================================
# 8. MAIN TRAINING LOOP
# =====================================

best_f1 = -1.0
epochs_without_improvement = 0
history = []

print("\n===== RETINAL MULTIMODAL TRAINING =====")

for epoch in range(1, EPOCHS + 1):
    print(f"\nEpoch {epoch}/{EPOCHS}", flush=True)

    train_loss = train_one_epoch()

    accuracy, balanced_acc, macro_f1, qwk = validate()

    scheduler.step(macro_f1)

    learning_rate = optimizer.param_groups[0]["lr"]

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
        "val_quadratic_kappa": qwk,
        "learning_rate": learning_rate
    })

    pd.DataFrame(history).to_csv(
        HISTORY_PATH, index=False
    )

    if macro_f1 > best_f1 + 0.0001:
        best_f1 = macro_f1
        epochs_without_improvement = 0

        torch.save({
            "model_state_dict": model.state_dict(),
            "class_names": [
                "DR0", "DR1", "DR2", "DR3", "DR4"
            ],
            "clinical_dim": clinical_dim,
            "epoch": epoch,
            "val_macro_f1": macro_f1,
            "val_accuracy": accuracy,
            "val_balanced_accuracy": balanced_acc,
            "val_quadratic_kappa": qwk,
            "image_size": 224
        }, MODEL_PATH)

        print("Best retinal multimodal model saved!")

    else:
        epochs_without_improvement += 1

    if epochs_without_improvement >= PATIENCE:
        print("\nEarly stopping triggered")
        break


print("\n===== TRAINING COMPLETED =====")
print(f"Best validation macro F1: {best_f1:.4f}")
print("Checkpoint:", MODEL_PATH)
print("History:", HISTORY_PATH)
