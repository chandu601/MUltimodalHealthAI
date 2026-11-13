from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


class RetinalMultimodalDataset(Dataset):

    def __init__(
        self,
        csv_path,
        image_dir,
        clinical_path,
        image_ids_path,
        transform=None
    ):
        self.df = pd.read_csv(
            csv_path, dtype={"image_id": str}
        ).reset_index(drop=True)

        self.transform = transform

        # Load clinical feature matrix
        features = np.load(
            clinical_path, allow_pickle=False
        )

        if features.ndim != 2:
            raise ValueError(
                "Clinical features must be a 2D matrix"
            )

        if len(features) != len(self.df):
            raise ValueError(
                "CSV and clinical feature counts differ"
            )

        if not np.isfinite(features).all():
            raise ValueError(
                "Clinical features contain NaN or Inf"
            )

        # Verify clinical rows match image IDs
        saved_ids = pd.read_csv(
            image_ids_path,
            dtype={"image_id": str}
        )["image_id"].tolist()

        csv_ids = self.df["image_id"].tolist()

        if csv_ids != saved_ids:
            raise ValueError(
                "Clinical feature and image ID order mismatch"
            )

        self.clinical = torch.tensor(
            features, dtype=torch.float32
        )

        # Locate retinal images
        self.image_map = {}

        for path in Path(image_dir).rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in {
                ".jpg", ".jpeg", ".png"
            }:
                continue

            if path.stem in self.image_map:
                raise ValueError(
                    f"Duplicate image ID: {path.stem}"
                )

            self.image_map[path.stem] = path

        missing = [
            image_id for image_id in csv_ids
            if image_id not in self.image_map
        ]

        if missing:
            raise FileNotFoundError(
                f"{len(missing)} images missing: "
                f"{missing[:5]}"
            )

        # Validate DR labels
        self.labels = self.df["classe"].astype(int)

        if not self.labels.isin(range(5)).all():
            raise ValueError(
                "DR labels must be integers from 0 to 4"
            )

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):

        row = self.df.iloc[index]

        image_path = self.image_map[row["image_id"]]

        with Image.open(image_path) as img:
            image = img.convert("RGB")

        if self.transform:
            image = self.transform(image)

        clinical = self.clinical[index]

        label = torch.tensor(
            int(self.labels.iloc[index]),
            dtype=torch.long
        )

        return image, clinical, label
