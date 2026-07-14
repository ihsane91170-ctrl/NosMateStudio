from __future__ import annotations

from dataclasses import dataclass

from app.vision.window_detector import GameWindow


@dataclass(frozen=True, slots=True)
class CaptureCoordinateMapper:
    """Convert coordinates from a captured image to desktop coordinates.

    Pillow/ImageGrab may return an image whose pixel dimensions differ from
    the logical dimensions reported by the Windows window manager when DPI
    scaling is enabled. This mapper keeps clicks aligned with detections in
    both 100% and scaled display configurations.
    """

    window: GameWindow
    capture_width: int
    capture_height: int

    def __post_init__(self) -> None:
        if self.capture_width <= 0 or self.capture_height <= 0:
            raise ValueError("Les dimensions de la capture doivent être positives.")

    def to_screen(self, point: tuple[int, int]) -> tuple[int, int]:
        capture_x, capture_y = point

        scale_x = self.window.width / self.capture_width
        scale_y = self.window.height / self.capture_height

        return (
            self.window.left + round(capture_x * scale_x),
            self.window.top + round(capture_y * scale_y),
        )
