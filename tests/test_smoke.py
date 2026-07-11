from app import __version__
from app.models.workflow_state import WorkflowState
from app.workflow.session_workflow import SessionWorkflow


def test_version_is_defined() -> None:
    assert __version__ == "0.1.0-alpha"


def test_workflow_starts_idle() -> None:
    workflow = SessionWorkflow()
    assert workflow.state is WorkflowState.IDLE
