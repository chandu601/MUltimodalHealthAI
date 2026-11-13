
import json
import mimetypes
from pathlib import Path

import joblib
import pandas as pd

from fastapi.testclient import TestClient

from backend.main import app


# ==========================================
# PROJECT PATH
# ==========================================

ROOT = Path(__file__).resolve().parents[1]


# ==========================================
# HELPER: CONVERT CSV VALUES TO JSON
# ==========================================

def prepare_metadata(row, preprocessor):
    metadata = {}

    for column in preprocessor.feature_names_in_:
        value = row[column]

        if pd.isna(value):
            metadata[column] = None

        elif hasattr(value, "item"):
            metadata[column] = value.item()

        else:
            metadata[column] = value

    return metadata


# ==========================================
# 1. LOAD SKIN TEST SAMPLE
# ==========================================

def load_skin_test_sample():

    csv_path = ROOT / "data/splits/skin/test.csv"

    frame = pd.read_csv(csv_path)

    preprocessor = joblib.load(
        ROOT
        / "data/processed/skin"
        / "clinical_preprocessor.joblib"
    )

    image_root = ROOT / "data/skin"

    for _, row in frame.iterrows():

        filename = Path(
            str(row["img_id"])
        ).name

        matches = [
            path
            for path in image_root.rglob(filename)
            if path.is_file()
        ]

        if not matches:
            continue

        image_path = matches[0]

        metadata = prepare_metadata(
            row,
            preprocessor
        )

        return image_path, metadata

    raise FileNotFoundError(
        "No matching skin test image was found."
    )


# ==========================================
# 2. LOAD RETINAL TEST SAMPLE
# ==========================================

def load_retinal_test_sample():

    csv_path = ROOT / "data/splits/retinal/test.csv"

    frame = pd.read_csv(csv_path)

    preprocessor = joblib.load(
        ROOT
        / "data/processed/retinal"
        / "clinical_preprocessor.joblib"
    )

    image_root = ROOT / "data/retinal/images"

    for _, row in frame.iterrows():

        # Retinal CSV uses image_id, not img_id.
        image_id = str(
            row["image_id"]
        ).strip()

        # Images are stored as JPG files.
        image_path = (
            image_root / f"{image_id}.jpg"
        )

        if not image_path.is_file():
            continue

        metadata = prepare_metadata(
            row,
            preprocessor
        )

        return image_path, metadata

    raise FileNotFoundError(
        "No matching retinal test image was found."
    )


# ==========================================
# 3. HELPER: CALL PREDICTION AND EXPLANATION
# ==========================================

def check_prediction_explanation(
    screening_type,
    image_path,
    metadata,
    expected_feature_count
):

    image_bytes = image_path.read_bytes()

    metadata_json = json.dumps(metadata)

    mime_type = (
        mimetypes.guess_type(image_path.name)[0]
        or "image/jpeg"
    )

    files = {
        "file": (
            image_path.name,
            image_bytes,
            mime_type
        )
    }

    with TestClient(app) as client:

        # Get the model prediction.
        prediction_response = client.post(
            f"/predict/{screening_type}",
            files=files,
            data={"metadata": metadata_json}
        )

        assert prediction_response.status_code == 200, (
            "Prediction failed: "
            + prediction_response.text[:1000]
        )

        prediction = prediction_response.json()

        # Generate the explanation.
        explanation_response = client.post(
            f"/explain/{screening_type}",
            files=files,
            data={"metadata": metadata_json}
        )

        assert explanation_response.status_code == 200, (
            "Explanation failed: "
            + explanation_response.text[:1000]
        )

        explanation = explanation_response.json()

    # Verify correct screening type.
    assert (
        prediction["screening_type"]
        == screening_type
    )

    assert (
        explanation["screening_type"]
        == screening_type
    )

    # Verify matching predicted classes.
    assert (
        prediction["predicted_class"]
        == explanation["predicted_class"]
    ), (
        "Prediction and explanation returned "
        "different disease classes."
    )

    # Verify Grad-CAM output.
    gradcam = explanation.get(
        "visual_explanation"
    )

    assert isinstance(gradcam, str)

    assert len(gradcam) > 100

    # Verify clinical feature contributions.
    contributions = explanation.get(
        "clinical_contributions"
    )

    assert isinstance(contributions, dict)

    assert len(contributions) == (
        expected_feature_count
    )

    print(
        f"\n{screening_type.upper()} TEST PASSED"
    )

    print(
        "Image:",
        image_path.name
    )

    print(
        "Predicted class:",
        prediction["predicted_class"]
    )

    print(
        "Explanation class:",
        explanation["predicted_class"]
    )

    print(
        "Clinical feature groups:",
        len(contributions)
    )


# ==========================================
# TEST 1: SKIN CONSISTENCY
# ==========================================

def test_skin_prediction_explanation_consistency():

    image_path, metadata = (
        load_skin_test_sample()
    )

    check_prediction_explanation(
        screening_type="skin",
        image_path=image_path,
        metadata=metadata,
        expected_feature_count=12
    )


# ==========================================
# TEST 2: RETINAL CONSISTENCY
# ==========================================

def test_retinal_prediction_explanation_consistency():

    image_path, metadata = (
        load_retinal_test_sample()
    )

    check_prediction_explanation(
        screening_type="retinal",
        image_path=image_path,
        metadata=metadata,
        expected_feature_count=3
    )
