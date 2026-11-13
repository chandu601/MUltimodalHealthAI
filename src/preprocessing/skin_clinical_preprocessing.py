from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

# ==========================================
# 1. CONFIGURATION
# ==========================================

TRAIN_CSV = "data/splits/skin/train.csv"
VAL_CSV = "data/splits/skin/val.csv"

OUTPUT_DIR = Path("data/processed/skin")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NUMERICAL_FEATURES = [
    "age",
    "diameter_1",
    "diameter_2"
]

CATEGORICAL_FEATURES = [
    "gender",
    "region",
    "itch",
    "grew",
    "hurt",
    "changed",
    "bleed",
    "elevation",
    "skin_cancer_history"
]

FEATURE_COLUMNS = (
    NUMERICAL_FEATURES + CATEGORICAL_FEATURES
)

# ==========================================
# 2. LOAD DATA
# ==========================================

train_df = pd.read_csv(TRAIN_CSV)
val_df = pd.read_csv(VAL_CSV)

for col in FEATURE_COLUMNS:
    if col not in train_df.columns:
        raise ValueError(f"Missing training column: {col}")
    if col not in val_df.columns:
        raise ValueError(f"Missing validation column: {col}")

X_train = train_df[FEATURE_COLUMNS].copy()
X_val = val_df[FEATURE_COLUMNS].copy()

# Numeric values
for col in NUMERICAL_FEATURES:
    X_train[col] = pd.to_numeric(
        X_train[col], errors="coerce"
    )
    X_val[col] = pd.to_numeric(
        X_val[col], errors="coerce"
    )

# Convert categorical values to strings and
# preserve missing values as a separate category.
for col in CATEGORICAL_FEATURES:
    X_train[col] = (
        X_train[col].fillna("Missing").astype(str)
    )
    X_val[col] = (
        X_val[col].fillna("Missing").astype(str)
    )

# ==========================================
# 3. PREPROCESSING PIPELINES
# ==========================================

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(
        strategy="median",
        add_indicator=True
    )),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("encoder", OneHotEncoder(
        handle_unknown="ignore"
    ))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, NUMERICAL_FEATURES),
    ("categorical", categorical_pipeline, CATEGORICAL_FEATURES)
])

# ==========================================
# 4. FIT ON TRAINING DATA ONLY
# ==========================================

print("Fitting clinical preprocessor...")

X_train_processed = preprocessor.fit_transform(X_train)

# Apply the same transformation to validation
X_val_processed = preprocessor.transform(X_val)

# Handle sparse output
if hasattr(X_train_processed, "toarray"):
    X_train_processed = X_train_processed.toarray()

if hasattr(X_val_processed, "toarray"):
    X_val_processed = X_val_processed.toarray()

X_train_processed = np.asarray(
    X_train_processed, dtype=np.float32
)

X_val_processed = np.asarray(
    X_val_processed, dtype=np.float32
)

# ==========================================
# 5. SAVE PROCESSED FEATURES
# ==========================================

np.save(
    OUTPUT_DIR / "train_clinical.npy",
    X_train_processed
)

np.save(
    OUTPUT_DIR / "val_clinical.npy",
    X_val_processed
)

joblib.dump(
    preprocessor,
    OUTPUT_DIR / "clinical_preprocessor.joblib"
)

# ==========================================
# 6. VERIFICATION
# ==========================================

print("\n===== CLINICAL PREPROCESSING =====")

print("Training samples:", len(train_df))
print("Validation samples:", len(val_df))

print(
    "Training feature shape:",
    X_train_processed.shape
)

print(
    "Validation feature shape:",
    X_val_processed.shape
)

assert X_train_processed.shape[1] == X_val_processed.shape[1]

assert np.isfinite(X_train_processed).all()
assert np.isfinite(X_val_processed).all()

print("\nPreprocessing completed successfully!")
print("Files saved to:", OUTPUT_DIR)
