from pathlib import Path
from zipfile import ZipFile
import pandas as pd

root = Path("data/retinal")

df = pd.read_excel(
    root / "metadata_classification_DR.xlsx"
)

metadata_ids = set(df["image_id"].astype(str))

with ZipFile(root / "Fundus_FDR26.zip") as archive:
    zip_ids = {
        Path(name).stem
        for name in archive.namelist()
        if name.lower().endswith((".jpg", ".jpeg", ".png"))
    }

missing = sorted(metadata_ids - zip_ids)
extra = sorted(zip_ids - metadata_ids)

print("Metadata IDs without images:", missing)
print("ZIP image IDs without metadata:", extra)
