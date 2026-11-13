from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

DATA_PATH = Path("data/retinal/retinal_metadata_clean.csv")
OUTPUT_DIR = Path("data/splits/retinal")
IMAGE_DIR = Path("data/retinal/images")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

required = [
    "image_id", "patient_group", "classe",
    "age", "sexe", "type_diabete"
]

if df[required].isnull().any().any():
    raise ValueError("Required fields contain missing values")

if df["image_id"].duplicated().any():
    raise ValueError("Duplicate image IDs detected")

df["classe"] = df["classe"].astype(int)

assert set(df["classe"]) == {0, 1, 2, 3, 4}

# Check extracted image availability
available = {
    p.stem for p in IMAGE_DIR.iterdir()
    if p.is_file()
    and p.suffix.lower() in {".jpg", ".jpeg", ".png"}
}

missing = set(df["image_id"].astype(str)) - available

if missing:
    raise FileNotFoundError(
        f"{len(missing)} retinal images missing"
    )

# First split: approximately 70% of patients for training
splitter1 = GroupShuffleSplit(
    n_splits=1,
    train_size=0.70,
    random_state=42
)

train_idx, temp_idx = next(
    splitter1.split(
        df,
        groups=df["patient_group"]
    )
)

train_df = df.iloc[train_idx].copy()
temp_df = df.iloc[temp_idx].copy()

# Second split: remaining groups into val and test
splitter2 = GroupShuffleSplit(
    n_splits=1,
    train_size=0.50,
    random_state=42
)

val_idx, test_idx = next(
    splitter2.split(
        temp_df,
        groups=temp_df["patient_group"]
    )
)

val_df = temp_df.iloc[val_idx].copy()
test_df = temp_df.iloc[test_idx].copy()

# Check group isolation
train_groups = set(train_df["patient_group"])
val_groups = set(val_df["patient_group"])
test_groups = set(test_df["patient_group"])

assert train_groups.isdisjoint(val_groups)
assert train_groups.isdisjoint(test_groups)
assert val_groups.isdisjoint(test_groups)

# Verify no records were lost
assert (
    len(train_df) + len(val_df) + len(test_df)
    == len(df)
)

# Verify all five grades are represented
for name, subset in [
    ("Train", train_df),
    ("Validation", val_df),
    ("Test", test_df)
]:
    if set(subset["classe"]) != {0, 1, 2, 3, 4}:
        raise ValueError(
            f"{name} split is missing a DR class"
        )

# Save splits
train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
val_df.to_csv(OUTPUT_DIR / "val.csv", index=False)
test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

print("\n===== RETINAL DATASET SPLITS =====")

for name, subset in [
    ("Train", train_df),
    ("Validation", val_df),
    ("Test", test_df)
]:
    print(f"\n{name}:")
    print("Images:", len(subset))
    print("Patient groups:", subset["patient_group"].nunique())

    print("Class distribution:")
    print(
        subset["classe"].value_counts().sort_index()
    )

print("\nPatient group overlap: None")
print("All five DR classes represented")
print("Retinal splitting completed successfully!")
