from pathlib import Path
from collections import Counter
from zipfile import ZipFile

import pandas as pd

DATA_DIR = Path("data/retinal")

excel_path = DATA_DIR / "metadata_classification_DR.xlsx"
zip_path = DATA_DIR / "Fundus_FDR26.zip"

df = pd.read_excel(excel_path)

print("\n===== RETINAL ID ANALYSIS =====")

print("Total records:", len(df))
print("Unique image IDs:", df["image_id"].nunique())

print("\nClass distribution:")
print(df["classe"].value_counts().sort_index())

print("\nDiabetes type distribution:")
print(df["type_diabete"].value_counts())

print("\nSex distribution:")
print(df["sexe"].value_counts())

print("\nAge statistics:")
print(df["age"].describe())

# Investigate possible paired-eye naming convention
ids = df["image_id"].astype(str)

print("\nLast two characters of image IDs:")
print(ids.str[-2:].value_counts().head(15))

# Candidate grouping only — must verify convention
df["candidate_patient_group"] = ids.str[:-2]

group_sizes = df.groupby(
    "candidate_patient_group"
).size()

print("\nCandidate group size distribution:")
print(group_sizes.value_counts().sort_index())

print("\nExample grouped records:")
examples = df[
    df["candidate_patient_group"].isin(
        group_sizes[group_sizes > 1].index[:5]
    )
]

print(
    examples[
        ["image_id", "candidate_patient_group",
         "classe", "age", "sexe", "type_diabete"]
    ].to_string(index=False)
)

# Verify image-to-metadata filename matching
with ZipFile(zip_path) as archive:
    filenames = {
        Path(name).stem
        for name in archive.namelist()
        if name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    }

metadata_ids = set(ids)

missing = metadata_ids - filenames
extra = filenames - metadata_ids

print("\nImages referenced but missing:", len(missing))
print("Images without metadata:", len(extra))

print("First missing IDs:", list(sorted(missing))[:10])
print("First extra IDs:", list(sorted(extra))[:10])

print("\n===== ANALYSIS COMPLETED =====")
