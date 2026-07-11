from app.models.workflow_state import WorkflowState


class SessionWorkflow:
    def __init__(self) -> None:
        self.state = WorkflowState.IDLE

    def reset(self) -> None:
        self.state = WorkflowState.IDLE
