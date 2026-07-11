import pytest

from app.safety import (
    SafetyManager,
    SafetyStatus,
    SafetyViolationError,
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


def test_safety_is_valid_when_window_is_usable() -> None:
    manager = SafetyManager(WindowDetectorStub(usable_window()))

    result = manager.check()

    assert result.status is SafetyStatus.SAFE
    assert result.is_safe is True


def test_safety_rejects_missing_window() -> None:
    manager = SafetyManager(WindowDetectorStub(None))

    result = manager.check()

    assert result.status is SafetyStatus.WINDOW_NOT_FOUND
    assert result.is_safe is False


def test_safety_rejects_invalid_window_dimensions() -> None:
    window = GameWindow(
        title="NosTale",
        left=0,
        top=0,
        width=0,
        height=720,
    )
    manager = SafetyManager(WindowDetectorStub(window))

    result = manager.check()

    assert result.status is SafetyStatus.WINDOW_NOT_USABLE


def test_stop_request_blocks_automation() -> None:
    manager = SafetyManager(WindowDetectorStub(usable_window()))
    manager.request_stop()

    with pytest.raises(SafetyViolationError):
        manager.ensure_safe()


def test_stop_request_can_be_reset() -> None:
    manager = SafetyManager(WindowDetectorStub(usable_window()))
    manager.request_stop()
    manager.reset_stop()

    assert manager.check().is_safe is True