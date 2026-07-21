from __future__ import annotations

from collections.abc import Callable
import time
from typing import Protocol

from app.automation.win32_scan_code import (
    SCAN_CODE_1_AMPERSAND,
    press_scan_code,
)


class MouseExecutorProtocol(Protocol):
    def click(self, x: int, y: int) -> None: ...
    def double_click(self, x: int, y: int) -> None: ...


class KeyboardExecutorProtocol(Protocol):
    def press(self, key: str) -> None: ...


class ActionEngine:
    """Point d'entrée testable pour les actions souris, clavier et attentes."""

    def __init__(
        self,
        mouse: MouseExecutorProtocol,
        keyboard: KeyboardExecutorProtocol,
        *,
        sleep_fn: Callable[[float], None] = time.sleep,
        scan_code_press_fn: Callable[[int], None] = press_scan_code,
    ) -> None:
        self._mouse = mouse
        self._keyboard = keyboard
        self._sleep = sleep_fn
        self._scan_code_press = scan_code_press_fn

    def click(self, x: int, y: int) -> None:
        self._mouse.click(x, y)

    def double_click(self, x: int, y: int) -> None:
        self._mouse.double_click(x, y)

    def press(self, key: str) -> None:
        normalized = key.strip().lower()
        if normalized in {"&", "1", "ampersand"}:
            raise ValueError("La touche de capture est interdite dans le workflow d'attaque.")
        self._keyboard.press(normalized)

    def press_capture_azerty(self) -> None:
        """Envoie la touche physique ``1/&`` par son scan code Windows.

        L'envoi contourne la traduction AZERTY/QWERTY de PyAutoGUI et de
        PyDirectInput. La touche de capture reste isolée de l'API d'attaque.
        """
        self._scan_code_press(SCAN_CODE_1_AMPERSAND)

    def wait(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("Le délai ne peut pas être négatif.")
        self._sleep(seconds)
