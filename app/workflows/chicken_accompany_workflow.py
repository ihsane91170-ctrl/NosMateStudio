from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_step import (
    StepResult,
    StepResultStatus,
    WorkflowStep,
)
from app.vision.coordinates import CaptureCoordinateMapper
from app.vision.screenshot_provider import (
    PillowScreenshotBackend,
    WindowScreenshotProvider,
)
from app.vision.template_matcher import TemplateMatcher
from app.vision.template_repository import TemplateRepository
from app.vision.window_detector import WindowDetector


class ChickenAccompanyWorkflow(WorkflowStep):
    name = "Chicken Accompany Test"

    def __init__(
        self,
        *,
        chicken_template: str = "pet_chicken_row",
        accompany_template: str = "accompany_button",
        chicken_threshold: float = 0.70,
        accompany_threshold: float = 0.70,
        minimum_distance: int = 10,
        focus_delay: float = 0.35,
        details_delay: float = 1.5,
        click_retries: int = 3,
    ) -> None:
        self.chicken_template = chicken_template
        self.accompany_template = accompany_template
        self.chicken_threshold = chicken_threshold
        self.accompany_threshold = accompany_threshold
        self.minimum_distance = minimum_distance
        self.focus_delay = focus_delay
        self.details_delay = details_delay
        self.click_retries = click_retries

    def steps(self) -> tuple[WorkflowStep, ...]:
        return (self,)

    def execute(self, context: WorkflowContext) -> StepResult:
        runtime = context.require_runtime()
        game_window = context.require("game_window")

        screenshot_provider = WindowScreenshotProvider(
            PillowScreenshotBackend()
        )
        matcher = TemplateMatcher(
            TemplateRepository(Path("assets/templates"))
        )
        window_detector = WindowDetector("NosTale")

        project_root = Path(__file__).resolve().parents[2]
        debug_directory = project_root / "captures"
        debug_directory.mkdir(parents=True, exist_ok=True)

        window_detector.activate()
        runtime.wait.wait(self.focus_delay)

        screenshot = screenshot_provider.capture(game_window)

        initial_capture_path = (
            debug_directory / "chicken_workflow_capture.png"
        )
        screenshot.save(initial_capture_path)

        chickens = matcher.find_all(
            screenshot,
            self.chicken_template,
            threshold=self.chicken_threshold,
            minimum_distance=self.minimum_distance,
        )

        if not chickens:
            return StepResult(
                status=StepResultStatus.FAILED,
                message=(
                    "Aucune poule détectée. "
                    f"Capture enregistrée dans {initial_capture_path}."
                ),
            )

        chicken = chickens[0]

        mapper = CaptureCoordinateMapper(
            window=game_window,
            capture_width=screenshot.width,
            capture_height=screenshot.height,
        )

        # Le template couvre plus que l'icône.
        # On clique donc dans sa partie gauche, au milieu vertical.
        icon_click_point = (
            chicken.left + min(18, chicken.width // 4),
            chicken.top + chicken.height // 2,
        )

        chicken_x, chicken_y = mapper.to_screen(icon_click_point)

        print(
            "[Chicken] "
            f"match=({chicken.left}, {chicken.top}, "
            f"{chicken.width}, {chicken.height}) "
            f"relative_click={icon_click_point} "
            f"screen_click=({chicken_x}, {chicken_y})"
        )

        self._save_click_debug(
            screenshot=screenshot,
            chicken=chicken,
            click_point=icon_click_point,
            path=debug_directory / "chicken_click_position.png",
        )

        accompany = None
        last_capture_path = initial_capture_path

        for attempt in range(1, self.click_retries + 1):
            window_detector.activate()
            runtime.wait.wait(self.focus_delay)

            runtime.mouse.click(chicken_x, chicken_y)
            runtime.wait.wait(self.details_delay)

            screenshot = screenshot_provider.capture(game_window)

            last_capture_path = (
                debug_directory
                / f"chicken_after_click_{attempt}.png"
            )
            screenshot.save(last_capture_path)

            accompany = matcher.find(
                screenshot,
                self.accompany_template,
                threshold=self.accompany_threshold,
            )

            if accompany is not None:
                break

        if accompany is None:
            return StepResult(
                status=StepResultStatus.FAILED,
                message=(
                    "La poule a été cliquée, mais le bouton Accompagner "
                    f"reste introuvable. Dernière capture : "
                    f"{last_capture_path}. Point écran utilisé : "
                    f"({chicken_x}, {chicken_y})."
                ),
            )

        button_mapper = CaptureCoordinateMapper(
            window=game_window,
            capture_width=screenshot.width,
            capture_height=screenshot.height,
        )
        button_x, button_y = button_mapper.to_screen(
            accompany.center
        )

        window_detector.activate()
        runtime.wait.wait(self.focus_delay)

        runtime.mouse.click(button_x, button_y)
        runtime.wait.wait(self.details_delay)

        verification = screenshot_provider.capture(game_window)

        still_visible = matcher.find(
            verification,
            self.accompany_template,
            threshold=self.accompany_threshold,
        )

        verification_path = (
            debug_directory / "chicken_after_accompany.png"
        )
        verification.save(verification_path)

        if still_visible is not None:
            return StepResult(
                status=StepResultStatus.FAILED,
                message=(
                    "Le bouton Accompagner est encore visible après le clic. "
                    f"Capture : {verification_path}."
                ),
            )

        return StepResult(
            status=StepResultStatus.SUCCESS,
            message=(
                "Poule détectée, sélectionnée et accompagnée. "
                f"Clic poule : ({chicken_x}, {chicken_y})."
            ),
        )

    @staticmethod
    def _save_click_debug(
        *,
        screenshot: Image.Image,
        chicken,
        click_point: tuple[int, int],
        path: Path,
    ) -> None:
        annotated = screenshot.convert("RGB").copy()
        draw = ImageDraw.Draw(annotated)

        click_x, click_y = click_point

        draw.rectangle(
            (
                chicken.left,
                chicken.top,
                chicken.right,
                chicken.bottom,
            ),
            outline="red",
            width=3,
        )
        draw.ellipse(
            (
                click_x - 5,
                click_y - 5,
                click_x + 5,
                click_y + 5,
            ),
            fill="lime",
        )

        annotated.save(path)