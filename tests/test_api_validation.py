import pytest

from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app

from backend.prediction_api import (
    parse_metadata,
    SKIN_NUMERIC,
    SKIN_CATEGORICAL,
)


# ==========================================
# 1. FASTAPI TEST CLIENT
# ==========================================

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==========================================
# TEST 1: UNSUPPORTED FILE FORMAT
# ==========================================

def test_skin_rejects_unsupported_file(client):

    response = client.post(
        "/predict/skin",
        files={
            "file": (
                "test.txt",
                b"This is not an image",
                "text/plain",
            )
        },
        data={
            "metadata": "{}"
        },
    )

    assert response.status_code == 415


# ==========================================
# TEST 2: EMPTY RETINAL IMAGE
# ==========================================

def test_retinal_rejects_empty_image(client):

    response = client.post(
        "/predict/retinal",
        files={
            "file": (
                "empty.png",
                b"",
                "image/png",
            )
        },
        data={
            "metadata": "{}"
        },
    )

    assert response.status_code == 422

    assert (
        response.json()["detail"]
        == "The uploaded image is empty."
    )


# ==========================================
# TEST 3: CORRUPTED SKIN IMAGE
# ==========================================

def test_skin_rejects_corrupted_image(client):

    response = client.post(
        "/predict/skin",
        files={
            "file": (
                "broken.png",
                b"Not a real PNG image",
                "image/png",
            )
        },
        data={
            "metadata": "{}"
        },
    )

    assert response.status_code == 422

    assert (
        response.json()["detail"]
        == "The uploaded image could not be read."
    )


# ==========================================
# TEST 4: INVALID CLINICAL METADATA
# ==========================================

def test_skin_rejects_invalid_metadata():

    invalid_metadata = '{"invalid_field": 123}'

    with pytest.raises(HTTPException) as error:

        parse_metadata(
            invalid_metadata,
            SKIN_NUMERIC,
            SKIN_CATEGORICAL,
        )

    assert error.value.status_code == 422

    detail = error.value.detail

    assert isinstance(detail, dict)

    assert detail.get("message") == (
        "Invalid clinical metadata fields."
    )

    assert "invalid_field" in detail.get(
        "unexpected_fields",
        [],
    )
