
from fastapi import FastAPI

from backend.prediction_api import (
    router as prediction_router,
)

from backend.explanation_api import (
    router as retinal_explanation_router,
)

from backend.skin_explanation_api import (
    router as skin_explanation_router,
)


app = FastAPI(
    title="Explainable Multimodal Healthcare AI",
    description=(
        "Experimental research system for "
        "skin lesion and retinal disease screening."
    ),
    version="0.4.0",
)


# Prediction endpoints
app.include_router(
    prediction_router
)

# Retinal explanation endpoint
app.include_router(
    retinal_explanation_router
)

# Skin explanation endpoint
app.include_router(
    skin_explanation_router
)


@app.get("/")
def root():
    return {
        "application": "Multimodal Healthcare AI",
        "status": "running",
        "screening_modules": [
            "skin",
            "retinal",
        ],
        "clinical_use": False,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "API server is running",
    }
