 
from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

from torch.utils.data import DataLoader

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    cohen_kappa_score,
)

from src.datasets.skin_dataset import (
    CLASS_NAMES as SKIN_CLASSES
)

from src.datasets.skin_multimodal_dataset import (
    SkinMultimodalDataset
)

from src.datasets.retinal_multimodal_dataset import (
    RetinalMultimodalDataset
)

from src.models.skin_multimodal_model import (
    SkinMultimodalModel
)

from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)

from src.preprocessing.skin_transforms import (
    eval_transforms as skin_transforms
)

from src.preprocessing.retinal_transforms import (
    eval_transforms as retinal_transforms
)


# ==================================================
# 1. CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = ROOT / "results" / "final_test"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DEVICE = torch.device("cpu")

torch.set_num_threads(2)

RETINAL_CLASSES = [
    "DR0",
    "DR1",
    "DR2",
    "DR3",
    "DR4"
]


# ==================================================
# 2. NORMALIZE CLINICAL CATEGORIES
# ==================================================

def normalize_categories(
    clinical_frame,
    preprocessor,
    dataset_name
):
    """
    Convert test categorical values to the types
    expected by the encoder fitted on training data.

    Never fit a new encoder on test data.
    """

    categorical_pipeline = (
        preprocessor.named_transformers_["categorical"]
    )

    encoder = (
        categorical_pipeline.named_steps["encoder"]
    )

    categorical_columns = None

    for name, transformer, columns in (
        preprocessor.transformers_
    ):

        if name == "categorical":
            categorical_columns = list(columns)
            break

    if categorical_columns is None:
        raise RuntimeError(
            "Could not find categorical columns "
            "in the saved preprocessor."
        )

    if len(categorical_columns) != len(
        encoder.categories_
    ):
        raise RuntimeError(
            "Mismatch between categorical columns "
            "and saved encoder categories."
        )

    for column, categories in zip(
        categorical_columns,
        encoder.categories_
    ):

        saved_values = list(categories)

        # Only normalize to strings when the saved
        # encoder was trained with string categories.
        string_categories = all(
            isinstance(value, str)
            for value in saved_values
        )

        if string_categories:

            def to_training_string(value):

                if pd.isna(value):
                    return "Missing"

                if isinstance(
                    value,
                    (bool, np.bool_)
                ):
                    return (
                        "True"
                        if bool(value)
                        else "False"
                    )

                return str(value)

            clinical_frame[column] = (
                clinical_frame[column].map(
                    to_training_string
                )
            )

        # Check that all values are compatible
        # with the saved encoder.
        known_values = {
            str(value)
            for value in saved_values
        }

        observed_values = {
            str(value)
            for value in (
                clinical_frame[column]
                .dropna()
                .unique()
            )
        }

        unknown_values = (
            observed_values - known_values
        )

        if unknown_values:

            raise RuntimeError(
                f"{dataset_name}: unsupported category "
                f"in column '{column}'. "
                f"Unknown: {sorted(unknown_values)}. "
                f"Expected: {sorted(known_values)}"
            )

    return clinical_frame


# ==================================================
# 3. PREPARE TEST CLINICAL FEATURES
# ==================================================

def prepare_clinical(kind):

    print(
        f"\nPreparing {kind} test clinical data..."
    )

    csv_path = (
        ROOT
        / "data"
        / "splits"
        / kind
        / "test.csv"
    )

    preprocessor_path = (
        ROOT
        / "data"
        / "processed"
        / kind
        / "clinical_preprocessor.joblib"
    )

    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    if not preprocessor_path.exists():
        raise FileNotFoundError(
            preprocessor_path
        )

    frame = pd.read_csv(csv_path)

    preprocessor = joblib.load(
        preprocessor_path
    )

    if not hasattr(
        preprocessor,
        "feature_names_in_"
    ):
        raise RuntimeError(
            "Saved preprocessor does not contain "
            "feature_names_in_. Check the original "
            "preprocessing pipeline."
        )

    expected_columns = list(
        preprocessor.feature_names_in_
    )

    missing_columns = [
        column
        for column in expected_columns
        if column not in frame.columns
    ]

    if missing_columns:

        raise RuntimeError(
            f"{kind}: missing clinical fields: "
            f"{missing_columns}"
        )

    clinical_frame = (
        frame[expected_columns].copy()
    )

    # Convert categorical test values into
    # the format used during training.
    clinical_frame = normalize_categories(
        clinical_frame,
        preprocessor,
        kind
    )

    # Apply the original fitted preprocessing.
    # Do not call fit() or fit_transform().
    encoded = preprocessor.transform(
        clinical_frame
    )

    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()

    encoded = np.asarray(
        encoded,
        dtype=np.float32
    )

    if encoded.ndim != 2:
        raise RuntimeError(
            "Clinical features must be a 2D array."
        )

    if len(encoded) != len(frame):
        raise RuntimeError(
            "Clinical feature row count mismatch."
        )

    if not np.isfinite(encoded).all():
        raise RuntimeError(
            "Clinical features contain NaN or infinity."
        )

    clinical_path = (
        OUTPUT_DIR
        / f"{kind}_test_clinical.npy"
    )

    np.save(
        clinical_path,
        encoded
    )

    image_ids_path = None

    if kind == "retinal":

        if "image_id" not in frame.columns:

            raise RuntimeError(
                "Retinal test.csv must contain image_id."
            )

        if frame["image_id"].isna().any():

            raise RuntimeError(
                "Missing retinal image IDs."
            )

        if frame["image_id"].duplicated().any():

            raise RuntimeError(
                "Duplicate retinal image IDs."
            )

        image_ids_path = (
            OUTPUT_DIR
            / "retinal_test_image_ids.csv"
        )

        frame[["image_id"]].to_csv(
            image_ids_path,
            index=False
        )

    print(
        f"Samples: {len(frame)}"
    )

    print(
        f"Clinical features: {encoded.shape[1]}"
    )

    print(
        f"Saved clinical data: {clinical_path}"
    )

    return (
        csv_path,
        clinical_path,
        image_ids_path,
        len(frame)
    )


