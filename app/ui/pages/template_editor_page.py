from __future__ import annotations

from pathlib import Path
from typing import Protocol

from PIL import Image
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets import ImageSelectionWidget
from app.vision.screenshot_provider import (
    PillowScreenshotBackend,
    WindowScreenshotProvider,
)
from app.vision.template_repository import (
    TemplateAlreadyExistsError,
    TemplateRepository,
)
from app.vision.window_detector import GameWindow, WindowDetector


class WindowDetectorProtocol(Protocol):
    def detect(self) -> GameWindow | None:
        ...


class ScreenshotProviderProtocol(Protocol):
    def capture(self, window: GameWindow) -> Image.Image:
        ...


class TemplateEditorPage(QWidget):
    TEMPLATE_DIRECTORY = Path("assets/templates")

    def __init__(
        self,
        window_detector: WindowDetectorProtocol | None = None,
        screenshot_provider: ScreenshotProviderProtocol | None = None,
        template_repository: TemplateRepository | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._window_detector = (
            window_detector or WindowDetector("NosTale")
        )
        self._screenshot_provider = (
            screenshot_provider
            or WindowScreenshotProvider(
                PillowScreenshotBackend()
            )
        )
        self._template_repository = (
            template_repository
            or TemplateRepository(self.TEMPLATE_DIRECTORY)
        )

        title = QLabel("Template Editor")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Capturez la fenêtre NosTale, sélectionnez une zone puis "
            "enregistrez-la comme template."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        self.capture_button = QPushButton("Capturer NosTale")
        self.capture_button.setObjectName("PrimaryButton")
        self.capture_button.clicked.connect(self._capture_window)

        self.status_label = QLabel("Aucune capture chargée.")
        self.status_label.setObjectName("Muted")

        self.image_widget = ImageSelectionWidget()
        self.image_widget.selection_changed.connect(
            self._on_selection_changed
        )

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.image_widget)

        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText(
            "Ex. accompany_button"
        )

        self.save_button = QPushButton("Sauvegarder le template")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save_template)

        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Nom du template"))
        form_layout.addWidget(self.template_name_input, 1)
        form_layout.addWidget(self.save_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.scroll_area, 1)
        layout.addLayout(form_layout)

    def _capture_window(self) -> None:
        window = self._window_detector.detect()

        if window is None:
            self.status_label.setText(
                "Erreur : fenêtre NosTale introuvable."
            )
            return

        try:
            image = self._screenshot_provider.capture(window)
        except (OSError, ValueError) as exc:
            self.status_label.setText(
                f"Erreur pendant la capture : {exc}"
            )
            return

        self.image_widget.set_image(image)
        self.template_name_input.clear()
        self.save_button.setEnabled(False)

        self.status_label.setText(
            f"Capture chargée : {image.width} × {image.height} pixels."
        )

    def _on_selection_changed(self, selection) -> None:
        self.save_button.setEnabled(
            selection is not None and selection.is_valid
        )

        if selection is None:
            return

        self.status_label.setText(
            "Zone sélectionnée : "
            f"{selection.width} × {selection.height} pixels."
        )

    def _save_template(self) -> None:
        name = self.template_name_input.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Nom manquant",
                "Saisissez un nom pour le template.",
            )
            return

        try:
            cropped = self.image_widget.selected_image()
            template = self._template_repository.save(
                name,
                cropped,
            )
        except RuntimeError as exc:
            QMessageBox.warning(
                self,
                "Sélection invalide",
                str(exc),
            )
            return
        except TemplateAlreadyExistsError:
            answer = QMessageBox.question(
                self,
                "Template existant",
                (
                    "Un template porte déjà ce nom. "
                    "Voulez-vous le remplacer ?"
                ),
                (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                ),
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

            template = self._template_repository.save(
                name,
                cropped,
                overwrite=True,
            )
        except ValueError as exc:
            QMessageBox.warning(
                self,
                "Nom invalide",
                str(exc),
            )
            return

        self.status_label.setText(
            f"Template enregistré : {template.path}"
        )
        self.template_name_input.clear()
        self.image_widget.clear_selection()
        self.save_button.setEnabled(False)