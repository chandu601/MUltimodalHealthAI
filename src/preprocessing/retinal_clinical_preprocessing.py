from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# Paths
SPLIT_DIR = Path("data/splits/retinal")
OUTPUT_DIR = Path("data/processed/retinal")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NUMERICAL = ["age"]
CATEGORICAL = ["sexe", "type_diabete"]
FEATURES = NUMERICAL + CATEGORICAL

# Load splits
train_df = pd.read_csv(SPLIT_DIR / "train.csv")
val_df = pd.read_csv(SPLIT_DIR / "val.csv")

def prepare_features(df):
    X = df[FEATURES].copy()

    X["age"] = pd.to_numeric(
        X["age"], errors="coerce"
    )

    for col in CATEGORICAL:
        X[col] = X[col].astype("string").fillna("Missing")
        X[col] = X[col].astype(str)

    return X

# Preprocessing pipeline
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, NUMERICAL),
    ("categorical", categorical_pipeline, CATEGORICAL)
])

# Fit ONLY on training data
X_train = preprocessor.fit_transform(
    prepare_features(train_df)
)

X_val = preprocessor.transform(
    prepare_features(val_df)
)

def to_array(X):
    if hasattr(X, "toarray"):
        X = X.toarray()
    return np.asarray(X, dtype=np.float32)

X_train = to_array(X_train)
X_val = to_array(X_val)

assert X_train.shape[0] == len(train_df)
assert X_val.shape[0] == len(val_df)
assert X_train.shape[1] == X_val.shape[1]
assert np.isfinite(X_train).all()
assert np.isfinite(X_val).all()

# Save features and original row IDs
np.save(OUTPUT_DIR / "train_clinical.npy", X_train)
np.save(OUTPUT_DIR / "val_clinical.npy", X_val)

train_df[["image_id"]].to_csv(
    OUTPUT_DIR / "train_image_ids.csv", index=False
)
val_df[["image_id"]].to_csv(
    OUTPUT_DIR / "val_image_ids.csv", index=False
)

joblib.dump(
    preprocessor,
    OUTPUT_DIR / "clinical_preprocessor.joblib"
)

print("\n===== RETINAL CLINICAL PREPROCESSING =====")
print("Training samples:", len(train_df))
print("Validation samples:", len(val_df))
print("Training shape:", X_train.shape)
print("Validation shape:", X_val.shape)
print("Encoded features:", preprocessor.get_feature_names_out().tolist())
print("Preprocessing completed successfully!")
