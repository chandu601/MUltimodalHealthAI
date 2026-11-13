from pathlib import Path

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


CLASS_NAMES = ["ACK", "BCC", "MEL", "NEV", "SCC", "SEK"]

CLASS_TO_IDX = {
    name: idx for idx, name in enumerate(CLASS_NAMES)
}


class SkinDataset(Dataset):

    def __init__(self, csv_path, image_dir, transform=None):
        self.df = pd.read_csv(csv_path)
        self.image_dir = Path(image_dir)
        self.transform = transform

        # Search recursively to support extracted subfolders
        image_paths = [
            p for p in self.image_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in {".png", ".jpg", ".jpeg"}
        ]

        self.image_map = {p.name: p for p in image_paths}

        missing = [
            name for name in self.df["img_id"]
            if name not in self.image_map
        ]

        if missing:
            raise FileNotFoundError(
                f"{len(missing)} images missing. Examples: {missing[:5]}"
            )

        unknown = set(self.df["diagnostic"]) - set(CLASS_TO_IDX)
        if unknown:
            raise ValueError(f"Unknown diagnostic classes: {unknown}")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        image_path = self.image_map[row["img_id"]]

        with Image.open(image_path) as img:
            image = img.convert("RGB")

        if self.transform:
            image = self.transform(image)

        label = CLASS_TO_IDX[row["diagnostic"]]

        return image, torch.tensor(label, dtype=torch.long)
