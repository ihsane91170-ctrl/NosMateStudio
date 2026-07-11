from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL import Image, ImageDraw
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.pets import PetScanner, VisiblePet
from app.ui.widgets import ImageSelectionWidget
from app.vision.match import TemplateMatch
from app.vision.screenshot_provider import (
    PillowScreenshotBackend,
    WindowScreenshotProvider,
)
from app.vision.template_matcher import TemplateMatcher
from app.vision.template_repository import TemplateRepository
from app.vision.window_detector import GameWindow, WindowDetector


class WindowDetectorProtocol(Protocol):
    def detect(self) -> GameWindow | None:
        ...


class ScreenshotProviderProtocol(Protocol):
    def capture(self, window: GameWindow) -> Image.Image:
        ...


class MatcherProtocol(Protocol):
    def find_all(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]:
        ...


class CapturedVisionAdapter:
    """Expose find_all() sur une capture déjà réalisée."""

    def __init__(
        self,
        matcher: MatcherProtocol,
        screenshot: Image.Image,
    ) -> None:
        self._matcher = matcher
        self._screenshot = screenshot

    def find_all(
        self,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]:
        return self._matcher.find_all(
            self._screenshot,
            template_name,
            threshold=threshold,
            minimum_distance=minimum_distance,
        )


class VisionDebugPage(QWidget):
    TEMPLATE_DIRECTORY = Path("assets/templates")

    def __init__(
        self,
        window_detector: WindowDetectorProtocol | None = None,
        screenshot_provider: ScreenshotProviderProtocol | None = None,
        template_repository: TemplateRepository | None = None,
        matcher: MatcherProtocol | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._window_detector = (
            window_detector or WindowDetector("NosTale")
        )
        self._screenshot_provider = (
            screenshot_provider
            or WindowScreenshotProvider(PillowScreenshotBackend())
        )
        self._template_repository = (
            template_repository
            or TemplateRepository(self.TEMPLATE_DIRECTORY)
        )
        self._matcher = (
            matcher
            or TemplateMatcher(self._template_repository)
        )

        title = QLabel("Vision Debug")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Testez la détection des templates sur une capture réelle "
            "de NosTale."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        self.template_selector = QComboBox()

        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setRange(0.01, 1.00)
        self.threshold_input.setSingleStep(0.01)
        self.threshold_input.setDecimals(2)
        self.threshold_input.setValue(0.80)

        self.minimum_distance_input = QSpinBox()
        self.minimum_distance_input.setRange(0, 1000)
        self.minimum_distance_input.setValue(40)

        self.refresh_button = QPushButton("Actualiser les templates")
        self.refresh_button.clicked.connect(self._load_templates)

        self.detect_button = QPushButton("Détecter")
        self.detect_button.setObjectName("PrimaryButton")
        self.detect_button.clicked.connect(self._detect)

        self.scan_pets_button = QPushButton("Scanner les familiers")
        self.scan_pets_button.clicked.connect(self._scan_pets)

        form = QFormLayout()
        form.addRow("Template", self.template_selector)
        form.addRow("Seuil", self.threshold_input)
        form.addRow(
            "Distance minimale",
            self.minimum_distance_input,
        )

        buttons = QHBoxLayout()
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.detect_button)
        buttons.addWidget(self.scan_pets_button)
        buttons.addStretch(1)

        self.status_label = QLabel("Prêt.")
        self.status_label.setObjectName("Muted")

        self.results_list = QListWidget()

        self.image_widget = ImageSelectionWidget()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.image_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.status_label)
        layout.addWidget(self.results_list)
        layout.addWidget(self.scroll_area, 1)

        self._load_templates()

    def _load_templates(self) -> None:
        current_name = self.template_selector.currentText()

        self.template_selector.clear()

        for template in self._template_repository.list():
            self.template_selector.addItem(template.name)

        if current_name:
            self.template_selector.setCurrentText(current_name)

        has_templates = self.template_selector.count() > 0
        self.detect_button.setEnabled(has_templates)
        self.scan_pets_button.setEnabled(
            self.template_selector.findText("pet_row") >= 0
        )

        if not has_templates:
            self.status_label.setText(
                "Aucun template disponible dans assets/templates."
            )

    def _detect(self) -> None:
        template_name = self.template_selector.currentText()

        if not template_name:
            self.status_label.setText(
                "Erreur : aucun template sélectionné."
            )
            return

        window = self._window_detector.detect()

        if window is None:
            self.status_label.setText(
                "Erreur : fenêtre NosTale introuvable."
            )
            return

        try:
            screenshot = self._screenshot_provider.capture(window)
            matches = self._matcher.find_all(
                screenshot,
                template_name,
                threshold=self.threshold_input.value(),
                minimum_distance=self.minimum_distance_input.value(),
            )
        except (OSError, ValueError) as exc:
            self.status_label.setText(
                f"Erreur pendant la détection : {exc}"
            )
            return

        self.image_widget.set_image(
            self._draw_matches(screenshot, matches)
        )
        self._display_results(matches)

        self.status_label.setText(
            f"{len(matches)} détection(s) pour « {template_name} »."
        )

    def _scan_pets(self) -> None:
        window = self._window_detector.detect()

        if window is None:
            self.status_label.setText(
                "Erreur : fenêtre NosTale introuvable."
            )
            return

        try:
            screenshot = self._screenshot_provider.capture(window)

            scanner = PetScanner(
                CapturedVisionAdapter(
                    matcher=self._matcher,
                    screenshot=screenshot,
                ),
                template_name="pet_row",
                threshold=self.threshold_input.value(),
                minimum_distance=self.minimum_distance_input.value(),
            )

            pets = scanner.scan()
        except (OSError, ValueError) as exc:
            self.status_label.setText(
                f"Erreur pendant le scan : {exc}"
            )
            return

        self.image_widget.set_image(
            self._draw_pets(screenshot, pets)
        )
        self._display_pets(pets)

        self.status_label.setText(
            f"{len(pets)} familier(s) visible(s) détecté(s)."
        )

    def _display_results(
        self,
        matches: tuple[TemplateMatch, ...],
    ) -> None:
        self.results_list.clear()

        for index, match in enumerate(matches, start=1):
            center_x, center_y = match.center

            self.results_list.addItem(
                f"{index:02d} — "
                f"x={match.left}, y={match.top}, "
                f"centre=({center_x}, {center_y}), "
                f"confiance={match.confidence:.3f}"
            )

    def _display_pets(
        self,
        pets: tuple[VisiblePet, ...],
    ) -> None:
        self.results_list.clear()

        for pet in pets:
            center_x, center_y = pet.center

            self.results_list.addItem(
                f"Familier #{pet.index:02d} — "
                f"x={pet.left}, y={pet.top}, "
                f"centre=({center_x}, {center_y}), "
                f"confiance={pet.confidence:.3f}"
            )

    @staticmethod
    def _draw_matches(
        screenshot: Image.Image,
        matches: tuple[TemplateMatch, ...],
    ) -> Image.Image:
        annotated = screenshot.convert("RGB").copy()
        painter = ImageDraw.Draw(annotated)

        for index, match in enumerate(matches, start=1):
            painter.rectangle(
                (
                    match.left,
                    match.top,
                    match.right,
                    match.bottom,
                ),
                outline="lime",
                width=3,
            )
            painter.text(
                (match.left, max(0, match.top - 14)),
                f"{index} — {match.confidence:.2f}",
                fill="lime",
            )

        return annotated

    @staticmethod
    def _draw_pets(
        screenshot: Image.Image,
        pets: tuple[VisiblePet, ...],
    ) -> Image.Image:
        annotated = screenshot.convert("RGB").copy()
        painter = ImageDraw.Draw(annotated)

        for pet in pets:
            painter.rectangle(
                (
                    pet.left,
                    pet.top,
                    pet.left + pet.width,
                    pet.top + pet.height,
                ),
                outline="lime",
                width=3,
            )
            painter.text(
                (pet.left, max(0, pet.top - 16)),
                f"Pet #{pet.index}",
                fill="lime",
            )

        return annotated