import torch

from src.models.skin_multimodal_model import SkinMultimodalModel


torch.set_num_threads(2)

model = SkinMultimodalModel(
    clinical_dim=43,
    num_classes=6
)

model.eval()

# Test batch of 2 samples
images = torch.randn(2, 3, 224, 224)
clinical = torch.randn(2, 43)

with torch.no_grad():
    outputs = model(images, clinical)

print("Image shape:", images.shape)
print("Clinical shape:", clinical.shape)
print("Output shape:", outputs.shape)

trainable_params = sum(
    p.numel() for p in model.parameters()
    if p.requires_grad
)

print("Trainable parameters:", trainable_params)

assert outputs.shape == (2, 6)
assert torch.isfinite(outputs).all()

print("Multimodal model test passed!")
