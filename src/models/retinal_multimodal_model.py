from pathlib import Path

import torch
import torch.nn as nn

from src.models.retinal_model import build_retinal_model


class RetinalMultimodalModel(nn.Module):

    def __init__(
        self,
        clinical_dim=5,
        num_classes=5,
        image_checkpoint="checkpoints/retinal_efficientnet_best.pth"
    ):
        super().__init__()

        # ==================================
        # 1. LOAD RETINAL IMAGE ENCODER
        # ==================================

        self.image_model = build_retinal_model(
            num_classes=num_classes,
            pretrained=False
        )

        checkpoint_path = Path(image_checkpoint)

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Missing checkpoint: {checkpoint_path}"
            )

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=True
        )

        expected_classes = [
            "DR0", "DR1", "DR2", "DR3", "DR4"
        ]

        if checkpoint["class_names"] != expected_classes:
            raise ValueError(
                "Retinal checkpoint class order mismatch"
            )

        self.image_model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        # EfficientNet-B0 feature dimension
        image_dim = (
            self.image_model.classifier[1].in_features
        )

        # Remove the original classification head
        self.image_model.classifier = nn.Identity()

        # Freeze the retinal image encoder
        for parameter in self.image_model.parameters():
            parameter.requires_grad = False

        # ==================================
        # 2. CLINICAL FEATURE ENCODER
        # ==================================

        self.clinical_encoder = nn.Sequential(
            nn.Linear(clinical_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, 32),
            nn.ReLU()
        )

        # ==================================
        # 3. MULTIMODAL FUSION CLASSIFIER
        # ==================================

        self.fusion_classifier = nn.Sequential(
            nn.Linear(image_dim + 32, 128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, num_classes)
        )

    # ==================================
    # 4. TRAINING MODE
    # ==================================

    def train(self, mode=True):
        super().train(mode)

        # Keep the frozen image encoder in
        # evaluation mode, including BatchNorm.
        self.image_model.eval()

        return self

    # ==================================
    # 5. FORWARD PASS
    # ==================================

    def forward(self, images, clinical):

        if clinical.ndim != 2:
            raise ValueError(
                "Clinical input must have shape (batch, features)"
            )

        if images.shape[0] != clinical.shape[0]:
            raise ValueError(
                "Image and clinical batch sizes differ"
            )

        # Extract retinal image features
        # Keeping gradients enabled allows
        # Grad-CAM to be implemented later.
        image_features = self.image_model(images)

        # Process patient clinical information
        clinical_features = self.clinical_encoder(
            clinical
        )

        # Concatenate both modalities
        fused_features = torch.cat(
            [image_features, clinical_features],
            dim=1
        )

        # Output five classification logits
        outputs = self.fusion_classifier(
            fused_features
        )

        return outputs
