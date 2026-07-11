import pyautogui

from app.executors.exceptions import ExecutorDisabledError
from app.executors.mouse.validation import validate_coordinates


class PyAutoGUIMouseExecutor:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def click(self, x: int, y: int) -> None:
        validate_coordinates(x, y)

        if not self.enabled:
            raise ExecutorDisabledError(
                "Le Mouse Executor est désactivé."
            )

        pyautogui.click(x, y)

    def double_click(self, x: int, y: int) -> None:
        validate_coordinates(x, y)

        if not self.enabled:
            raise ExecutorDisabledError(
                "Le Mouse Executor est désactivé."
            )

        pyautogui.doubleClick(x, y)