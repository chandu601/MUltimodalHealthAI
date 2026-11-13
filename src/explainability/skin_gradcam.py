import torch
import torch.nn.functional as F


class SkinGradCAM:
    def __init__(self, model):
        self.model = model
        self.activations = None
        self.gradients = None

        # Final convolutional feature block of EfficientNet-B0
        target_layer = model.image_model.features[-1]

        self.handle = target_layer.register_forward_hook(
            self._save_activations
        )

    def _save_activations(self, module, inputs, output):
        self.activations = output
        self.gradients = None

        if output.requires_grad:
            output.register_hook(self._save_gradients)

    def _save_gradients(self, gradient):
        self.gradients = gradient

    def generate(self, image, clinical, target_class=None):
        self.model.eval()

        if image.shape[0] != 1:
            raise ValueError("Grad-CAM expects one image")

        image = image.detach().clone().requires_grad_(True)

        self.model.zero_grad(set_to_none=True)

        with torch.enable_grad():
            logits = self.model(image, clinical)

            probabilities = F.softmax(logits, dim=1)

            predicted_class = int(
                probabilities.argmax(dim=1).item()
            )

            if target_class is None:
                target_class = predicted_class

            score = logits[0, target_class]
            score.backward()

        if self.gradients is None:
            raise RuntimeError(
                "Gradients unavailable. Check model forward()."
            )

        gradients = self.gradients.detach()
        activations = self.activations.detach()

        weights = gradients.mean(dim=(2, 3), keepdim=True)

        cam = (weights * activations).sum(dim=1)
        cam = F.relu(cam).unsqueeze(1)

        cam = F.interpolate(
            cam,
            size=image.shape[-2:],
            mode="bilinear",
            align_corners=False
        )

        cam = cam[0, 0]

        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)

        return {
            "heatmap": cam.cpu().numpy(),
            "predicted_class": predicted_class,
            "target_class": target_class,
            "probability": float(
                probabilities[0, predicted_class].item()
            )
        }

    def close(self):
        self.handle.remove()
