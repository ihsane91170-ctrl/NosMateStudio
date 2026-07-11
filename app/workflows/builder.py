from __future__ import annotations

from app.actions.click import ClickAction, ClickType
from app.actions.press_key import PressKeyAction
from app.actions.wait import WaitAction
from app.calibration.models import CalibrationTarget
from app.configuration.models import Action
from app.engine.workflow_step import WorkflowStep


class WorkflowBuilder:
    def __init__(self) -> None:
        self._steps: list[WorkflowStep] = []

    def press(self, action: Action) -> WorkflowBuilder:
        self._steps.append(PressKeyAction(action))
        return self

    def wait(self, seconds: float) -> WorkflowBuilder:
        self._steps.append(WaitAction(seconds))
        return self

    def click(
        self,
        target: CalibrationTarget,
    ) -> WorkflowBuilder:
        self._steps.append(ClickAction(target))
        return self

    def double_click(
        self,
        target: CalibrationTarget,
    ) -> WorkflowBuilder:
        self._steps.append(
            ClickAction(
                target,
                ClickType.DOUBLE,
            )
        )
        return self

    def build(self) -> list[WorkflowStep]:
        return list(self._steps)