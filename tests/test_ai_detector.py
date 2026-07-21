from pathlib import Path

import pytest
from PIL import Image

from app.vision.ai_detector import ModelNotAvailableError, ObjectDetection, UltralyticsObjectDetector


def test_object_detection_center() -> None:
    detection = ObjectDetection("chicken", 0.9, 10, 20, 30, 50)
    assert detection.center == (20, 35)


def test_missing_model_is_explicit(tmp_path: Path) -> None:
    detector = UltralyticsObjectDetector(tmp_path / "missing.pt")
    with pytest.raises(ModelNotAvailableError, match="Modèle IA introuvable"):
        detector.detect(Image.new("RGB", (100, 100)))


def test_invalid_confidence_is_rejected(tmp_path: Path) -> None:
    detector = UltralyticsObjectDetector(tmp_path / "missing.pt")
    with pytest.raises(ValueError):
        detector.detect(Image.new("RGB", (100, 100)), confidence=0)
