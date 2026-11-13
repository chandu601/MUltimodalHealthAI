from pathlib import Path
from zipfile import ZipFile
import shutil
import pandas as pd

DATA_DIR = Path("data/retinal")
ZIP_PATH = DATA_DIR / "Fundus_FDR26.zip"
CSV_PATH = DATA_DIR / "retinal_metadata_clean.csv"
IMAGE_DIR = DATA_DIR / "images"

IMAGE_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH)
required_ids = set(df["image_id"].astype(str))

print("===== RETINAL IMAGE EXTRACTION =====")
print("Required images:", len(required_ids))

extracted = set()

with ZipFile(ZIP_PATH) as archive:

    for member in archive.infolist():

        if member.is_dir():
            continue

        name = Path(member.filename).name
        suffix = Path(name).suffix.lower()

        if suffix not in {".jpg", ".jpeg", ".png"}:
            continue

        image_id = Path(name).stem

        if image_id not in required_ids:
            continue

        if image_id in extracted:
            raise ValueError(
                f"Duplicate image ID in ZIP: {image_id}"
            )

        destination = IMAGE_DIR / name

        # Stream extraction without loading
        # the entire image archive into memory.
        with archive.open(member) as source:
            with open(destination, "wb") as target:
                shutil.copyfileobj(source, target)

        extracted.add(image_id)

        if len(extracted) % 500 == 0:
            print(
                f"Extracted {len(extracted)}/{len(required_ids)}",
                flush=True
            )

missing = required_ids - extracted

print("\nExtracted images:", len(extracted))
print("Missing images:", len(missing))

if missing:
    raise RuntimeError(
        f"Missing images: {sorted(missing)[:10]}"
    )

print("Image extraction completed successfully!")
