from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


CLASS_NAMES = [
    "DR0", "DR1", "DR2", "DR3", "DR4"
]


class RetinalDataset(Dataset):

    def __init__(
        self,
        csv_path,
        image_dir,
        transform=None
    ):
        self.df = pd.read_csv(csv_path)
        self.image_dir = Path(image_dir)
        self.transform = transform

        self.image_map = {}

        for path in self.image_dir.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower()
                in {".jpg", ".jpeg", ".png"}
            ):
                if path.stem in self.image_map:
                    raise ValueError(
                        f"Duplicate image ID: {path.stem}"
                    )

                self.image_map[path.stem] = path

        missing = [
            str(image_id)
            for image_id in self.df["image_id"]
            if str(image_id) not in self.image_map
        ]

        if missing:
            raise FileNotFoundError(
                f"{len(missing)} images missing: {missing[:5]}"
            )

        labels = set(self.df["classe"].astype(int))

        if not labels.issubset({0, 1, 2, 3, 4}):
            raise ValueError(
                f"Unexpected DR grades: {labels}"
            )

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):

        row = self.df.iloc[index]

        image_id = str(row["image_id"])
        image_path = self.image_map[image_id]

        with Image.open(image_path) as img:
            image = img.convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = torch.tensor(
            int(row["classe"]),
            dtype=torch.long
        )

        return image, label