# ==================================================
# 4. CREATE TEST DATASET
# ==================================================

def build_dataset(
    kind,
    csv_path,
    clinical_path,
    image_ids_path
):

    if kind == "skin":

        dataset = SkinMultimodalDataset(
            csv_path=str(csv_path),
            image_dir=str(
                ROOT / "data/skin/images"
            ),
            clinical_path=str(
                clinical_path
            ),
            transform=skin_transforms
        )

    elif kind == "retinal":

        dataset = RetinalMultimodalDataset(
            csv_path=str(csv_path),
            image_dir=str(
                ROOT / "data/retinal/images"
            ),
            clinical_path=str(
                clinical_path
            ),
            image_ids_path=str(
                image_ids_path
            ),
            transform=retinal_transforms
        )

    else:

        raise ValueError(
            f"Unknown dataset type: {kind}"
        )

    return dataset


# ==================================================
# 5. LOAD TRAINED MULTIMODAL MODEL
# ==================================================

def load_trained_model(
    kind,
    clinical_dim
):

    if kind == "skin":

        classes = list(SKIN_CLASSES)

        checkpoint_path = (
            ROOT
            / "checkpoints"
            / "skin_multimodal_best.pth"
        )

        image_checkpoint = (
            ROOT
            / "checkpoints"
            / "skin_efficientnet_baseline.pth"
        )

        model_class = SkinMultimodalModel

    elif kind == "retinal":

        classes = RETINAL_CLASSES

        checkpoint_path = (
            ROOT
            / "checkpoints"
            / "retinal_multimodal_best.pth"
        )

        image_checkpoint = (
            ROOT
            / "checkpoints"
            / "retinal_efficientnet_best.pth"
        )

        model_class = RetinalMultimodalModel

    else:

        raise ValueError(
            f"Unknown model type: {kind}"
        )

    checkpoint = torch.load(
        checkpoint_path,
        map_location=DEVICE,
        weights_only=True
    )

    if list(
        checkpoint["class_names"]
    ) != classes:

        raise RuntimeError(
            f"{kind}: checkpoint class order mismatch."
        )

    checkpoint_clinical_dim = int(
        checkpoint["clinical_dim"]
    )

    if checkpoint_clinical_dim != clinical_dim:

        raise RuntimeError(
            f"{kind}: clinical dimension mismatch. "
            f"Expected {checkpoint_clinical_dim}, "
            f"received {clinical_dim}."
        )

    model = model_class(
        clinical_dim=clinical_dim,
        num_classes=len(classes),
        image_checkpoint=str(
            image_checkpoint
        )
    )

    model.load_state_dict(
        checkpoint["model_state_dict"],
        strict=True
    )

    model.to(DEVICE)

    model.eval()

    print(
        f"{kind} trained model loaded successfully."
    )

    return model, classes


# ==================================================
# 6. EVALUATION AND METRICS
# ==================================================

