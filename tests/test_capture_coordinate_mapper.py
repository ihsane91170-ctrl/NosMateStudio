import pytest

from app.vision.coordinates import CaptureCoordinateMapper
from app.vision.window_detector import GameWindow


def test_mapper_keeps_coordinates_at_one_hundred_percent_scaling() -> None:
    window = GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )

    mapper = CaptureCoordinateMapper(window, 1280, 720)

    assert mapper.to_screen((640, 360)) == (740, 560)


def test_mapper_handles_dpi_scaled_capture() -> None:
    window = GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )

    mapper = CaptureCoordinateMapper(window, 1600, 900)

    assert mapper.to_screen((800, 450)) == (740, 560)


def test_mapper_rejects_empty_capture() -> None:
    window = GameWindow(
        title="NosTale",
        left=0,
        top=0,
        width=1280,
        height=720,
    )

    with pytest.raises(ValueError):
        CaptureCoordinateMapper(window, 0, 720)
