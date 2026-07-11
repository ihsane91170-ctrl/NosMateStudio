from __future__ import annotations

from typing import Protocol

from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResult, WorkflowStep


class WaitExecutor(Protocol):
    def wait(self, seconds: float) -> None:
        ...


class WaitAction(WorkflowStep):
    def __init__(self, seconds: float, name: str | None = None) -> None:
        if seconds < 0:
            raise ValueError("La durée d'attente ne peut pas être négative.")

        super().__init__(name or f"Attendre {seconds:g} seconde(s)")
        self.seconds = seconds

    def execute(self, context: WorkflowContext) -> StepResult:
        waiter: WaitExecutor = context.require("waiter")
        waiter.wait(self.seconds)

        return StepResult.success(
            f"Attente de {self.seconds:g} seconde(s) terminée."
        )