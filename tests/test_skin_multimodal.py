import torch
from torch.utils.data import DataLoader

from src.datasets.skin_multimodal_dataset import SkinMultimodalDataset
from src.preprocessing.skin_transforms import eval_transforms

dataset = SkinMultimodalDataset(
    csv_path="data/splits/skin/train.csv",
    image_dir="data/skin/images",
    clinical_path="data/processed/skin/train_clinical.npy",
    transform=eval_transforms
)

print("Total samples:", len(dataset))

image, clinical, label = dataset[0]

print("Image shape:", image.shape)
print("Clinical shape:", clinical.shape)
print("Label:", label.item())

assert len(dataset) == 1582
assert image.shape == (3, 224, 224)
assert clinical.shape == (43,)
assert torch.isfinite(clinical).all()
assert 0 <= label.item() < 6

loader = DataLoader(
    dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

images, clinical_features, labels = next(iter(loader))

print("Batch images:", images.shape)
print("Batch clinical features:", clinical_features.shape)
print("Batch labels:", labels.shape)

assert images.shape == (8, 3, 224, 224)
assert clinical_features.shape == (8, 43)
assert labels.shape == (8,)

print("Multimodal dataset test passed!")
