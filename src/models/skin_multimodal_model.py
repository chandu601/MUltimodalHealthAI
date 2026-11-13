from pathlib import Path

import torch
import torch.nn as nn

from src.models.skin_model import build_skin_model


class SkinMultimodalModel(nn.Module):

    def __init__(
        self,
        clinical_dim=43,
        num_classes=6,
        image_checkpoint="checkpoints/skin_efficientnet_baseline.pth"
    ):
        super().__init__()

        # 1. Load previously trained image model
        self.image_model = build_skin_model(
            num_classes=num_classes,
            pretrained=False
        )

        checkpoint_path = Path(image_checkpoint)

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Image checkpoint missing: {checkpoint_path}"
            )

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=True
        )

        expected_classes = [
            "ACK", "BCC", "MEL",
            "NEV", "SCC", "SEK"
        ]

        if checkpoint["class_names"] != expected_classes:
            raise ValueError("Checkpoint class order mismatch")

        self.image_model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        # EfficientNet-B0 outputs 1280 image features
        image_dim = self.image_model.classifier[1].in_features

        # Remove original classification head
        self.image_model.classifier = nn.Identity()

        # Freeze image encoder
        for parameter in self.image_model.parameters():
            parameter.requires_grad = False

        # 2. Clinical feature encoder
        self.clinical_encoder = nn.Sequential(
            nn.Linear(clinical_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        # 3. Fusion classifier
        self.fusion_classifier = nn.Sequential(
            nn.Linear(image_dim + 64, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )

    def train(self, mode=True):
        super().train(mode)

        # Frozen EfficientNet stays in eval mode
        self.image_model.eval()

        return self

    def forward(self, images, clinical_features):

        # Extract image features without gradients
        image_features = self.image_model(images)
        
        # Process clinical information
        clinical_features = self.clinical_encoder(
            clinical_features
        )

        # Combine image and clinical features
        fused_features = torch.cat(
            [image_features, clinical_features],
            dim=1
        )

        # Predict six classes
        outputs = self.fusion_classifier(fused_features)

        return outputs
