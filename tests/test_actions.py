from app.actions.click import ClickAction, ClickType
from app.actions.press_key import PressKeyAction
from app.actions.wait import WaitAction
from app.calibration.models import (
    CalibrationProfile,
    CalibrationTarget,
    RelativePoint,
)
from app.configuration.models import (
    Action,
    Environment,
    Hotkeys,
    Settings,
)
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResultStatus
from app.vision.window_detector import GameWindow


class KeyboardFake:
    def __init__(self) -> None:
        self.keys: list[str] = []

    def press(self, key: str) -> None:
        self.keys.append(key)


class MouseFake:
    def __init__(self) -> None:
        self.clicks: list[tuple[str, int, int]] = []

    def click(self, x: int, y: int) -> None:
        self.clicks.append(("left", x, y))

    def double_click(self, x: int, y: int) -> None:
        self.clicks.append(("double", x, y))


class WaiterFake:
    def __init__(self) -> None:
        self.durations: list[float] = []

    def wait(self, seconds: float) -> None:
        self.durations.append(seconds)


def test_press_key_action_uses_configured_hotkey() -> None:
    keyboard = KeyboardFake()
    settings = Settings(
        profile="Default",
        environment=Environment.RECETTE,
        hotkeys=Hotkeys("Q", "W", "_","1", "2", "3"),
    )
    context = WorkflowContext(
        {
            "keyboard": keyboard,
            "settings": settings,
        }
    )

    result = PressKeyAction(Action.PET_STORAGE).execute(context)

    assert result.status is StepResultStatus.SUCCESS
    assert keyboard.keys == ["Q"]


def test_wait_action_uses_wait_executor() -> None:
    waiter = WaiterFake()
    context = WorkflowContext({"waiter": waiter})

    result = WaitAction(2.5).execute(context)

    assert result.status is StepResultStatus.SUCCESS
    assert waiter.durations == [2.5]


def test_click_action_converts_relative_position() -> None:
    mouse = MouseFake()
    calibration = CalibrationProfile(
        points={
            CalibrationTarget.ACCOMPANY_BUTTON: RelativePoint(100, 50),
        }
    )
    window = GameWindow(
        title="NosTale",
        left=400,
        top=200,
        width=1280,
        height=720,
    )
    context = WorkflowContext(
        {
            "mouse": mouse,
            "calibration": calibration,
            "game_window": window,
        }
    )

    result = ClickAction(
        CalibrationTarget.ACCOMPANY_BUTTON,
        ClickType.DOUBLE,
    ).execute(context)

    assert result.status is StepResultStatus.SUCCESS
    assert mouse.clicks == [("double", 500, 250)]


def test_click_action_fails_when_target_is_not_calibrated() -> None:
    context = WorkflowContext(
        {
            "mouse": MouseFake(),
            "calibration": CalibrationProfile(),
            "game_window": GameWindow(
                title="NosTale",
                left=0,
                top=0,
                width=1280,
                height=720,
            ),
        }
    )

    result = ClickAction(
        CalibrationTarget.ACCOMPANY_BUTTON
    ).execute(context)

    assert result.status is StepResultStatus.FAILED