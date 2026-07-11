from app.actions.click import ClickAction
from app.actions.press_key import PressKeyAction
from app.actions.wait import WaitAction
from app.calibration.models import CalibrationTarget
from app.configuration.models import Action
from app.workflows.builder import WorkflowBuilder


def test_builder_creates_workflow_steps() -> None:
    steps = (
        WorkflowBuilder()
        .press(Action.PET_STORAGE)
        .wait(0.5)
        .click(CalibrationTarget.PET_ICON_1)
        .double_click(CalibrationTarget.ACCOMPANY_BUTTON)
        .build()
    )

    assert len(steps) == 4

    assert isinstance(steps[0], PressKeyAction)
    assert isinstance(steps[1], WaitAction)
    assert isinstance(steps[2], ClickAction)
    assert isinstance(steps[3], ClickAction)