from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = Path("data/skin/metadata.csv")
OUTPUT_DIR = Path("notebooks/eda_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

print("===== SKIN DATASET EDA =====")
print("Total records:", len(df))
print("Unique patients:", df["patient_id"].nunique())
print("Unique lesions:", df["lesion_id"].nunique())

# 1. Class distribution
class_counts = df["diagnostic"].value_counts()

plt.figure(figsize=(9, 5))
class_counts.plot(kind="bar")
plt.title("Skin Lesion Class Distribution")
plt.xlabel("Diagnostic Class")
plt.ylabel("Number of Images")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "class_distribution.png")
plt.close()

# 2. Missing values
missing = df.isnull().sum().sort_values(ascending=False)
missing = missing[missing > 0]

plt.figure(figsize=(11, 6))
missing.plot(kind="bar")
plt.title("Missing Clinical Values")
plt.ylabel("Missing Records")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "missing_values.png")
plt.close()

# 3. Age distribution
plt.figure(figsize=(8, 5))
df["age"].dropna().hist(bins=20)
plt.title("Patient Age Distribution")
plt.xlabel("Age")
plt.ylabel("Number of Images")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "age_distribution.png")
plt.close()

print("\nMissing-value percentages:")
print((df.isnull().mean() * 100).round(2))

print("\nClass distribution:")
print(class_counts)

print("\nEDA plots saved to:", OUTPUT_DIR)
