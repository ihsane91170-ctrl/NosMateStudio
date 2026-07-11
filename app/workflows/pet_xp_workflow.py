from app.configuration.models import Action
from app.engine.workflow_step import WorkflowStep
from app.workflows.builder import WorkflowBuilder


class PetXpWorkflow:
    @property
    def name(self) -> str:
        return "Pet XP Workflow"

    def steps(self) -> list[WorkflowStep]:
        return (
            WorkflowBuilder()
            .press(Action.PET_STORAGE)
            .wait(0.5)
            .press(Action.CAPTURE_NEW_PET)
            .wait(0.5)
            .press(Action.XP_MAP)
            .wait(1.0)
            .press(Action.SUMMON_WEAK)
            .wait(0.5)
            .press(Action.SUMMON_NORMAL)
            .wait(0.5)
            .press(Action.SUMMON_STRONG)
            .build()
        )