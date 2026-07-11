from app.actions.press_key import PressKeyAction
from app.actions.wait import WaitAction
from app.workflows import PetXpWorkflow


def test_pet_xp_workflow_definition() -> None:
    workflow = PetXpWorkflow()

    assert workflow.name == "Pet XP Workflow"

    steps = workflow.steps()

    assert len(steps) == 11

    assert isinstance(steps[0], PressKeyAction)
    assert isinstance(steps[1], WaitAction)
    assert isinstance(steps[2], PressKeyAction)
    assert isinstance(steps[3], WaitAction)
    assert isinstance(steps[4], PressKeyAction)
    assert isinstance(steps[5], WaitAction)
    assert isinstance(steps[6], PressKeyAction)
    assert isinstance(steps[7], WaitAction)
    assert isinstance(steps[8], PressKeyAction)
    assert isinstance(steps[9], WaitAction)
    assert isinstance(steps[10], PressKeyAction)