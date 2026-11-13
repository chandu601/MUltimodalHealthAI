from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset

from src.datasets.skin_dataset import CLASS_TO_IDX


class SkinMultimodalDataset(Dataset):

    def __init__(
        self,
        csv_path,
        image_dir,
        clinical_path,
        transform=None
    ):
        self.df = pd.read_csv(csv_path).reset_index(drop=True)
        self.transform = transform

        # Load clinical features
        self.clinical = np.load(
            clinical_path,
            allow_pickle=False
        )

        if self.clinical.ndim != 2:
            raise ValueError("Clinical features must be 2D")

        if len(self.df) != len(self.clinical):
            raise ValueError(
                "CSV and clinical features have different row counts"
            )

        if not np.isfinite(self.clinical).all():
            raise ValueError("Clinical features contain NaN or Inf")

        self.clinical = torch.tensor(
            self.clinical,
            dtype=torch.float32
        )

        # Locate extracted skin images recursively
        image_dir = Path(image_dir)

        self.image_map = {}

        for path in image_dir.rglob("*"):
            if (
                path.is_file()
                and path.suffix.lower() in {".png", ".jpg", ".jpeg"}
            ):
                if path.name in self.image_map:
                    raise ValueError(
                        f"Duplicate image filename: {path.name}"
                    )

                self.image_map[path.name] = path

        missing = [
            name for name in self.df["img_id"]
            if name not in self.image_map
        ]

        if missing:
            raise FileNotFoundError(
                f"Missing {len(missing)} images: {missing[:5]}"
            )

        unknown = set(self.df["diagnostic"]) - set(CLASS_TO_IDX)

        if unknown:
            raise ValueError(f"Unknown diagnostic labels: {unknown}")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):

        row = self.df.iloc[index]

        image_path = self.image_map[row["img_id"]]

        with Image.open(image_path) as img:
            image = img.convert("RGB")

        if self.transform:
            image = self.transform(image)

        clinical_features = self.clinical[index]

        label = torch.tensor(
            CLASS_TO_IDX[row["diagnostic"]],
            dtype=torch.long
        )

        return image, clinical_features, label
