from pathlib import Path
from zipfile import ZipFile
import pandas as pd

root = Path("data/retinal")

df = pd.read_excel(
    root / "metadata_classification_DR.xlsx"
)

df["image_id"] = df["image_id"].astype(str)
df["candidate_patient_id"] = df["image_id"].str[:-2]

print("===== PATIENT GROUP VERIFICATION =====")

print("Images:", len(df))
print("Candidate patients:",
      df["candidate_patient_id"].nunique())

# Clinical data consistency within candidate patients
for col in ["sexe", "age", "type_diabete"]:
    counts = df.groupby("candidate_patient_id")[col].nunique()

    inconsistent = counts[counts > 1]

    print(f"\n{col} inconsistent groups:",
          len(inconsistent))

    if len(inconsistent):
        print(
            df[df["candidate_patient_id"].isin(
                inconsistent.index
            )][
                ["image_id", "candidate_patient_id",
                 col]
            ].head(10).to_string(index=False)
        )

# Verify every metadata image exists in ZIP
with ZipFile(root / "Fundus_FDR26.zip") as archive:
    image_ids = [
        Path(name).stem
        for name in archive.namelist()
        if name.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ]

metadata_ids = set(df["image_id"])
archive_ids = set(image_ids)

print("\nZIP image entries:", len(image_ids))
print("Unique ZIP image IDs:", len(archive_ids))
print("Missing images:", len(metadata_ids - archive_ids))
print("Images without metadata:", len(archive_ids - metadata_ids))

print("\n===== VERIFICATION COMPLETED =====")
