from pathlib import Path
from zipfile import ZipFile
import pandas as pd

DATA_DIR = Path("data/retinal")

excel_path = DATA_DIR / "metadata_classification_DR.xlsx"
zip_path = DATA_DIR / "Fundus_FDR26.zip"

output_path = DATA_DIR / "retinal_metadata_clean.csv"

df = pd.read_excel(excel_path)

df["image_id"] = df["image_id"].astype(str).str.strip()

with ZipFile(zip_path) as archive:
    available_ids = {
        Path(name).stem
        for name in archive.namelist()
        if name.lower().endswith((".jpg", ".jpeg", ".png"))
    }

# Keep only metadata rows with matching image files.
clean_df = df[
    df["image_id"].isin(available_ids)
].copy()

removed_df = df[
    ~df["image_id"].isin(available_ids)
].copy()

clean_df["patient_group"] = (
    clean_df["image_id"].str[:-2]
)

clean_df.to_csv(output_path, index=False)

print("===== RETINAL CLEANING RESULTS =====")
print("Original records:", len(df))
print("Clean records:", len(clean_df))
print("Removed records:", len(removed_df))

print("\nRemoved image IDs:")
print(removed_df["image_id"].tolist())

print("\nUnique candidate patient groups:",
      clean_df["patient_group"].nunique())

print("\nClass distribution:")
print(clean_df["classe"].value_counts().sort_index())

print("\nSaved:", output_path)
