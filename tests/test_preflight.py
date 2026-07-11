from app.calibration.models import CalibrationProfile
from app.configuration.defaults import DEFAULT_SETTINGS
from app.execution import (
    PreflightCheck,
    PreflightStatus,
)
from app.vision.window_detector import GameWindow


class WindowDetectorStub:
    def __init__(self, window: GameWindow | None) -> None:
        self.window = window

    def detect(self) -> GameWindow | None:
        return self.window


def usable_window() -> GameWindow:
    return GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )


def test_preflight_is_ready_for_keyboard_only_workflow() -> None:
    check = PreflightCheck(WindowDetectorStub(usable_window()))

    result = check.run(
        settings=DEFAULT_SETTINGS,
        calibration=CalibrationProfile(),
        require_calibration=False,
    )

    assert result.status is PreflightStatus.READY
    assert result.allowed is True


def test_preflight_rejects_missing_window() -> None:
    check = PreflightCheck(WindowDetectorStub(None))

    result = check.run(
        settings=DEFAULT_SETTINGS,
        calibration=CalibrationProfile(),
        require_calibration=False,
    )

    assert result.status is PreflightStatus.WINDOW_NOT_FOUND
    assert result.allowed is False


def test_preflight_rejects_unusable_window() -> None:
    window = GameWindow(
        title="NosTale",
        left=0,
        top=0,
        width=0,
        height=720,
    )
    check = PreflightCheck(WindowDetectorStub(window))

    result = check.run(
        settings=DEFAULT_SETTINGS,
        calibration=CalibrationProfile(),
        require_calibration=False,
    )

    assert result.status is PreflightStatus.WINDOW_NOT_USABLE


def test_preflight_requires_calibration_when_requested() -> None:
    check = PreflightCheck(WindowDetectorStub(usable_window()))

    result = check.run(
        settings=DEFAULT_SETTINGS,
        calibration=CalibrationProfile(),
        require_calibration=True,
    )

    assert result.status is PreflightStatus.CALIBRATION_MISSING
    assert result.allowed is False