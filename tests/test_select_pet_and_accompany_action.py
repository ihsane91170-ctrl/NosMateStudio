from PIL import Image

from app.actions.select_pet_and_accompany import (
    SelectPetAndAccompanyAction,
)
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResultStatus
from app.vision.match import TemplateMatch
from app.vision.window_detector import GameWindow


class MouseFake:
    def __init__(self) -> None:
        self.clicks: list[tuple[int, int]] = []

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))


class WaitFake:
    def __init__(self) -> None:
        self.delays: list[float] = []

    def wait(self, seconds: float) -> None:
        self.delays.append(seconds)


class RuntimeFake:
    def __init__(self) -> None:
        self.mouse = MouseFake()
        self.wait = WaitFake()


class ScreenshotProviderFake:
    def __init__(self) -> None:
        self.capture_count = 0

    def capture(self, window: GameWindow) -> Image.Image:
        self.capture_count += 1

        return Image.new(
            "RGB",
            (window.width, window.height),
        )


class MatcherFake:
    def __init__(
        self,
        matches: dict[str, TemplateMatch | None],
    ) -> None:
        self.matches = matches
        self.calls: list[str] = []

    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float,
    ) -> TemplateMatch | None:
        self.calls.append(template_name)
        return self.matches.get(template_name)


def build_context(
    runtime: RuntimeFake,
    screenshot_provider: ScreenshotProviderFake,
    matcher: MatcherFake,
) -> WorkflowContext:
    return WorkflowContext(
        data={
            "runtime": runtime,
            "game_window": GameWindow(
                title="NosTale",
                left=400,
                top=200,
                width=1280,
                height=720,
            ),
            "screenshot_provider": screenshot_provider,
            "template_matcher": matcher,
        }
    )


def test_action_selects_pet_then_clicks_accompany() -> None:
    runtime = RuntimeFake()
    screenshot_provider = ScreenshotProviderFake()

    matcher = MatcherFake(
        {
            "pet_slot": TemplateMatch(
                template_name="pet_slot",
                confidence=0.96,
                left=100,
                top=50,
                width=40,
                height=20,
            ),
            "accompany_button": TemplateMatch(
                template_name="accompany_button",
                confidence=0.94,
                left=300,
                top=200,
                width=80,
                height=30,
            ),
        }
    )

    context = build_context(
        runtime,
        screenshot_provider,
        matcher,
    )

    result = SelectPetAndAccompanyAction(
        details_delay=0.5,
    ).execute(context)

    assert result.status is StepResultStatus.SUCCESS

    assert runtime.mouse.clicks == [
        (520, 260),
        (740, 415),
    ]
    assert runtime.wait.delays == [0.5]
    assert screenshot_provider.capture_count == 2
    assert matcher.calls == [
        "pet_slot",
        "accompany_button",
    ]


def test_action_fails_when_pet_is_missing() -> None:
    runtime = RuntimeFake()
    screenshot_provider = ScreenshotProviderFake()
    matcher = MatcherFake(
        {
            "pet_slot": None,
        }
    )

    context = build_context(
        runtime,
        screenshot_provider,
        matcher,
    )

    result = SelectPetAndAccompanyAction().execute(context)

    assert result.status is StepResultStatus.FAILED
    assert runtime.mouse.clicks == []
    assert runtime.wait.delays == []
    assert screenshot_provider.capture_count == 1


def test_action_fails_when_accompany_button_is_missing() -> None:
    runtime = RuntimeFake()
    screenshot_provider = ScreenshotProviderFake()

    matcher = MatcherFake(
        {
            "pet_slot": TemplateMatch(
                template_name="pet_slot",
                confidence=0.96,
                left=100,
                top=50,
                width=40,
                height=20,
            ),
            "accompany_button": None,
        }
    )

    context = build_context(
        runtime,
        screenshot_provider,
        matcher,
    )

    result = SelectPetAndAccompanyAction().execute(context)

    assert result.status is StepResultStatus.FAILED
    assert runtime.mouse.clicks == [
        (520, 260),
    ]
    assert runtime.wait.delays == [0.5]
    assert screenshot_provider.capture_count == 2