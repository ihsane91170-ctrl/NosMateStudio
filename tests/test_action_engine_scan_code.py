from app.automation.action_engine import ActionEngine
from app.automation.win32_scan_code import SCAN_CODE_1_AMPERSAND


class Mouse:
    def click(self, x: int, y: int) -> None: pass
    def double_click(self, x: int, y: int) -> None: pass


class Keyboard:
    def __init__(self) -> None:
        self.keys: list[str] = []

    def press(self, key: str) -> None:
        self.keys.append(key)


def test_capture_uses_physical_scan_code_not_keyboard_executor() -> None:
    keyboard = Keyboard()
    scan_codes: list[int] = []
    engine = ActionEngine(
        Mouse(),
        keyboard,
        sleep_fn=lambda _seconds: None,
        scan_code_press_fn=scan_codes.append,
    )

    engine.press_capture_azerty()

    assert scan_codes == [SCAN_CODE_1_AMPERSAND]
    assert keyboard.keys == []
