from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


CLASS_NAMES = ["skin", "retinal"]

train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])


class ImageTypeDataset(Dataset):

    def __init__(self, split="train"):
        if split not in {"train", "val"}:
            raise ValueError("Use train or val")

        self.transform = (
            train_transform if split == "train"
            else eval_transform
        )

        records = []

        sources = [
            (
                "skin",
                f"data/splits/skin/{split}.csv",
                "data/skin/images",
                "img_id",
                0
            ),
            (
                "retinal",
                f"data/splits/retinal/{split}.csv",
                "data/retinal/images",
                "image_id",
                1
            )
        ]

        for name, csv_path, image_dir, id_col, label in sources:
            df = pd.read_csv(
                csv_path, dtype={id_col: str}
            )

            image_map = {}

            for path in Path(image_dir).rglob("*"):
                if (
                    path.is_file()
                    and path.suffix.lower()
                    in {".jpg", ".jpeg", ".png"}
                ):
                    image_map.setdefault(path.stem, path)

            for image_id in df[id_col].astype(str):
                key = Path(image_id).stem

                if key not in image_map:
                    raise FileNotFoundError(
                        f"{name} image missing: {image_id}"
                    )

                records.append(
                    (image_map[key], label)
                )

        self.records = records

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        path, label = self.records[index]

        with Image.open(path) as img:
            image = img.convert("RGB")

        return (
            self.transform(image),
            torch.tensor(label, dtype=torch.long)
        )
