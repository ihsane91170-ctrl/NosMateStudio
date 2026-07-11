from PIL import Image

from app.actions.select_pet import SelectPetAction
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResultStatus
from app.vision.match import TemplateMatch
from app.vision.window_detector import GameWindow


class MouseFake:
    def __init__(self) -> None:
        self.clicks: list[tuple[int, int]] = []

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))


class RuntimeFake:
    def __init__(self, mouse: MouseFake) -> None:
        self.mouse = mouse


class ScreenshotProviderFake:
    def capture(self, window: GameWindow) -> Image.Image:
        return Image.new("RGB", (window.width, window.height))


class MatcherFake:
    def __init__(self, match: TemplateMatch | None) -> None:
        self.match = match

    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float,
    ) -> TemplateMatch | None:
        return self.match


def test_select_pet_action_clicks_match_center() -> None:
    mouse = MouseFake()

    context = WorkflowContext(
        data={
            "runtime": RuntimeFake(mouse),
            "game_window": GameWindow(
                title="NosTale",
                left=400,
                top=200,
                width=1280,
                height=720,
            ),
            "screenshot_provider": ScreenshotProviderFake(),
            "template_matcher": MatcherFake(
                TemplateMatch(
                    template_name="pet_slot",
                    confidence=0.95,
                    left=100,
                    top=50,
                    width=40,
                    height=20,
                )
            ),
        }
    )

    result = SelectPetAction().execute(context)

    assert result.status is StepResultStatus.SUCCESS
    assert mouse.clicks == [(520, 260)]


def test_select_pet_action_fails_when_template_is_missing() -> None:
    mouse = MouseFake()

    context = WorkflowContext(
        data={
            "runtime": RuntimeFake(mouse),
            "game_window": GameWindow(
                title="NosTale",
                left=0,
                top=0,
                width=1280,
                height=720,
            ),
            "screenshot_provider": ScreenshotProviderFake(),
            "template_matcher": MatcherFake(None),
        }
    )

    result = SelectPetAction().execute(context)

    assert result.status is StepResultStatus.FAILED
    assert mouse.clicks == []