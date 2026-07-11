from PIL import Image

from app.vision.service import VisionService
from app.vision.window_detector import GameWindow


class ScreenshotProviderFake:
    def capture(self, window: GameWindow) -> Image.Image:
        return Image.new(
            "RGB",
            (window.width, window.height),
        )


class MatcherFake:
    def __init__(self) -> None:
        self.find_all_calls: list[
            tuple[str, float | None, int]
        ] = []

    def find_all(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None,
        minimum_distance: int,
    ):
        self.find_all_calls.append(
            (
                template_name,
                threshold,
                minimum_distance,
            )
        )
        return ()

    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None,
    ):
        return None


class MouseFake:
    def click(self, x: int, y: int) -> None:
        pass


def test_vision_service_finds_all_templates() -> None:
    matcher = MatcherFake()

    service = VisionService(
        game_window=GameWindow(
            title="NosTale",
            left=100,
            top=200,
            width=1280,
            height=720,
        ),
        screenshot_provider=ScreenshotProviderFake(),
        matcher=matcher,
        mouse=MouseFake(),
    )

    matches = service.find_all(
        "pet_row",
        threshold=0.82,
        minimum_distance=25,
    )

    assert matches == ()
    assert matcher.find_all_calls == [
        (
            "pet_row",
            0.82,
            25,
        )
    ]