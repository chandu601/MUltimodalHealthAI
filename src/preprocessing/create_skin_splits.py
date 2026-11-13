from pathlib import Path
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

DATA_PATH = Path("data/skin/metadata.csv")
OUTPUT_DIR = Path("data/splits/skin")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Split 70% train and 30% temporary data
split1 = GroupShuffleSplit(
    n_splits=1, train_size=0.70, random_state=42
)

train_idx, temp_idx = next(
    split1.split(df, groups=df["patient_id"])
)

train_df = df.iloc[train_idx].copy()
temp_df = df.iloc[temp_idx].copy()

# Split remaining patients into validation and test
split2 = GroupShuffleSplit(
    n_splits=1, train_size=0.50, random_state=42
)

val_idx, test_idx = next(
    split2.split(temp_df, groups=temp_df["patient_id"])
)

val_df = temp_df.iloc[val_idx].copy()
test_df = temp_df.iloc[test_idx].copy()

# Ensure patients do not overlap
assert set(train_df.patient_id).isdisjoint(val_df.patient_id)
assert set(train_df.patient_id).isdisjoint(test_df.patient_id)
assert set(val_df.patient_id).isdisjoint(test_df.patient_id)

train_df.to_csv(OUTPUT_DIR / "train.csv", index=False)
val_df.to_csv(OUTPUT_DIR / "val.csv", index=False)
test_df.to_csv(OUTPUT_DIR / "test.csv", index=False)

print("\n===== SKIN DATASET SPLITS =====")

for name, split in [
    ("Train", train_df),
    ("Validation", val_df),
    ("Test", test_df)
]:
    print(f"\n{name}: {len(split)} images")
    print(f"Patients: {split.patient_id.nunique()}")
    print(split.diagnostic.value_counts())

print("\nPatient overlap: None")
print("Splits saved successfully!")
