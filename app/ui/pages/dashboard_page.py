from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.core.controllers.diagnostic_controller import DiagnosticController


class DashboardPage(QWidget):
    def __init__(
        self,
        version: str,
        diagnostic_controller: DiagnosticController,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._diagnostic_controller = diagnostic_controller

        title = QLabel("Dashboard")
        title.setObjectName("PageTitle")

        self.status_label = QLabel(
            "Surveillance automatique du client NosTale prête."
        )
        self.status_label.setObjectName("Muted")
        self.status_label.setWordWrap(True)

        version_label = QLabel(f"Version {version}")
        version_label.setObjectName("Muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addStretch(1)
        layout.addWidget(version_label)

        diagnostic_controller.diagnostic_updated.connect(
            self._on_diagnostic_updated
        )

    def start_monitoring(self) -> None:
        self._diagnostic_controller.start()

    def stop_monitoring(self) -> None:
        self._diagnostic_controller.stop()

    def _on_diagnostic_updated(self, result: object) -> None:
        message = getattr(result, "message", "Diagnostic actualisé.")
        self.status_label.setText(str(message))