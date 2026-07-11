from __future__ import annotations

from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import (
    StepResult,
    StepResultStatus,
    WorkflowStep,
)


class SelectPetAndAccompanyAction(WorkflowStep):
    def __init__(
        self,
        pet_template: str = "pet_slot",
        accompany_template: str = "accompany_button",
        threshold: float = 0.80,
        details_delay: float = 0.5,
    ) -> None:
        self.pet_template = pet_template
        self.accompany_template = accompany_template
        self.threshold = threshold
        self.details_delay = details_delay

    def execute(self, context: WorkflowContext) -> StepResult:
        runtime = context.require("runtime")
        game_window = context.require("game_window")
        screenshot_provider = context.require("screenshot_provider")
        matcher = context.require("template_matcher")

        first_screenshot = screenshot_provider.capture(game_window)

        pet_match = matcher.find(
            first_screenshot,
            self.pet_template,
            threshold=self.threshold,
        )

        if pet_match is None:
            return StepResult(
                status=StepResultStatus.FAILED,
                message=(
                    f"Familier introuvable avec le template "
                    f"{self.pet_template!r}."
                ),
            )

        pet_x = game_window.left + pet_match.center[0]
        pet_y = game_window.top + pet_match.center[1]

        runtime.mouse.click(pet_x, pet_y)
        runtime.wait.wait(self.details_delay)

        second_screenshot = screenshot_provider.capture(game_window)

        accompany_match = matcher.find(
            second_screenshot,
            self.accompany_template,
            threshold=self.threshold,
        )

        if accompany_match is None:
            return StepResult(
                status=StepResultStatus.FAILED,
                message=(
                    "Le familier a été sélectionné, mais le bouton "
                    f"{self.accompany_template!r} est introuvable."
                ),
            )

        button_x = game_window.left + accompany_match.center[0]
        button_y = game_window.top + accompany_match.center[1]

        runtime.mouse.click(button_x, button_y)

        return StepResult(
            status=StepResultStatus.SUCCESS,
            message=(
                "Familier sélectionné puis bouton Accompagner cliqué."
            ),
        )