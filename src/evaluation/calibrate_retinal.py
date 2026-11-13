from pathlib import Path
import json

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)
from src.preprocessing.retinal_transforms import eval_transforms
from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)

# Configuration
torch.set_num_threads(2)
DEVICE = torch.device("cpu")

CLASS_NAMES = ["DR0", "DR1", "DR2", "DR3", "DR4"]

OUTPUT_PATH = Path(
    "checkpoints/retinal_temperature.json"
)

# Load trained model
checkpoint = torch.load(
    "checkpoints/retinal_multimodal_best.pth",
    map_location=DEVICE,
    weights_only=True
)

assert checkpoint["class_names"] == CLASS_NAMES

model = RetinalMultimodalModel(
    clinical_dim=checkpoint["clinical_dim"],
    num_classes=5,
    image_checkpoint="checkpoints/retinal_efficientnet_best.pth"
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# Validation data only
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

# Collect raw logits and labels
all_logits = []
all_labels = []

with torch.no_grad():
    for images, clinical, labels in loader:
        logits = model(
            images.to(DEVICE),
            clinical.to(DEVICE)
        )

        all_logits.append(logits.cpu())
        all_labels.append(labels.cpu())

logits = torch.cat(all_logits)
labels = torch.cat(all_labels)

# Learn positive temperature
log_temperature = torch.nn.Parameter(
    torch.tensor(0.0)
)

optimizer = torch.optim.LBFGS(
    [log_temperature],
    lr=0.1,
    max_iter=100,
    line_search_fn="strong_wolfe"
)

def closure():
    optimizer.zero_grad()
    temperature = log_temperature.exp()
    loss = F.cross_entropy(
        logits / temperature, labels
    )
    loss.backward()
    return loss

optimizer.step(closure)

temperature = float(
    log_temperature.detach().exp().item()
)

# Calculate calibration metrics
def calculate_metrics(scores):
    probabilities = F.softmax(scores, dim=1)

    confidence, predictions = probabilities.max(dim=1)
    correct = predictions.eq(labels).float()

    nll = F.cross_entropy(scores, labels).item()

    one_hot = F.one_hot(
        labels, num_classes=len(CLASS_NAMES)
    ).float()

    brier = (
        (probabilities - one_hot)
        .square()
        .sum(dim=1)
        .mean()
        .item()
    )

    ece = 0.0

    for index in range(10):
        lower = index / 10
        upper = (index + 1) / 10

        mask = (
            (confidence > lower)
            & (confidence <= upper)
        )

        if mask.any():
            bin_accuracy = correct[mask].mean().item()
            bin_confidence = confidence[mask].mean().item()
            fraction = mask.float().mean().item()

            ece += fraction * abs(
                bin_accuracy - bin_confidence
            )

    return nll, brier, ece

before = calculate_metrics(logits)
after = calculate_metrics(logits / temperature)

# Predictions should remain unchanged
assert torch.equal(
    logits.argmax(dim=1),
    (logits / temperature).argmax(dim=1)
)

# Save calibration parameter
with open(OUTPUT_PATH, "w") as file:
    json.dump({
        "temperature": temperature,
        "model": "retinal_multimodal_best.pth",
        "fitted_on": "retinal_validation_split",
        "class_names": CLASS_NAMES,
        "num_samples": len(labels)
    }, file, indent=2)

print("\n===== RETINAL CALIBRATION RESULTS =====")
print("Validation images:", len(labels))
print(f"Optimal temperature: {temperature:.4f}")

print("\nMetric          Before       After")

for name, old, new in zip(
    ["NLL", "Brier", "ECE"],
    before, after
):
    print(f"{name:8s} {old:12.4f} {new:11.4f}")

print("\nSaved:", OUTPUT_PATH)
print("Retinal calibration fitting completed!")
