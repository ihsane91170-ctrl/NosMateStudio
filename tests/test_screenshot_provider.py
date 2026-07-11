import pytest
from PIL import Image

from app.vision.screenshot_provider import WindowScreenshotProvider
from app.vision.window_detector import GameWindow


class ScreenshotBackendFake:
    def __init__(self) -> None:
        self.received_bbox: tuple[int, int, int, int] | None = None
        self.image = Image.new("RGB", (1280, 720))

    def grab(
        self,
        bbox: tuple[int, int, int, int],
    ) -> Image.Image:
        self.received_bbox = bbox
        return self.image


def test_provider_captures_exact_window_bounds() -> None:
    backend = ScreenshotBackendFake()
    provider = WindowScreenshotProvider(backend)

    window = GameWindow(
        title="NosTale",
        left=100,
        top=200,
        width=1280,
        height=720,
    )

    image = provider.capture(window)

    assert image is backend.image
    assert backend.received_bbox == (
        100,
        200,
        1380,
        920,
    )


def test_provider_rejects_unusable_window() -> None:
    backend = ScreenshotBackendFake()
    provider = WindowScreenshotProvider(backend)

    window = GameWindow(
        title="NosTale",
        left=0,
        top=0,
        width=0,
        height=720,
    )

    with pytest.raises(ValueError):
        provider.capture(window)