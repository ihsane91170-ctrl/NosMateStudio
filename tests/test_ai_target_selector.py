import pytest

from app.vision.ai_detector import ObjectDetection
from app.vision.ai_target_selector import AITargetSelector


def detection(name: str, confidence: float, x: int, y: int) -> ObjectDetection:
    return ObjectDetection(name, confidence, x - 10, y - 10, x + 10, y + 10)


def test_ignores_non_chicken_classes() -> None:
    selector = AITargetSelector()
    ranked = selector.rank(
        (
            detection("not_chicken", 0.99, 500, 300),
            detection("chicken", 0.80, 400, 300),
        ),
        image_width=800,
        image_height=600,
    )
    assert len(ranked) == 1
    assert ranked[0].detection.class_name == "chicken"


def test_prefers_center_when_confidences_are_equal() -> None:
    selector = AITargetSelector()
    centered = detection("chicken", 0.90, 400, 300)
    corner = detection("chicken", 0.90, 50, 50)
    selected = selector.choose(
        (corner, centered), image_width=800, image_height=600
    )
    assert selected is not None
    assert selected.detection is centered


def test_confidence_remains_main_weight() -> None:
    selector = AITargetSelector(confidence_weight=0.70, center_weight=0.30)
    high_confidence = detection("chicken", 0.99, 250, 300)
    low_confidence_centered = detection("chicken", 0.60, 400, 300)
    selected = selector.choose(
        (low_confidence_centered, high_confidence),
        image_width=800,
        image_height=600,
    )
    assert selected is not None
    assert selected.detection is high_confidence


def test_returns_none_without_chicken() -> None:
    selector = AITargetSelector()
    assert selector.choose(
        (detection("not_chicken", 0.99, 400, 300),),
        image_width=800,
        image_height=600,
    ) is None


def test_scores_are_sorted_descending() -> None:
    selector = AITargetSelector()
    ranked = selector.rank(
        (
            detection("chicken", 0.70, 50, 50),
            detection("chicken", 0.90, 400, 300),
            detection("chicken", 0.80, 300, 300),
        ),
        image_width=800,
        image_height=600,
    )
    assert [item.score for item in ranked] == sorted(
        [item.score for item in ranked], reverse=True
    )


def test_invalid_image_size_is_rejected() -> None:
    selector = AITargetSelector()
    with pytest.raises(ValueError):
        selector.rank((), image_width=0, image_height=600)
