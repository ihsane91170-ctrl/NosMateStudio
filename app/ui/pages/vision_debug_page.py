from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime
from typing import Protocol

from PIL import Image, ImageDraw
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
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

from app.executors.mouse.pyautogui_executor import PyAutoGUIMouseExecutor
from app.automation.action_engine import ActionEngine
from app.automation.input_controller import InputController
from app.combat.target_attack import AttackConfig, TargetAttackService
from app.combat.chicken_capture import (
    CaptureOutcome,
    ChickenCaptureConfig,
    ChickenCaptureService,
)
from app.vision.hp_state_reader import HpStateReader
from app.vision.hp_diagnostic import HpDiagnosticExporter
from app.pets import PetScanner, VisiblePet
from app.vision.chicken_detector import (
    ChickenCandidate,
    ChickenDetectionReport,
    ChickenDetector,
)
from app.vision.chicken_selector import ChickenSelector
from app.vision.ai_detector import (
    ModelNotAvailableError,
    ObjectDetection,
    UltralyticsObjectDetector,
)
from app.vision.ai_target_selector import AITargetSelector, RankedTarget
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
    def find_best(
        self,
        screenshot: Image.Image,
        template_name: str,
    ) -> TemplateMatch:
        ...

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
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    TEMPLATE_DIRECTORY = PROJECT_ROOT / "assets" / "templates"

    def __init__(
        self,
        window_detector: WindowDetectorProtocol | None = None,
        screenshot_provider: ScreenshotProviderProtocol | None = None,
        template_repository: TemplateRepository | None = None,
        matcher: MatcherProtocol | None = None,
        mouse_executor=None,
        ai_detector=None,
        ai_target_selector=None,
        chicken_capture_service=None,
        hp_state_reader=None,
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
        self._mouse_executor = mouse_executor or PyAutoGUIMouseExecutor(enabled=True)
        self._keyboard_controller = InputController(simulation_mode=False)
        self._action_engine = ActionEngine(
            self._mouse_executor, self._keyboard_controller
        )
        self._target_attack_service = TargetAttackService(self._action_engine)
        self._hp_state_reader = hp_state_reader or HpStateReader()
        self._hp_diagnostic_exporter = HpDiagnosticExporter(
            self._hp_state_reader, self.PROJECT_ROOT / "vision_logs"
        )
        self._chicken_capture_service = (
            chicken_capture_service
            or ChickenCaptureService(self._action_engine, self._hp_state_reader)
        )
        self._chicken_selector = ChickenSelector()
        self._ai_detector = ai_detector or UltralyticsObjectDetector(
            self.PROJECT_ROOT / "assets" / "models" / "chicken_detector.pt"
        )
        self._ai_target_selector = ai_target_selector or AITargetSelector()
        self._last_ai_detections: tuple[ObjectDetection, ...] = ()
        self._last_ai_selection: RankedTarget | None = None
        self._chicken_detector = ChickenDetector(self._matcher)
        self._last_chicken_report = ChickenDetectionReport((), (), ())
        self._last_chicken_matches: tuple[TemplateMatch, ...] = ()
        self._last_window: GameWindow | None = None
        self._last_screenshot: Image.Image | None = None

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

        self.negative_threshold_input = QDoubleSpinBox()
        self.negative_threshold_input.setRange(0.01, 1.00)
        self.negative_threshold_input.setSingleStep(0.01)
        self.negative_threshold_input.setDecimals(2)
        self.negative_threshold_input.setValue(0.45)

        self.minimum_margin_input = QDoubleSpinBox()
        self.minimum_margin_input.setRange(0.00, 1.00)
        self.minimum_margin_input.setSingleStep(0.01)
        self.minimum_margin_input.setDecimals(2)
        self.minimum_margin_input.setValue(0.12)

        self.refresh_button = QPushButton("Actualiser les templates")
        self.refresh_button.clicked.connect(self._load_templates)

        self.detect_button = QPushButton("Détecter")
        self.detect_button.setObjectName("PrimaryButton")
        self.detect_button.clicked.connect(self._detect)

        self.scan_pets_button = QPushButton("Scanner les familiers")
        self.scan_pets_button.clicked.connect(self._scan_pets)

        self.detect_chickens_button = QPushButton("Détecter les poules (templates)")
        self.detect_chickens_button.clicked.connect(self._detect_chickens)

        self.detect_ai_button = QPushButton("Détecter par IA")
        self.detect_ai_button.setObjectName("PrimaryButton")
        self.detect_ai_button.clicked.connect(self._detect_with_ai)

        self.arm_real_click = QCheckBox("Armer le clic réel")
        self.select_chicken_button = QPushButton("Sélectionner la meilleure poule")
        self.select_chicken_button.setEnabled(False)
        self.select_chicken_button.clicked.connect(self._select_best_chicken)

        self.attack_attempts_input = QSpinBox()
        self.attack_attempts_input.setRange(1, 5)
        self.attack_attempts_input.setValue(2)

        self.selection_delay_input = QDoubleSpinBox()
        self.selection_delay_input.setRange(0.00, 5.00)
        self.selection_delay_input.setSingleStep(0.10)
        self.selection_delay_input.setDecimals(2)
        self.selection_delay_input.setValue(0.40)
        self.selection_delay_input.setSuffix(" s")

        self.attack_retry_delay_input = QDoubleSpinBox()
        self.attack_retry_delay_input.setRange(0.00, 5.00)
        self.attack_retry_delay_input.setSingleStep(0.10)
        self.attack_retry_delay_input.setDecimals(2)
        self.attack_retry_delay_input.setValue(0.70)
        self.attack_retry_delay_input.setSuffix(" s")

        self.attack_chicken_button = QPushButton("Sélectionner et attaquer (ESPACE)")
        self.attack_chicken_button.setEnabled(False)
        self.attack_chicken_button.clicked.connect(self._select_and_attack_best_chicken)

        self.capture_max_attacks_input = QSpinBox()
        self.capture_max_attacks_input.setRange(1, 8)
        self.capture_max_attacks_input.setValue(3)

        self.hp_update_delay_input = QDoubleSpinBox()
        self.hp_update_delay_input.setRange(0.10, 5.00)
        self.hp_update_delay_input.setSingleStep(0.10)
        self.hp_update_delay_input.setDecimals(2)
        self.hp_update_delay_input.setValue(0.80)
        self.hp_update_delay_input.setSuffix(" s")

        self.hp_confirmation_reads_input = QSpinBox()
        self.hp_confirmation_reads_input.setRange(1, 3)
        self.hp_confirmation_reads_input.setValue(2)

        self.capture_chicken_button = QPushButton("Attaquer puis capturer à 1 PV (&)")
        self.capture_chicken_button.setEnabled(False)
        self.capture_chicken_button.clicked.connect(
            self._select_attack_and_capture_best_chicken
        )

        self.diagnose_hp_button = QPushButton("Diagnostiquer les PV")
        self.diagnose_hp_button.clicked.connect(self._diagnose_hp)

        self.export_diagnostic_button = QPushButton("Exporter le diagnostic")
        self.export_diagnostic_button.setEnabled(False)
        self.export_diagnostic_button.clicked.connect(self._export_chicken_diagnostic)

        form = QFormLayout()
        form.addRow("Template", self.template_selector)
        form.addRow("Seuil", self.threshold_input)
        form.addRow(
            "Distance minimale",
            self.minimum_distance_input,
        )
        form.addRow("Seuil autre monstre", self.negative_threshold_input)
        form.addRow("Marge minimale", self.minimum_margin_input)
        form.addRow("Tentatives d'attaque max", self.attack_attempts_input)
        form.addRow("Délai sélection → attaque", self.selection_delay_input)
        form.addRow("Délai entre tentatives", self.attack_retry_delay_input)
        form.addRow("Attaques max avant capture", self.capture_max_attacks_input)
        form.addRow("Délai attaque → lecture PV", self.hp_update_delay_input)
        form.addRow("Confirmations de 1 PV", self.hp_confirmation_reads_input)

        buttons = QHBoxLayout()
        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.detect_button)
        buttons.addWidget(self.scan_pets_button)
        buttons.addWidget(self.detect_chickens_button)
        buttons.addWidget(self.detect_ai_button)
        buttons.addWidget(self.arm_real_click)
        buttons.addWidget(self.select_chicken_button)
        buttons.addWidget(self.attack_chicken_button)
        buttons.addWidget(self.capture_chicken_button)
        buttons.addWidget(self.diagnose_hp_button)
        buttons.addWidget(self.export_diagnostic_button)
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
        # Toujours laisser le bouton actif afin de fournir un diagnostic
        # explicite lorsque le template chicken est absent.
        self.detect_chickens_button.setEnabled(True)

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


    def _detect_chickens(self) -> None:
        self.select_chicken_button.setEnabled(False)
        self.export_diagnostic_button.setEnabled(False)
        self.results_list.clear()
        self.status_label.setText("Détection multi-templates en cours…")
        QApplication.processEvents()

        self._load_templates()
        template_names = tuple(
            template.name for template in self._template_repository.list()
        )
        positive_names, negative_names = ChickenDetector.classify_template_names(
            template_names
        )
        if not positive_names:
            self.status_label.setText(
                "Aucun template poule. Créez chicken.png ou chicken_01.png, "
                "chicken_02.png, etc."
            )
            return

        window = self._window_detector.detect()
        if window is None:
            self.status_label.setText("Erreur : fenêtre NosTale introuvable.")
            return

        try:
            screenshot = self._screenshot_provider.capture(window)
            report = self._chicken_detector.detect(
                screenshot,
                template_names=template_names,
                threshold=self.threshold_input.value(),
                negative_threshold=self.negative_threshold_input.value(),
                minimum_margin=self.minimum_margin_input.value(),
                minimum_distance=self.minimum_distance_input.value(),
                require_negative_templates=True,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Erreur pendant la détection des poules : "
                f"{type(exc).__name__}: {exc}"
            )
            return

        self._last_window = window
        self._last_screenshot = screenshot.copy()
        self._last_chicken_report = report
        self._last_chicken_matches = tuple(
            candidate.match for candidate in report.accepted
        )
        selected = self._chicken_selector.choose(
            self._last_chicken_matches, window
        )
        self.image_widget.set_image(
            self._draw_chicken_candidates(screenshot, report.candidates)
        )
        self._display_chicken_candidates(report.candidates)
        self.select_chicken_button.setEnabled(selected is not None)
        self.export_diagnostic_button.setEnabled(True)

        warning = ""
        if not negative_names:
            warning = (
                " Aucun template not_chicken : mode diagnostic uniquement, "
                "aucun clic autorisé."
            )

        # Compatibilité avec le diagnostic S3 : lorsque rien ne dépasse le seuil,
        # afficher tout de même la meilleure correspondance au lieu d'un simple 0.
        if not report.candidates:
            best_matches: list[TemplateMatch] = []
            for template_name in positive_names:
                try:
                    best_matches.append(
                        self._matcher.find_best(screenshot, template_name)
                    )
                except Exception:
                    continue
            if best_matches:
                best = max(best_matches, key=lambda match: match.confidence)
                center_x, center_y = best.center
                self.image_widget.set_image(
                    self._draw_diagnostic_match(screenshot, best)
                )
                self._display_results((best,))
                self.status_label.setText(
                    "0 poule(s) détectée(s). "
                    f"Meilleur score={best.confidence:.3f}, "
                    f"seuil={self.threshold_input.value():.3f}, "
                    f"position=({center_x}, {center_y})." + warning
                )
                return

        # Conserver le libellé historique attendu par les tests et les utilisateurs,
        # tout en ajoutant les informations de confirmation/refus propres à S4.
        self.status_label.setText(
            f"{len(report.accepted)} poule(s) détectée(s) et confirmée(s), "
            f"{len(report.ambiguous)} candidate(s) refusée(s)." + warning
        )


    def _detect_with_ai(self) -> None:
        self.select_chicken_button.setEnabled(False)
        self.attack_chicken_button.setEnabled(False)
        self.results_list.clear()
        self.status_label.setText("Détection IA en cours…")
        QApplication.processEvents()

        window = self._window_detector.detect()
        if window is None:
            self.status_label.setText("Erreur : fenêtre NosTale introuvable.")
            return

        try:
            screenshot = self._screenshot_provider.capture(window)
            detections = self._ai_detector.detect(
                screenshot, confidence=self.threshold_input.value()
            )
        except ModelNotAvailableError as exc:
            self.status_label.setText(str(exc))
            return
        except Exception as exc:
            self.status_label.setText(
                f"Erreur pendant la détection IA : {type(exc).__name__}: {exc}"
            )
            return

        ranked = self._ai_target_selector.rank(
            detections,
            image_width=screenshot.width,
            image_height=screenshot.height,
        )
        selected = ranked[0] if ranked else None
        chickens = tuple(d for d in detections if d.class_name == "chicken")

        self._last_window = window
        self._last_screenshot = screenshot.copy()
        self._last_ai_detections = detections
        self._last_ai_selection = selected
        # Une détection IA invalide les anciennes candidates templates.
        self._last_chicken_matches = ()

        self.image_widget.set_image(
            self._draw_ai_detections(screenshot, detections, selected)
        )
        ranking_by_detection = {id(item.detection): item for item in ranked}
        for index, detection in enumerate(detections, start=1):
            ranking = ranking_by_detection.get(id(detection))
            suffix = ""
            if ranking is not None:
                marker = " — MEILLEURE CIBLE" if ranking is selected else ""
                suffix = (
                    f" — score={ranking.score:.3f}"
                    f" (conf={ranking.confidence_score:.3f}, centre={ranking.center_score:.3f})"
                    f"{marker}"
                )
            self.results_list.addItem(
                f"{index:02d} — {detection.class_name} — "
                f"confiance={detection.confidence:.3f} — centre={detection.center}"
                f"{suffix}"
            )

        self.select_chicken_button.setEnabled(selected is not None)
        self.attack_chicken_button.setEnabled(selected is not None)
        self.capture_chicken_button.setEnabled(selected is not None)
        selected_text = (
            f" Meilleure cible : centre={selected.detection.center}, "
            f"score={selected.score:.3f}."
            if selected is not None
            else " Aucune poule sélectionnable."
        )
        self.status_label.setText(
            f"IA : {len(chickens)} poule(s), "
            f"{len(detections) - len(chickens)} autre(s) objet(s)."
            + selected_text
        )

    @staticmethod
    def _draw_ai_detections(
        screenshot: Image.Image,
        detections: tuple[ObjectDetection, ...],
        selected: RankedTarget | None = None,
    ) -> Image.Image:
        annotated = screenshot.convert("RGB").copy()
        painter = ImageDraw.Draw(annotated)
        selected_detection = selected.detection if selected is not None else None
        for detection in detections:
            is_selected = detection is selected_detection
            color = "yellow" if is_selected else (
                "lime" if detection.class_name == "chicken" else "red"
            )
            width = 5 if is_selected else 3
            painter.rectangle(
                (detection.left, detection.top, detection.right, detection.bottom),
                outline=color,
                width=width,
            )
            prefix = "CIBLE " if is_selected else ""
            painter.text(
                (detection.left, max(0, detection.top - 16)),
                f"{prefix}{detection.class_name} {detection.confidence:.2f}",
                fill=color,
            )
        return annotated

    def _export_chicken_diagnostic(self) -> None:
        screenshot = self._last_screenshot
        if screenshot is None:
            self.status_label.setText(
                "Aucun diagnostic à exporter : lancez d'abord la détection."
            )
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        directory = self.PROJECT_ROOT / "vision_logs" / f"chicken_{timestamp}"
        directory.mkdir(parents=True, exist_ok=True)

        screenshot.save(directory / "capture_originale.png")
        self._draw_chicken_candidates(
            screenshot, self._last_chicken_report.candidates
        ).save(directory / "capture_annotee.png")

        templates = [
            template.name for template in self._template_repository.list()
        ]
        payload = {
            "templates_charges": templates,
            "seuil_poule": self.threshold_input.value(),
            "seuil_autre": self.negative_threshold_input.value(),
            "marge_minimale": self.minimum_margin_input.value(),
            "candidates": [
                {
                    "template": candidate.match.template_name,
                    "position": [candidate.match.left, candidate.match.top],
                    "taille": [candidate.match.width, candidate.match.height],
                    "score_poule": candidate.chicken_score,
                    "score_autre": candidate.other_monster_score,
                    "marge": candidate.margin,
                    "acceptee": candidate.accepted,
                    "raison": candidate.reason,
                }
                for candidate in self._last_chicken_report.candidates
            ],
        }
        (directory / "diagnostic.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.status_label.setText(
            f"Diagnostic exporté dans {directory}."
        )

    def _select_best_chicken(self) -> None:
        if not self.arm_real_click.isChecked():
            self.status_label.setText(
                "Clic bloqué : cochez « Armer le clic réel » avant de sélectionner."
            )
            return

        # Priorité au moteur IA lorsqu'une détection IA a été effectuée.
        if self._last_ai_selection is not None:
            window = self._window_detector.detect()
            if window is None:
                self.status_label.setText("Erreur : fenêtre NosTale introuvable.")
                return

            try:
                fresh_screenshot = self._screenshot_provider.capture(window)
                fresh_detections = self._ai_detector.detect(
                    fresh_screenshot, confidence=self.threshold_input.value()
                )
                fresh_selection = self._ai_target_selector.choose(
                    fresh_detections,
                    image_width=fresh_screenshot.width,
                    image_height=fresh_screenshot.height,
                )
            except Exception as exc:
                self.status_label.setText(
                    f"Clic annulé : impossible de revalider la cible IA "
                    f"({type(exc).__name__}: {exc})."
                )
                return

            if fresh_selection is None:
                self.status_label.setText(
                    "Clic annulé : aucune poule détectée lors de la revalidation."
                )
                self.select_chicken_button.setEnabled(False)
                self._last_ai_selection = None
                return

            detection = fresh_selection.detection
            local_x, local_y = detection.center
            screen_x = window.left + local_x
            screen_y = window.top + local_y
            try:
                self._mouse_executor.click(screen_x, screen_y)
            except Exception as exc:
                self.status_label.setText(f"Erreur pendant le clic IA : {exc}")
                return

            self._last_window = window
            self._last_screenshot = fresh_screenshot.copy()
            self._last_ai_detections = fresh_detections
            self._last_ai_selection = fresh_selection
            self.image_widget.set_image(
                self._draw_ai_detections(
                    fresh_screenshot, fresh_detections, fresh_selection
                )
            )
            self.status_label.setText(
                f"Clic IA envoyé en ({screen_x}, {screen_y}) sur une poule "
                f"(confiance={detection.confidence:.3f}, "
                f"score={fresh_selection.score:.3f}). "
                "Vérifiez dans NosTale que la bonne cible est sélectionnée."
            )
            return

        # Compatibilité avec l'ancien moteur templates.
        window = self._last_window
        selected = (
            self._chicken_selector.choose(self._last_chicken_matches, window)
            if window is not None
            else None
        )
        if window is None or selected is None:
            self.status_label.setText(
                "Aucune candidate disponible : lancez d'abord une détection IA "
                "ou une détection par templates."
            )
            return

        screen_x, screen_y = self._chicken_selector.to_screen_coordinates(
            selected, window
        )
        try:
            self._mouse_executor.click(screen_x, screen_y)
        except Exception as exc:
            self.status_label.setText(f"Erreur pendant le clic : {exc}")
            return

        self.status_label.setText(
            f"Clic envoyé sur la candidate template en ({screen_x}, {screen_y}). "
            "Vérifiez dans NosTale que la bonne cible est sélectionnée."
        )

    def _select_and_attack_best_chicken(self) -> None:
        if not self.arm_real_click.isChecked():
            self.status_label.setText(
                "Attaque bloquée : cochez « Armer le clic réel »."
            )
            return

        window = self._window_detector.detect()
        if window is None:
            self.status_label.setText("Erreur : fenêtre NosTale introuvable.")
            return

        try:
            screenshot = self._screenshot_provider.capture(window)
            detections = self._ai_detector.detect(
                screenshot, confidence=self.threshold_input.value()
            )
            selected = self._ai_target_selector.choose(
                detections,
                image_width=screenshot.width,
                image_height=screenshot.height,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Attaque annulée pendant la revalidation IA : "
                f"{type(exc).__name__}: {exc}"
            )
            return

        if selected is None:
            self.status_label.setText(
                "Attaque annulée : aucune poule détectée lors de la revalidation."
            )
            self.attack_chicken_button.setEnabled(False)
            self.capture_chicken_button.setEnabled(False)
            return

        local_x, local_y = selected.detection.center
        screen_x = window.left + local_x
        screen_y = window.top + local_y
        config = AttackConfig(
            max_attempts=self.attack_attempts_input.value(),
            selection_delay_seconds=self.selection_delay_input.value(),
            retry_delay_seconds=self.attack_retry_delay_input.value(),
        )

        try:
            result = self._target_attack_service.execute(
                x=screen_x, y=screen_y, config=config
            )
        except Exception as exc:
            self.status_label.setText(f"Erreur pendant l'attaque : {exc}")
            return

        sequence = " → ".join(attempt.value for attempt in result.attempts)
        self.status_label.setText(
            f"Séquence terminée sur ({screen_x}, {screen_y}) : {sequence}. "
            "Aucune touche de capture n'a été envoyée."
        )


    def _diagnose_hp(self) -> None:
        window = self._window_detector.detect()
        if window is None:
            self.status_label.setText("Diagnostic PV impossible : fenêtre NosTale introuvable.")
            return

        try:
            screenshot = self._screenshot_provider.capture(window)
            diagnostic = self._hp_diagnostic_exporter.export(screenshot)
        except Exception as exc:
            self.status_label.setText(
                f"Diagnostic PV impossible : {type(exc).__name__}: {exc}"
            )
            return

        self._last_window = window
        self._last_screenshot = screenshot
        self.image_widget.set_image(Image.open(diagnostic.annotated_path))
        result = diagnostic.result
        box = result.hp_box if result.hp_box is not None else "introuvable"
        self.status_label.setText(
            f"Diagnostic PV : {result.state.value} — vert={result.green_ratio:.4f} — "
            f"rouge={result.red_ratio:.4f} — zone={box}. Export : {diagnostic.directory}"
        )

    def _select_attack_and_capture_best_chicken(self) -> None:
        if not self.arm_real_click.isChecked():
            self.status_label.setText(
                "Capture bloquée : cochez « Armer le clic réel »."
            )
            return

        window = self._window_detector.detect()
        if window is None:
            self.status_label.setText("Erreur : fenêtre NosTale introuvable.")
            return

        try:
            screenshot = self._screenshot_provider.capture(window)
            detections = self._ai_detector.detect(
                screenshot, confidence=self.threshold_input.value()
            )
            selected = self._ai_target_selector.choose(
                detections,
                image_width=screenshot.width,
                image_height=screenshot.height,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Capture annulée pendant la revalidation IA : "
                f"{type(exc).__name__}: {exc}"
            )
            return

        if selected is None:
            self.status_label.setText(
                "Capture annulée : aucune poule détectée lors de la revalidation."
            )
            self.capture_chicken_button.setEnabled(False)
            return

        local_x, local_y = selected.detection.center
        screen_x = window.left + local_x
        screen_y = window.top + local_y
        config = ChickenCaptureConfig(
            max_attacks=self.capture_max_attacks_input.value(),
            selection_delay_seconds=self.selection_delay_input.value(),
            hp_update_delay_seconds=self.hp_update_delay_input.value(),
            confirmation_reads=self.hp_confirmation_reads_input.value(),
        )

        def capture_image() -> Image.Image:
            fresh_window = self._window_detector.detect()
            if fresh_window is None:
                raise RuntimeError("Fenêtre NosTale perdue pendant la lecture des PV.")
            return self._screenshot_provider.capture(fresh_window)

        try:
            result = self._chicken_capture_service.execute(
                x=screen_x,
                y=screen_y,
                capture_image=capture_image,
                config=config,
            )
        except Exception as exc:
            self.status_label.setText(f"Erreur pendant attaque/capture : {exc}")
            return

        states = " → ".join(read.state.value for read in result.hp_reads) or "aucune lecture"
        if result.outcome is CaptureOutcome.CAPTURE_SENT:
            message = (
                f"Capture confirmée après {result.attacks_sent} attaque(s) et "
                f"{result.capture_attempts} tentative(s) de capture. PV : {states}."
            )
        elif result.outcome is CaptureOutcome.MAX_ATTACKS_REACHED:
            message = (
                f"Capture non envoyée : PV restés à 156 après "
                f"{result.attacks_sent} attaque(s). PV : {states}."
            )
        elif result.outcome is CaptureOutcome.MAX_CAPTURE_ATTEMPTS_REACHED:
            message = (
                f"Capture échouée après {result.capture_attempts} tentative(s), "
                f"sans nouvelle attaque. PV : {states}."
            )
        else:
            message = (
                f"Capture bloquée : état des PV incertain après "
                f"{result.attacks_sent} attaque(s). PV : {states}."
            )
        self.status_label.setText(message)

    def _display_chicken_candidates(
        self, candidates: tuple[ChickenCandidate, ...]
    ) -> None:
        self.results_list.clear()
        for index, candidate in enumerate(candidates, start=1):
            x, y = candidate.center
            decision = "ACCEPTÉE" if candidate.accepted else "REFUSÉE"
            self.results_list.addItem(
                f"{index:02d} — {decision} — centre=({x}, {y}) — "
                f"poule={candidate.chicken_score:.3f} — "
                f"autre={candidate.other_monster_score:.3f} — "
                f"marge={candidate.margin:.3f} — {candidate.reason}"
            )

    @staticmethod
    def _draw_chicken_candidates(
        screenshot: Image.Image,
        candidates: tuple[ChickenCandidate, ...],
    ) -> Image.Image:
        annotated = screenshot.convert("RGB").copy()
        painter = ImageDraw.Draw(annotated)
        for index, candidate in enumerate(candidates, start=1):
            match = candidate.match
            color = "lime" if candidate.accepted else "red"
            painter.rectangle(
                (match.left, match.top, match.right, match.bottom),
                outline=color,
                width=3,
            )
            painter.text(
                (match.left, max(0, match.top - 16)),
                f"{index} P:{candidate.chicken_score:.2f} "
                f"N:{candidate.other_monster_score:.2f}",
                fill=color,
            )
        return annotated

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
    def _draw_diagnostic_match(
        screenshot: Image.Image,
        match: TemplateMatch,
    ) -> Image.Image:
        """Dessine la meilleure ressemblance sans la présenter comme validée."""
        annotated = screenshot.convert("RGB").copy()
        painter = ImageDraw.Draw(annotated)
        painter.rectangle(
            (match.left, match.top, match.right, match.bottom),
            outline="red",
            width=3,
        )
        painter.text(
            (match.left, max(0, match.top - 14)),
            f"DIAGNOSTIC — {match.confidence:.2f}",
            fill="red",
        )
        return annotated

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