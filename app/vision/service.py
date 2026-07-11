from __future__ import annotations

from app.executors.mouse.protocol import MouseExecutor
from app.vision.match import TemplateMatch
from app.vision.screenshot_provider import WindowScreenshotProvider
from app.vision.template_matcher import TemplateMatcher
from app.vision.window_detector import GameWindow


class VisionService:
    def __init__(
        self,
        game_window: GameWindow,
        screenshot_provider: WindowScreenshotProvider,
        matcher: TemplateMatcher,
        mouse: MouseExecutor,
    ) -> None:
        self._game_window = game_window
        self._screenshot_provider = screenshot_provider
        self._matcher = matcher
        self._mouse = mouse

    def capture(self):
        return self._screenshot_provider.capture(
            self._game_window
        )

    def find(
        self,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> TemplateMatch | None:
        screenshot = self.capture()

        return self._matcher.find(
            screenshot,
            template_name,
            threshold=threshold,
        )

    def find_all(
        self,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]:
        screenshot = self.capture()

        return self._matcher.find_all(
            screenshot,
            template_name,
            threshold=threshold,
            minimum_distance=minimum_distance,
        )

    def exists(
        self,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> bool:
        return (
            self.find(
                template_name,
                threshold=threshold,
            )
            is not None
        )

    def click(
        self,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> bool:
        match = self.find(
            template_name,
            threshold=threshold,
        )

        if match is None:
            return False

        screen_x = self._game_window.left + match.center[0]
        screen_y = self._game_window.top + match.center[1]

        self._mouse.click(screen_x, screen_y)

        return True