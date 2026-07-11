import pytest

from app.calibration.models import CalibrationProfile, CalibrationTarget
from app.calibration.service import CalibrationError, CalibrationService
from app.vision.window_detector import GameWindow


class MemoryRepository:
    def __init__(self) -> None:
        self.profile = CalibrationProfile()

    def load(self):
        return self.profile

    def save(self, profile):
        self.profile = profile


def game_window() -> GameWindow:
    return GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )


def test_capture_saves_relative_coordinates() -> None:
    repository = MemoryRepository()
    service = CalibrationService(repository)

    capture = service.capture(
        CalibrationTarget.ACCOMPANY_BUTTON,
        absolute_x=350,
        absolute_y=500,
        window=game_window(),
    )

    assert capture.relative_point.x == 250
    assert capture.relative_point.y == 300
    assert repository.profile.points[
        CalibrationTarget.ACCOMPANY_BUTTON
    ] == capture.relative_point


def test_capture_rejects_mouse_outside_game_window() -> None:
    service = CalibrationService(MemoryRepository())

    with pytest.raises(CalibrationError):
        service.capture(
            CalibrationTarget.PET_ICON_1,
            absolute_x=50,
            absolute_y=50,
            window=game_window(),
        )
