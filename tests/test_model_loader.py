from backend.model_loader import load_models

models = load_models()

print("===== MODEL LOADING TEST =====")

print("Skin model loaded:", models["skin_model"] is not None)

print(
    "Retinal model loaded:",
    models["retinal_model"] is not None
)

print(
    "Skin clinical features:",
    len(models["skin_preprocessor"].get_feature_names_out())
)

print(
    "Retinal clinical features:",
    len(models["retinal_preprocessor"].get_feature_names_out())
)

assert len(
    models["skin_preprocessor"].get_feature_names_out()
) == 43

assert len(
    models["retinal_preprocessor"].get_feature_names_out()
) == 5

print("\nBoth models loaded successfully!")