def evaluate(kind):

    print("\n" + "=" * 55)

    print(
        f"FINAL {kind.upper()} "
        f"MULTIMODAL TEST EVALUATION"
    )

    print("=" * 55)

    (
        csv_path,
        clinical_path,
        image_ids_path,
        expected_count
    ) = prepare_clinical(kind)

    dataset = build_dataset(
        kind,
        csv_path,
        clinical_path,
        image_ids_path
    )

    if len(dataset) != expected_count:

        raise RuntimeError(
            f"{kind}: dataset sample count mismatch."
        )

    loader = DataLoader(
        dataset,
        batch_size=8,
        shuffle=False,
        num_workers=0
    )

    clinical_dim = (
        dataset.clinical.shape[1]
    )

    model, classes = load_trained_model(
        kind,
        clinical_dim
    )

    true_labels = []

    predicted_labels = []

    # Inference without modifying model weights
    with torch.inference_mode():

        for images, clinical, labels in loader:

            images = images.to(DEVICE)

            clinical = clinical.to(DEVICE)

            logits = model(
                images,
                clinical
            )

            predictions = logits.argmax(
                dim=1
            )

            true_labels.extend(
                labels.cpu().numpy().tolist()
            )

            predicted_labels.extend(
                predictions.cpu().numpy().tolist()
            )

    y_true = np.asarray(
        true_labels,
        dtype=int
    )

    y_pred = np.asarray(
        predicted_labels,
        dtype=int
    )

    labels = list(
        range(len(classes))
    )

    if len(y_true) != expected_count:

        raise RuntimeError(
            "Not all test samples were evaluated."
        )

    if not np.isin(
        y_true,
        labels
    ).all():

        raise RuntimeError(
            "Unknown test label indices found."
        )

    # ------------------------------------------
    # Calculate metrics
    # ------------------------------------------

    metrics = {
        "dataset": kind,
        "split": "test",
        "samples": int(len(y_true)),
        "accuracy": float(
            accuracy_score(
                y_true,
                y_pred
            )
        ),
        "balanced_accuracy": float(
            balanced_accuracy_score(
                y_true,
                y_pred
            )
        ),
        "macro_f1": float(
            f1_score(
                y_true,
                y_pred,
                labels=labels,
                average="macro",
                zero_division=0
            )
        )
    }

    if kind == "retinal":

        metrics[
            "quadratic_weighted_kappa"
        ] = float(
            cohen_kappa_score(
                y_true,
                y_pred,
                labels=labels,
                weights="quadratic"
            )
        )

    # ------------------------------------------
    # Classification report
    # ------------------------------------------

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=classes,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    print("\nFINAL TEST METRICS")

    print(
        json.dumps(
            metrics,
            indent=2
        )
    )

    print(
        "\nCLASSIFICATION REPORT\n"
    )

    print(report)

    print(
        "\nCONFUSION MATRIX\n"
    )

    print(matrix)

    # ------------------------------------------
    # Save metrics as JSON
    # ------------------------------------------

    metrics_path = (
        OUTPUT_DIR
        / f"{kind}_metrics.json"
    )

    with metrics_path.open(
        "w",
        encoding="utf-8"
    ) as handle:

        json.dump(
            metrics,
            handle,
            indent=2
        )

    # ------------------------------------------
    # Save classification report
    # ------------------------------------------

    report_path = (
        OUTPUT_DIR
        / f"{kind}_classification_report.txt"
    )

    report_path.write_text(
        report,
        encoding="utf-8"
    )

    # ------------------------------------------
    # Save predictions
    # ------------------------------------------

    predictions_path = (
        OUTPUT_DIR
        / f"{kind}_predictions.csv"
    )

    pd.DataFrame({
        "true_label": [
            classes[index]
            for index in y_true
        ],
        "predicted_label": [
            classes[index]
            for index in y_pred
        ]
    }).to_csv(
        predictions_path,
        index=False
    )

    # ------------------------------------------
    # Save confusion matrix
    # ------------------------------------------

    figure, axis = plt.subplots(
        figsize=(8, 7)
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=classes
    )

    display.plot(
        ax=axis,
        cmap="Blues",
        values_format="d",
        colorbar=False
    )

    axis.set_title(
        f"{kind.title()} Multimodal Model "
        f"- Test Set"
    )

    figure.tight_layout()

    confusion_path = (
        OUTPUT_DIR
        / f"{kind}_confusion_matrix.png"
    )

    figure.savefig(
        confusion_path,
        dpi=160
    )

    plt.close(figure)

    print(
        "\nSaved evaluation results to:",
        OUTPUT_DIR
    )

    return metrics


# ==================================================
# 7. MAIN PROGRAM
# ==================================================

if __name__ == "__main__":

    skin_results = evaluate(
        "skin"
    )

    retinal_results = evaluate(
        "retinal"
    )

    summary = pd.DataFrame([
        skin_results,
        retinal_results
    ])

    summary_path = (
        OUTPUT_DIR
        / "summary.csv"
    )

    summary.to_csv(
        summary_path,
        index=False
    )

    print("\n" + "=" * 55)

    print(
        "FINAL TEST EVALUATION COMPLETED"
    )

    print("=" * 55)

    print(
        "All results saved in:",
        OUTPUT_DIR
    )
