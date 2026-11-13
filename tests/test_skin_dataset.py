from src.datasets.skin_dataset import SkinDataset
from src.preprocessing.skin_transforms import eval_transforms


dataset = SkinDataset(
    csv_path="data/splits/skin/train.csv",
    image_dir="data/skin/images",
    transform=eval_transforms
)

print("Total training images:", len(dataset))

image, label = dataset[0]

print("Image tensor shape:", image.shape)
print("Label:", label.item())

assert image.shape == (3, 224, 224)
assert 0 <= label.item() < 6

print("Dataset preprocessing test passed!")
