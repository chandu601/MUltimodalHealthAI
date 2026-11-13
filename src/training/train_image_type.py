from pathlib import Path
import random

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

from torch.utils.data import DataLoader
from torchvision.models import (
    efficientnet_b0,
    EfficientNet_B0_Weights
)
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from src.datasets.image_type_dataset import (
    ImageTypeDataset,
    CLASS_NAMES
)


# Configuration
SEED = 42
BATCH_SIZE = 8
EPOCHS = 2
DEVICE = torch.device("cpu")

torch.set_num_threads(2)
torch.manual_seed(SEED)
np.random.seed(SEED)
random.seed(SEED)

OUTPUT_DIR = Path("checkpoints")
OUTPUT_DIR.mkdir(exist_ok=True)

RESULTS_DIR = Path("notebooks/image_type_outputs")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

train_data = ImageTypeDataset("train")
val_data = ImageTypeDataset("val")

train_loader = DataLoader(
    train_data,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_data,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

print("===== IMAGE TYPE DATASET =====")
print("Training images:", len(train_data))
print("Validation images:", len(val_data))


# EfficientNet-B0 image-type model
model = efficientnet_b0(
    weights=EfficientNet_B0_Weights.DEFAULT
)

for parameter in model.features.parameters():
    parameter.requires_grad = False

in_features = model.classifier[1].in_features

model.classifier[1] = nn.Linear(in_features, 2)
model.to(DEVICE)

# Calculate class weights
labels = [label for _, label in train_data.records]
counts = np.bincount(labels, minlength=2)

weights = len(labels) / (2 * counts)

criterion = nn.CrossEntropyLoss(
    weight=torch.tensor(
        weights,
        dtype=torch.float32
    )
)

optimizer = torch.optim.Adam(
    filter(
        lambda p: p.requires_grad,
        model.parameters()
    ),
    lr=0.001
)


def train_one_epoch():
    model.train()
    model.features.eval()

    total_loss = 0.0

    for batch_index, (images, labels) in enumerate(
        train_loader, start=1
    ):
        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        logits = model(images)
        loss = criterion(logits, labels)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(images)

        if batch_index % 100 == 0:
            print(
                f"Processed {batch_index}/"
                f"{len(train_loader)} batches",
                flush=True
            )

    return total_loss / len(train_data)


@torch.no_grad()
def evaluate():
    model.eval()

    true_labels = []
    predictions = []
    confidences = []

    for images, labels in val_loader:
        logits = model(images.to(DEVICE))
        probabilities = torch.softmax(logits, dim=1)

        confidence, predicted = probabilities.max(dim=1)

        true_labels.extend(labels.tolist())
        predictions.extend(predicted.cpu().tolist())
        confidences.extend(confidence.cpu().tolist())

    accuracy = accuracy_score(true_labels, predictions)

    balanced = balanced_accuracy_score(
        true_labels, predictions
    )

    macro_f1 = f1_score(
        true_labels,
        predictions,
        average="macro",
        zero_division=0
    )

    print("\nValidation accuracy:", round(accuracy, 4))
    print("Balanced accuracy:", round(balanced, 4))
    print("Macro F1:", round(macro_f1, 4))

    print("\nClassification Report:")
    print(classification_report(
        true_labels,
        predictions,
        target_names=CLASS_NAMES,
        zero_division=0
    ))

    print("Confusion matrix:")
    print(confusion_matrix(
        true_labels, predictions
    ))

    return accuracy, macro_f1


best_f1 = -1.0
history = []

print("\n===== IMAGE TYPE TRAINING STARTED =====")

for epoch in range(1, EPOCHS + 1):
    print(f"\nEpoch {epoch}/{EPOCHS}", flush=True)

    loss = train_one_epoch()
    accuracy, macro_f1 = evaluate()

    print("Training loss:", round(loss, 4))

    history.append({
        "epoch": epoch,
        "train_loss": loss,
        "val_accuracy": accuracy,
        "val_macro_f1": macro_f1
    })

    pd.DataFrame(history).to_csv(
        RESULTS_DIR / "training_history.csv",
        index=False
    )

    if macro_f1 > best_f1:
        best_f1 = macro_f1

        torch.save({
            "model_state_dict": model.state_dict(),
            "class_names": CLASS_NAMES,
            "epoch": epoch,
            "val_macro_f1": best_f1,
            "image_size": 224
        }, OUTPUT_DIR / "image_type_best.pth")

        print("Best image-type model saved!")

print("\n===== TRAINING COMPLETED =====")
print("Best validation macro F1:", round(best_f1, 4))
