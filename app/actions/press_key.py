from __future__ import annotations

from typing import Protocol

from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResult, WorkflowStep


class KeyboardExecutor(Protocol):
    def press(self, key: str) -> None:
        ...


class PressKeyAction(WorkflowStep):
    def __init__(self, key: str, name: str | None = None) -> None:
        super().__init__(name or f"Appuyer sur {key}")
        self.key = key

    def execute(self, context: WorkflowContext) -> StepResult:
        keyboard: KeyboardExecutor = context.require("keyboard")
        keyboard.press(self.key)

        return StepResult.success(f"Touche {self.key} envoyée.")