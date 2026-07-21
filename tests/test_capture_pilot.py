from __future__ import annotations

from PIL import Image, ImageDraw

from app.production.capture_pilot import CapturePilot, CapturePilotConfig


class Keyboard:
    def __init__(self) -> None:
        self.keys: list[str] = []

    def press(self, key: str) -> None:
        self.keys.append(key)


class Waiter:
    def wait(self, seconds: float) -> None:
        pass


class Screenshots:
    def __init__(self, images: list[Image.Image]) -> None:
        self.images = iter(images)

    def capture(self, window) -> Image.Image:
        return next(self.images)


class Activator:
    def __init__(self, result: bool = True) -> None:
        self.result = result

    def activate(self) -> bool:
        return self.result


def image(changed: bool = False) -> Image.Image:
    result = Image.new("RGB", (200, 100), "black")
    if changed:
        draw = ImageDraw.Draw(result)
        draw.rectangle((150, 15, 198, 85), fill="white")
    return result


def test_capture_succeeds_when_pet_list_changes() -> None:
    keyboard = Keyboard()
    pilot = CapturePilot(keyboard, Waiter(), Screenshots([image(), image(), image(True)]), Activator())
    result = pilot.run(object(), CapturePilotConfig(capture_key="W", max_attempts=1))
    assert result.succeeded
    assert result.attempts == 1
    assert keyboard.keys == ["W"]


def test_capture_retries_when_first_attempt_has_no_change() -> None:
    keyboard = Keyboard()
    pilot = CapturePilot(
        keyboard,
        Waiter(),
        Screenshots([image(), image(), image(), image(True)]),
        Activator(),
    )
    result = pilot.run(object(), CapturePilotConfig(capture_key="W", max_attempts=2))
    assert result.succeeded
    assert result.attempts == 2
    assert keyboard.keys == ["W", "W"]


def test_capture_fails_without_confirmed_change() -> None:
    keyboard = Keyboard()
    pilot = CapturePilot(
        keyboard,
        Waiter(),
        Screenshots([image(), image(), image(), image()]),
        Activator(),
    )
    result = pilot.run(object(), CapturePilotConfig(capture_key="W", max_attempts=2))
    assert not result.succeeded
    assert result.attempts == 2


def test_capture_refuses_unstable_baseline() -> None:
    keyboard = Keyboard()
    pilot = CapturePilot(
        keyboard,
        Waiter(),
        Screenshots([image(), image(True)]),
        Activator(),
    )
    result = pilot.run(object(), CapturePilotConfig(capture_key="W"))
    assert not result.succeeded
    assert result.attempts == 0
    assert keyboard.keys == []


def test_capture_fails_when_window_cannot_be_activated() -> None:
    pilot = CapturePilot(Keyboard(), Waiter(), Screenshots([]), Activator(False))
    result = pilot.run(object(), CapturePilotConfig(capture_key="W"))
    assert not result.succeeded
    assert result.attempts == 0
