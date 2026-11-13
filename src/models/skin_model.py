import torch.nn as nn
from torchvision.models import (
    efficientnet_b0,
    EfficientNet_B0_Weights
)


def build_skin_model(num_classes=6, pretrained=True):

    weights = (
        EfficientNet_B0_Weights.DEFAULT
        if pretrained else None
    )

    model = efficientnet_b0(weights=weights)

    # Freeze pretrained feature extractor
    for parameter in model.features.parameters():
        parameter.requires_grad = False

    # Replace final classifier for 6 skin classes
    in_features = model.classifier[1].in_features

    model.classifier[1] = nn.Linear(
        in_features,
        num_classes
    )

    return model
