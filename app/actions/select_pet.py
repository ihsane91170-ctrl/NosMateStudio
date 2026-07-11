from __future__ import annotations

from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import (
    StepResult,
    StepResultStatus,
    WorkflowStep,
)
from app.vision.screenshot_provider import WindowScreenshotProvider
from app.vision.template_matcher import TemplateMatcher


class SelectPetAction(WorkflowStep):
    def __init__(
        self,
        template_name: str = "pet_slot",
        threshold: float = 0.80,
    ) -> None:
        self.template_name = template_name
        self.threshold = threshold

    def execute(self, context: WorkflowContext) -> StepResult:
        runtime = context.require("runtime")
        game_window = context.require("game_window")
        screenshot_provider: WindowScreenshotProvider = context.require(
            "screenshot_provider"
        )
        matcher: TemplateMatcher = context.require("template_matcher")

        screenshot = screenshot_provider.capture(game_window)
        match = matcher.find(
            screenshot,
            self.template_name,
            threshold=self.threshold,
        )

        if match is None:
            return StepResult(
                status=StepResultStatus.FAILED,
                message=(
                    f"Template {self.template_name!r} introuvable."
                ),
            )

        screen_x = game_window.left + match.center[0]
        screen_y = game_window.top + match.center[1]

        runtime.mouse.click(screen_x, screen_y)

        return StepResult(
            status=StepResultStatus.SUCCESS,
            message=(
                f"Familier sélectionné en ({screen_x}, {screen_y})."
            ),
        )