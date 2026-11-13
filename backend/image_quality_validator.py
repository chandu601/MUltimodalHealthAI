import cv2
import numpy as np
from PIL import Image


# Initial experimental thresholds.
# These are not clinically validated.
MIN_BLUR_SCORE = 30.0
MIN_BRIGHTNESS = 35.0
MAX_BRIGHTNESS = 220.0


def validate_image_quality(image: Image.Image):
    """
    Perform basic technical image-quality checks.

    Checks:
    1. Blur
    2. Low brightness
    3. Excessive brightness

    This does not establish clinical image quality.
    """

    rgb_image = np.array(image.convert("RGB"))

    gray_image = cv2.cvtColor(
        rgb_image,
        cv2.COLOR_RGB2GRAY
    )

    # Blur estimation using variance of Laplacian
    blur_score = float(
        cv2.Laplacian(
            gray_image,
            cv2.CV_64F
        ).var()
    )

    # Average image brightness
    brightness = float(gray_image.mean())

    issues = []

    if blur_score < MIN_BLUR_SCORE:
        issues.append("Image may be blurry")

    if brightness < MIN_BRIGHTNESS:
        issues.append("Image is too dark")

    elif brightness > MAX_BRIGHTNESS:
        issues.append("Image is too bright")

    return {
        "accepted": len(issues) == 0,
        "blur_score": round(blur_score, 2),
        "brightness": round(brightness, 2),
        "issues": issues,
        "message": (
            "Basic image-quality checks passed"
            if not issues
            else "; ".join(issues)
        )
    }
