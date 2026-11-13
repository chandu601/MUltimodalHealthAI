from pathlib import Path

import joblib
import numpy as np
import torch


class SkinClinicalExplainer:
    """
    Integrated Gradients for clinical metadata.

    Keeps the skin image fixed and measures
    contributions from encoded clinical inputs.
    """

    def __init__(
        self,
        model,
        preprocessor_path="data/processed/skin/clinical_preprocessor.joblib",
        train_features_path="data/processed/skin/train_clinical.npy"
    ):
        self.model = model
        self.model.eval()

        preprocessor = joblib.load(preprocessor_path)

        self.feature_names = list(
            preprocessor.get_feature_names_out()
        )

        train_features = np.load(
            train_features_path,
            allow_pickle=False
        )

        # Training-set mean is our reference input.
        # Do not use validation/test data to compute it.
        self.baseline = torch.tensor(
            train_features.mean(axis=0),
            dtype=torch.float32
        )

        self.original_features = [
            "age",
            "diameter_1",
            "diameter_2",
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

        assert len(self.feature_names) == len(self.baseline)

    def _original_name(self, encoded_name):
        """
        Map encoded one-hot columns and numeric
        missing indicators to original attributes.
        """
        name = encoded_name.split("__", 1)[-1]

        if name.startswith("missingindicator_"):
            name = name[len("missingindicator_"):]

        for feature in sorted(
            self.original_features,
            key=len,
            reverse=True
        ):
            if name == feature or name.startswith(feature + "_"):
                return feature

        raise ValueError(
            f"Unrecognized encoded feature: {encoded_name}"
        )

    def explain(
        self,
        image,
        clinical,
        target_class=None,
        steps=32
    ):
        if image.shape[0] != 1 or clinical.shape[0] != 1:
            raise ValueError("Provide exactly one sample")

        if steps < 2:
            raise ValueError("steps must be at least 2")

        self.model.eval()

        # The visual encoder is frozen, so calculate
        # its representation only once.
        with torch.no_grad():
            image_features = self.model.image_model(image)

        actual = clinical.detach()
        reference = self.baseline.to(
            device=actual.device,
            dtype=actual.dtype
        ).unsqueeze(0)

        with torch.no_grad():
            clinical_embedding = self.model.clinical_encoder(actual)

            logits = self.model.fusion_classifier(
                torch.cat(
                    [image_features, clinical_embedding],
                    dim=1
                )
            )

            predicted = int(logits.argmax(dim=1).item())

        if target_class is None:
            target_class = predicted

        if not 0 <= target_class < logits.shape[1]:
            raise ValueError("Invalid target class")

        # Trapezoidal integration from baseline to input
        accumulated = torch.zeros_like(actual)
        difference = actual - reference

        for step in range(steps + 1):
            alpha = step / steps

            interpolated = (
                reference + alpha * difference
            ).detach().requires_grad_(True)

            encoded = self.model.clinical_encoder(
                interpolated
            )

            fused = torch.cat(
                [image_features, encoded],
                dim=1
            )

            score = self.model.fusion_classifier(
                fused
            )[0, target_class]

            gradient = torch.autograd.grad(
                score,
                interpolated
            )[0]

            weight = 0.5 if step in (0, steps) else 1.0
            accumulated += weight * gradient.detach()

        attribution = (
            difference * accumulated / steps
        )[0].detach().cpu().numpy()

        # Combine 43 encoded inputs back into
        # the 12 original clinical attributes.
        grouped = {
            feature: 0.0
            for feature in self.original_features
        }

        for name, value in zip(
            self.feature_names, attribution
        ):
            original_name = self._original_name(name)

            grouped[original_name] += float(value)

        return {
            "predicted_class": predicted,
            "target_class": target_class,
            "contributions": grouped,
            "encoded_attributions": attribution
        }
