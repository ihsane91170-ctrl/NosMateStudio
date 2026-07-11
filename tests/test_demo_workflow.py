from app.actions.click import ClickAction
from app.actions.press_key import PressKeyAction
from app.actions.wait import WaitAction
from app.calibration.models import (
    CalibrationProfile,
    CalibrationTarget,
    RelativePoint,
)
from app.configuration.models import (
    Environment,
    Hotkeys,
    Settings,
)
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_engine import WorkflowEngine
from app.engine.workflow_state import WorkflowState
from app.executors.keyboard import SimulationKeyboardExecutor
from app.executors.mouse import MouseEvent, SimulationMouseExecutor
from app.executors.wait import SimulationWaitExecutor, WaitEvent
from app.runtime import AutomationRuntime
from app.vision.window_detector import GameWindow
from app.workflows import DemoWorkflow


def test_demo_workflow_contains_expected_steps() -> None:
    workflow = DemoWorkflow()

    steps = workflow.steps()

    assert len(steps) == 7

    assert isinstance(steps[0], PressKeyAction)
    assert isinstance(steps[1], WaitAction)
    assert isinstance(steps[2], ClickAction)
    assert isinstance(steps[3], WaitAction)
    assert isinstance(steps[4], ClickAction)
    assert isinstance(steps[5], WaitAction)
    assert isinstance(steps[6], PressKeyAction)

def test_demo_workflow_executes_end_to_end_in_simulation() -> None:
    keyboard = SimulationKeyboardExecutor()
    mouse = SimulationMouseExecutor()
    waiter = SimulationWaitExecutor()

    runtime = AutomationRuntime(
        keyboard=keyboard,
        mouse=mouse,
        wait=waiter,
    )

    settings = Settings(
        profile="Default",
        environment=Environment.RECETTE,
        hotkeys=Hotkeys(
            pet_storage="Q",
            capture_new_pet="W",
            xp_map="_",
            summon_weak="1",
            summon_normal="2",
            summon_strong="3",
        ),
    )

    calibration = CalibrationProfile(
        points={
            CalibrationTarget.PET_ICON_1: RelativePoint(100, 50),
            CalibrationTarget.ACCOMPANY_BUTTON: RelativePoint(300, 200),
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
        runtime=runtime,
        data={
            "settings": settings,
            "calibration": calibration,
            "game_window": window,
        },
    )

    workflow = DemoWorkflow()
    engine = WorkflowEngine()

    state = engine.run(workflow.steps(), context)

    assert state is WorkflowState.FINISHED

    assert keyboard.history == ["Q", "_"]

    assert waiter.history == [
        WaitEvent(0.5),
        WaitEvent(0.2),
        WaitEvent(1.0),
    ]

    assert mouse.history == [
        MouseEvent("click", 500, 250),
        MouseEvent("double_click", 700, 400),
    ]

    assert workflow.name == "Demo Workflow"