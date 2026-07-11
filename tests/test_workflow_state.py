from app.engine.workflow_state import WorkflowState


def test_workflow_state_values_are_stable() -> None:
    assert WorkflowState.IDLE.value == "idle"
    assert WorkflowState.RUNNING.value == "running"
    assert WorkflowState.ERROR.value == "error"
