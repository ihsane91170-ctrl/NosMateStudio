from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from app.calibration.models import CalibrationTarget, RelativePoint
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import StepResult, WorkflowStep
from app.vision.window_detector import GameWindow


class ClickType(StrEnum):
    LEFT = "left"
    DOUBLE = "double"


class MouseExecutor(Protocol):
    def click(self, x: int, y: int) -> None:
        ...

    def double_click(self, x: int, y: int) -> None:
        ...


class ClickAction(WorkflowStep):
    def __init__(
        self,
        target: CalibrationTarget,
        click_type: ClickType = ClickType.LEFT,
        name: str | None = None,
    ) -> None:
        super().__init__(name or f"Cliquer sur {target.value}")
        self.target = target
        self.click_type = click_type

    def execute(self, context: WorkflowContext) -> StepResult:
        mouse: MouseExecutor = context.require_runtime().mouse
        window: GameWindow = context.require("game_window")
        calibration = context.require("calibration")

        point: RelativePoint | None = calibration.points.get(self.target)

        if point is None:
            return StepResult.failed(
                f"La cible {self.target.value} n'est pas calibrée."
            )

        x, y = point.to_absolute(window.left, window.top)

        if self.click_type is ClickType.DOUBLE:
            mouse.double_click(x, y)
        else:
            mouse.click(x, y)

        return StepResult.success(
            f"Clic exécuté sur {self.target.value} en X={x}, Y={y}."
        )