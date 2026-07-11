from __future__ import annotations

from dataclasses import dataclass

import pyautogui


@dataclass
class InputController:
    simulation_mode: bool = True

    def press(self, key: str) -> None:
        if self.simulation_mode:
            return
        pyautogui.press(key)

    def click(self, x: int, y: int, clicks: int = 1) -> None:
        if self.simulation_mode:
            return
        pyautogui.click(x=x, y=y, clicks=clicks, interval=0.12)
