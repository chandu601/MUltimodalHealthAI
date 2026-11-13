from pathlib import Path
from zipfile import ZipFile
import pandas as pd

DATA_DIR = Path("data/retinal")

print("\n===== FDR26 RETINAL DATASET AUDIT =====")

# Check files
print("\nDataset files:")
for path in sorted(DATA_DIR.iterdir()):
    print(path.name)

# Find metadata Excel file
excel_files = list(DATA_DIR.glob("*.xlsx"))

if not excel_files:
    raise FileNotFoundError(
        "No Excel metadata file found in data/retinal/"
    )

excel_path = excel_files[0]

# Read workbook sheets
workbook = pd.ExcelFile(excel_path)
print("\nExcel sheets:", workbook.sheet_names)

for sheet in workbook.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet)

    print(f"\n===== SHEET: {sheet} =====")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Column names:", df.columns.tolist())

    print("\nFirst 5 records:")
    print(df.head().to_string(index=False))

    print("\nMissing values:")
    print(df.isnull().sum().to_string())

# Inspect ZIP without extracting
zip_files = list(DATA_DIR.glob("*.zip"))

for zip_path in zip_files:
    with ZipFile(zip_path) as archive:
        image_files = [
            name for name in archive.namelist()
            if name.lower().endswith(
                (".png", ".jpg", ".jpeg", ".tif", ".tiff")
            )
        ]

    print(f"\nArchive: {zip_path.name}")
    print("Image files:", len(image_files))
    print("First 10 paths:", image_files[:10])

print("\n===== AUDIT COMPLETED =====")
