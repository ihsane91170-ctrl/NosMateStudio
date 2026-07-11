from __future__ import annotations

from app.configuration.models import Action, Settings
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResult, WorkflowStep
from app.executors.keyboard.protocol import KeyboardExecutor


class PressKeyAction(WorkflowStep):
    def __init__(
        self,
        action: Action,
        name: str | None = None,
    ) -> None:
        super().__init__(name or f"Exécuter {action.value}")
        self.action = action

    def execute(self, context: WorkflowContext) -> StepResult:
        keyboard: KeyboardExecutor = context.require("keyboard")
        settings: Settings = context.require("settings")

        key = settings.hotkeys.get(self.action)
        keyboard.press(key)

        return StepResult.success(
            f"Action {self.action.value} exécutée avec la touche {key}."
        )