import torch

from src.models.skin_model import build_skin_model

model = build_skin_model(num_classes=6)

model.eval()

# Artificial test batch of two images
dummy_images = torch.randn(2, 3, 224, 224)

with torch.no_grad():
    outputs = model(dummy_images)

print("Output shape:", outputs.shape)
print("Trainable parameters:", sum(
    p.numel() for p in model.parameters()
    if p.requires_grad
))

assert outputs.shape == (2, 6)

print("EfficientNet-B0 model test passed!")
