import torch

from src.models.retinal_multimodal_model import (
    RetinalMultimodalModel
)

torch.set_num_threads(2)

# Create multimodal model
model = RetinalMultimodalModel(
    clinical_dim=5,
    num_classes=5
)

model.eval()

# Artificial batch of two samples
images = torch.randn(
    2, 3, 224, 224
)

clinical_features = torch.randn(
    2, 5
)

# Perform forward pass
with torch.no_grad():
    outputs = model(
        images,
        clinical_features
    )

print("\n===== RETINAL MULTIMODAL MODEL TEST =====")

print("Image shape:", images.shape)
print("Clinical shape:", clinical_features.shape)
print("Output shape:", outputs.shape)

trainable_params = sum(
    p.numel()
    for p in model.parameters()
    if p.requires_grad
)

print("Trainable parameters:", trainable_params)

# Verify dimensions and numerical validity
assert outputs.shape == (2, 5)
assert torch.isfinite(outputs).all()
assert trainable_params > 0

# Confirm image encoder is frozen
assert all(
    not p.requires_grad
    for p in model.image_model.parameters()
)

print("\nRetinal multimodal model test passed!")
