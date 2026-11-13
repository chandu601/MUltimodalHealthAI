import torch
from torch.utils.data import DataLoader

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)
from src.preprocessing.retinal_transforms import (
    eval_transforms
)


dataset = RetinalMultimodalDataset(
    csv_path="data/splits/retinal/train.csv",
    image_dir="data/retinal/images",
    clinical_path=(
        "data/processed/retinal/train_clinical.npy"
    ),
    image_ids_path=(
        "data/processed/retinal/train_image_ids.csv"
    ),
    transform=eval_transforms
)

print("\n===== RETINAL MULTIMODAL DATASET TEST =====")

print("Total samples:", len(dataset))

image, clinical, label = dataset[0]

print("Image shape:", image.shape)
print("Clinical shape:", clinical.shape)
print("DR grade:", label.item())

assert len(dataset) == 2094
assert image.shape == (3, 224, 224)
assert clinical.shape == (5,)
assert torch.isfinite(image).all()
assert torch.isfinite(clinical).all()
assert 0 <= label.item() <= 4

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

images, clinical_features, labels = next(
    iter(loader)
)

print("\nBatch image shape:", images.shape)
print("Batch clinical shape:", clinical_features.shape)
print("Batch labels shape:", labels.shape)

assert images.shape == (8, 3, 224, 224)
assert clinical_features.shape == (8, 5)
assert labels.shape == (8,)

print("\nRetinal multimodal dataset test passed!")
