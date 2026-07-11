import pyautogui

from app.executors.exceptions import ExecutorDisabledError
from app.executors.keyboard.validation import (
    normalize_and_validate_key,
    to_pyautogui_key,
)


class PyAutoGUIKeyboardExecutor:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def press(self, key: str) -> None:
        normalized = normalize_and_validate_key(key)

        if not self.enabled:
            raise ExecutorDisabledError(
                "L'exécuteur clavier réel est désactivé."
            )

        pyautogui.press(to_pyautogui_key(normalized))