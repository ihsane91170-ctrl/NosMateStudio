import sys
import types

fake_pyautogui = types.SimpleNamespace(
    press=lambda *_args, **_kwargs: None,
    click=lambda *_args, **_kwargs: None,
    moveTo=lambda *_args, **_kwargs: None,
)
sys.modules.setdefault("pyautogui", fake_pyautogui)
sys.modules.setdefault("pydirectinput", fake_pyautogui)

from app.capture.live_services import HotkeyReturnToExpZone


class KeyboardStub:
    def __init__(self):
        self.keys = []

    def press(self, key: str) -> None:
        self.keys.append(key)


class WindowDetectorStub:
    def __init__(self, activates: bool = True):
        self.activates = activates
        self.calls = 0

    def activate(self) -> bool:
        self.calls += 1
        return self.activates


def test_return_activates_game_waits_for_dialog_then_confirms():
    keyboard = KeyboardStub()
    window = WindowDetectorStub()
    sleeps = []
    service = HotkeyReturnToExpZone(
        "-",
        delay_seconds=4.0,
        confirmation_delay_seconds=0.80,
        activation_delay_seconds=0.20,
        keyboard=keyboard,
        window_detector=window,
        sleep_fn=sleeps.append,
    )

    assert service.return_to_exp_zone()
    assert window.calls == 1
    assert keyboard.keys == ["-", "enter"]
    assert sleeps == [0.20, 0.80, 4.0]
    assert "confirmation Entrée" in service.last_message


def test_return_stops_when_nostale_cannot_be_activated():
    keyboard = KeyboardStub()
    window = WindowDetectorStub(activates=False)
    sleeps = []
    service = HotkeyReturnToExpZone(
        "-",
        keyboard=keyboard,
        window_detector=window,
        sleep_fn=sleeps.append,
    )

    assert not service.return_to_exp_zone()
    assert keyboard.keys == []
    assert sleeps == []
    assert "non activée" in service.last_message
