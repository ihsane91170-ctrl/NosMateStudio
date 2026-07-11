from app.configuration.models import Action
from app.engine.workflow_step import WorkflowStep
from app.workflows.builder import WorkflowBuilder


class FirstRealActionWorkflow:
    @property
    def name(self) -> str:
        return "First Real Action"

    def steps(self) -> list[WorkflowStep]:
        return (
            WorkflowBuilder()
            .press(Action.GO_TO_PET_XP_ZONE)
            .build()
        )