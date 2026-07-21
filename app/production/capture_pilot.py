from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any

import numpy as np
from PIL import Image


class KeyboardProtocol(Protocol):
    def press(self, key: str) -> None: ...


class WaitProtocol(Protocol):
    def wait(self, seconds: float) -> None: ...


class ScreenshotProtocol(Protocol):
    def capture(self, window: Any) -> Image.Image: ...


class WindowActivatorProtocol(Protocol):
    def activate(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class CapturePilotConfig:
    capture_key: str
    max_attempts: int = 3
    settle_delay: float = 0.6
    result_delay: float = 1.4
    pet_list_left_ratio: float = 0.64
    stable_threshold: float = 0.025
    changed_threshold: float = 0.045


@dataclass(frozen=True, slots=True)
class CapturePilotResult:
    succeeded: bool
    attempts: int
    message: str
    before_stability: float
    after_change: float


class CapturePilot:
    """Premier pilote réel : envoie la touche de capture et vérifie un changement visuel.

    La vérification porte volontairement sur la partie droite de la fenêtre, là où
    se trouve la liste des familiers. Elle ne prouve pas encore le niveau de PV de
    la cible ; la cible doit être préparée et sélectionnée par l'utilisateur.
    """

    def __init__(
        self,
        keyboard: KeyboardProtocol,
        waiter: WaitProtocol,
        screenshots: ScreenshotProtocol,
        activator: WindowActivatorProtocol,
    ) -> None:
        self._keyboard = keyboard
        self._waiter = waiter
        self._screenshots = screenshots
        self._activator = activator

    def run(self, window: Any, config: CapturePilotConfig) -> CapturePilotResult:
        if not config.capture_key.strip():
            raise ValueError("Le raccourci de capture est vide.")
        if config.max_attempts < 1:
            raise ValueError("Le nombre de tentatives doit être positif.")

        if not self._activator.activate():
            return CapturePilotResult(False, 0, "Impossible d'activer la fenêtre NosTale.", 0.0, 0.0)

        before_a = self._crop_pet_list(self._screenshots.capture(window), config.pet_list_left_ratio)
        self._waiter.wait(config.settle_delay)
        before_b = self._crop_pet_list(self._screenshots.capture(window), config.pet_list_left_ratio)
        stability = self._difference(before_a, before_b)

        if stability > config.stable_threshold:
            return CapturePilotResult(
                False,
                0,
                "La zone des familiers n'est pas assez stable. Fermez les animations ou fenêtres superposées puis réessayez.",
                stability,
                0.0,
            )

        baseline = before_b
        last_change = 0.0
        for attempt in range(1, config.max_attempts + 1):
            if not self._activator.activate():
                return CapturePilotResult(False, attempt - 1, "La fenêtre NosTale a perdu le focus.", stability, last_change)
            self._keyboard.press(config.capture_key)
            self._waiter.wait(config.result_delay)
            after = self._crop_pet_list(self._screenshots.capture(window), config.pet_list_left_ratio)
            last_change = self._difference(baseline, after)
            if last_change >= config.changed_threshold:
                return CapturePilotResult(
                    True,
                    attempt,
                    f"Changement visuel confirmé dans la liste des familiers après {attempt} tentative(s).",
                    stability,
                    last_change,
                )
            baseline = after

        return CapturePilotResult(
            False,
            config.max_attempts,
            "Aucun changement visuel confirmé après les tentatives de capture.",
            stability,
            last_change,
        )

    @staticmethod
    def _crop_pet_list(image: Image.Image, left_ratio: float) -> Image.Image:
        if not 0.0 < left_ratio < 1.0:
            raise ValueError("Le ratio de zone doit être compris entre 0 et 1.")
        left = round(image.width * left_ratio)
        return image.convert("RGB").crop((left, 0, image.width, image.height))

    @staticmethod
    def _difference(first: Image.Image, second: Image.Image) -> float:
        if first.size != second.size:
            second = second.resize(first.size)
        a = np.asarray(first, dtype=np.float32)
        b = np.asarray(second, dtype=np.float32)
        return float(np.mean(np.abs(a - b)) / 255.0)
