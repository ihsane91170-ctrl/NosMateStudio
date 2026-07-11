from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.calibration.models import (
    TARGET_LABELS,
    CalibrationProfile,
    CalibrationTarget,
)
from app.calibration.service import CalibrationCapture
from app.core.controllers.calibration_controller import CalibrationController


class CalibrationPage(QWidget):
    def __init__(
        self,
        controller: CalibrationController,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._position_labels: dict[CalibrationTarget, QLabel] = {}
        self._buttons: dict[CalibrationTarget, QPushButton] = {}
        self._active_target: CalibrationTarget | None = None

        title = QLabel("Calibration")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Apprenez à NosMate Studio où se trouvent les éléments de l'interface. "
            "Les coordonnées sont enregistrées relativement à la fenêtre NosTale."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        card = QFrame()
        card.setObjectName("Card")
        grid = QGridLayout(card)
        grid.setContentsMargins(20, 18, 20, 18)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)

        grid.addWidget(QLabel("Élément"), 0, 0)
        grid.addWidget(QLabel("Position relative"), 0, 1)
        grid.addWidget(QLabel("Action"), 0, 2)

        for row, target in enumerate(CalibrationTarget, start=1):
            name = QLabel(TARGET_LABELS[target])
            position = QLabel("Non calibré")
            position.setObjectName("Muted")
            button = QPushButton("Calibrer")
            button.clicked.connect(
                lambda checked=False, t=target: self._start_capture(t)
            )

            self._position_labels[target] = position
            self._buttons[target] = button

            grid.addWidget(name, row, 0)
            grid.addWidget(position, row, 1)
            grid.addWidget(button, row, 2)

        self.status = QLabel("Calibration non chargée.")
        self.status.setWordWrap(True)

        self.progress = QLabel("0 / 7 éléments calibrés")
        self.progress.setObjectName("Muted")

        self.reset_button = QPushButton("Réinitialiser la calibration")
        self.reset_button.clicked.connect(self._confirm_reset)

        actions = QHBoxLayout()
        actions.addWidget(self.progress)
        actions.addStretch(1)
        actions.addWidget(self.reset_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(card)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch(1)

        controller.profile_loaded.connect(self._apply_profile)
        controller.countdown_changed.connect(self._show_countdown)
        controller.capture_succeeded.connect(self._on_capture_succeeded)
        controller.capture_failed.connect(self._on_capture_failed)
        controller.reset_succeeded.connect(self._on_reset)

        controller.load()

    def _start_capture(self, target: CalibrationTarget) -> None:
        self._active_target = target
        self._set_buttons_enabled(False)
        self.status.setText(
            f"Placez la souris sur « {TARGET_LABELS[target]} » dans NosTale."
        )
        self._controller.start_capture(target.value)

    def _show_countdown(self, remaining: int) -> None:
        if self._active_target is None:
            return
        self.status.setText(
            f"Calibration de « {TARGET_LABELS[self._active_target]} » "
            f"dans {remaining} seconde(s)…"
        )

    def _on_capture_succeeded(self, capture: CalibrationCapture) -> None:
        target = capture.target
        point = capture.relative_point
        self._position_labels[target].setText(f"X={point.x}, Y={point.y}")
        self.status.setText(
            f"« {TARGET_LABELS[target]} » calibré avec succès."
        )
        self._active_target = None
        self._set_buttons_enabled(True)
        self._controller.load()

    def _on_capture_failed(self, message: str) -> None:
        self._active_target = None
        self._set_buttons_enabled(True)
        self.status.setText(message)
        QMessageBox.warning(self, "Calibration impossible", message)

    def _apply_profile(self, profile: CalibrationProfile) -> None:
        for target in CalibrationTarget:
            point = profile.points.get(target)
            text = f"X={point.x}, Y={point.y}" if point else "Non calibré"
            self._position_labels[target].setText(text)

        done, total = profile.completion()
        self.progress.setText(f"{done} / {total} éléments calibrés")

        if profile.is_complete():
            self.status.setText("Calibration complète.")
        elif done:
            self.status.setText("Calibration partielle.")
        else:
            self.status.setText("Aucun élément calibré.")

    def _confirm_reset(self) -> None:
        answer = QMessageBox.question(
            self,
            "Réinitialiser la calibration",
            "Supprimer toutes les positions enregistrées ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer is QMessageBox.StandardButton.Yes:
            self._controller.reset()

    def _on_reset(self, profile: CalibrationProfile) -> None:
        self._apply_profile(profile)
        self.status.setText("Calibration réinitialisée.")

    def _set_buttons_enabled(self, enabled: bool) -> None:
        for button in self._buttons.values():
            button.setEnabled(enabled)
        self.reset_button.setEnabled(enabled)
