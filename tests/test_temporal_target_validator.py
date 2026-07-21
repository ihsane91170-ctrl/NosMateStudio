from app.vision.ai_detector import ObjectDetection
from app.vision.temporal_target_validator import TemporalTargetValidator


def det(confidence=0.95, left=100, top=100, cls="chicken"):
    return ObjectDetection(cls, confidence, left, top, left + 40, top + 40)


def test_rejects_single_frame_false_positive():
    validator = TemporalTargetValidator(minimum_confidence=0.90, required_frames=2)
    result = validator.validate(
        ((det(),), tuple(), tuple()), image_width=800, image_height=600
    )
    assert result.accepted is False


def test_rejects_detection_below_real_click_threshold():
    validator = TemporalTargetValidator(minimum_confidence=0.90, required_frames=2)
    frames = ((det(0.887),), (det(0.889, left=102),), (det(0.888, left=101),))
    result = validator.validate(frames, image_width=800, image_height=600)
    assert result.accepted is False


def test_accepts_stable_high_confidence_chicken():
    validator = TemporalTargetValidator(minimum_confidence=0.90, required_frames=2)
    frames = ((det(0.95),), (det(0.96, left=104),), (det(0.94, left=107),))
    result = validator.validate(frames, image_width=800, image_height=600)
    assert result.accepted is True
    assert result.matched_frames == 3
    assert result.target is not None


def test_rejects_chicken_overlapping_not_chicken():
    validator = TemporalTargetValidator(minimum_confidence=0.90, required_frames=2)
    frames = (
        (det(0.97), det(0.92, left=105, top=105, cls="not_chicken")),
        (det(0.96, left=102), det(0.91, left=106, top=105, cls="not_chicken")),
        tuple(),
    )
    result = validator.validate(frames, image_width=800, image_height=600)
    assert result.accepted is False
