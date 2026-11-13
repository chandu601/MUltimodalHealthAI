from pathlib import Path

import joblib
import numpy as np
import torch


class RetinalClinicalExplainer:
    def __init__(self, model):
        self.model = model
        self.model.eval()

        root = Path("data/processed/retinal")

        preprocessor = joblib.load(
            root / "clinical_preprocessor.joblib"
        )

        self.feature_names = list(
            preprocessor.get_feature_names_out()
        )

        training_features = np.load(
            root / "train_clinical.npy",
            allow_pickle=False
        )

        self.baseline = torch.tensor(
            training_features.mean(axis=0),
            dtype=torch.float32
        )

        self.groups = {
            "age": [],
            "sex": [],
            "diabetes_type": []
        }

        for index, name in enumerate(self.feature_names):
            if name.startswith("numeric__age"):
                self.groups["age"].append(index)
            elif name.startswith("categorical__sexe_"):
                self.groups["sex"].append(index)
            elif name.startswith("categorical__type_diabete_"):
                self.groups["diabetes_type"].append(index)
            else:
                raise ValueError(
                    f"Unexpected clinical feature: {name}"
                )

    def explain(self, image, clinical, steps=32):
        if image.shape[0] != 1 or clinical.shape[0] != 1:
            raise ValueError("Expected one patient sample")

        if steps < 2:
            raise ValueError("steps must be >= 2")

        self.model.eval()

        device = clinical.device

        baseline = self.baseline.to(device).unsqueeze(0)
        actual = clinical.detach()
        difference = actual - baseline

        # Keep the retinal image fixed.
        with torch.no_grad():
            image_features = self.model.image_model(image)

            encoded = self.model.clinical_encoder(actual)
            fused = torch.cat(
                [image_features, encoded], dim=1
            )
            logits = self.model.fusion_classifier(fused)
            predicted_class = int(logits.argmax(1).item())

        accumulated = torch.zeros_like(actual)

        # Integrated Gradients
        for step in range(steps + 1):
            alpha = step / steps

            interpolated = (
                baseline + alpha * difference
            ).detach().requires_grad_(True)

            encoded = self.model.clinical_encoder(
                interpolated
            )

            fused = torch.cat(
                [image_features, encoded], dim=1
            )

            score = self.model.fusion_classifier(
                fused
            )[0, predicted_class]

            gradient = torch.autograd.grad(
                score, interpolated
            )[0]

            weight = 0.5 if step in (0, steps) else 1.0
            accumulated += weight * gradient.detach()

        attributions = (
            difference * accumulated / steps
        )[0].detach().cpu().numpy()

        contributions = {
            group: float(attributions[indices].sum())
            for group, indices in self.groups.items()
        }

        return predicted_class, contributions
