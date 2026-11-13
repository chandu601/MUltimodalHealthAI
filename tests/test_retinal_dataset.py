import torch
from torch.utils.data import DataLoader

from src.datasets.retinal_dataset import RetinalDataset
from src.preprocessing.retinal_transforms import (
    eval_transforms
)


dataset = RetinalDataset(
    csv_path="data/splits/retinal/train.csv",
    image_dir="data/retinal/images",
    transform=eval_transforms
)

print("Total training images:", len(dataset))

image, label = dataset[0]

print("Image shape:", image.shape)
print("DR grade:", label.item())

assert len(dataset) == 2094
assert image.shape == (3, 224, 224)
assert 0 <= label.item() <= 4
assert torch.isfinite(image).all()

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

images, labels = next(iter(loader))

print("Batch image shape:", images.shape)
print("Batch labels shape:", labels.shape)

assert images.shape == (8, 3, 224, 224)
assert labels.shape == (8,)

print("\nRetinal dataset test passed!")
