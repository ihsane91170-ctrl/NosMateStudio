from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PIL import Image, ImageGrab

from app.vision.window_detector import GameWindow


class ScreenshotBackend(Protocol):
    def grab(
        self,
        bbox: tuple[int, int, int, int],
    ) -> Image.Image:
        ...


class PillowScreenshotBackend:
    def grab(
        self,
        bbox: tuple[int, int, int, int],
    ) -> Image.Image:
        return ImageGrab.grab(bbox=bbox)


@dataclass(slots=True)
class WindowScreenshotProvider:
    backend: ScreenshotBackend

    def capture(self, window: GameWindow) -> Image.Image:
        if not window.is_usable:
            raise ValueError(
                "Impossible de capturer une fenêtre inutilisable."
            )

        bbox = (
            window.left,
            window.top,
            window.right,
            window.bottom,
        )

        return self.backend.grab(bbox)