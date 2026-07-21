from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app import __version__
from app.calibration.repository import JsonCalibrationRepository
from app.calibration.service import CalibrationService
from app.configuration.repository import JsonSettingsRepository
from app.configuration.service import SettingsService
from app.core.controllers.calibration_controller import CalibrationController
from app.core.controllers.diagnostic_controller import DiagnosticController
from app.core.controllers.settings_controller import SettingsController
from app.services.game_diagnostic_service import GameDiagnosticService
from app.ui.pages.calibration_page import CalibrationPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.logs_page import LogsPage
from app.ui.pages.production_planner_page import ProductionPlannerPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.template_editor_page import TemplateEditorPage
from app.ui.pages.vision_debug_page import VisionDebugPage
from app.ui.pages.workflow_page import WorkflowPage
from app.ui.theme import build_stylesheet
from app.vision.window_detector import WindowDetector


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"NosMate Studio — {__version__}")
        self.resize(1120, 720)
        self.setMinimumSize(960, 620)
        self.setStyleSheet(build_stylesheet())

        title_filter = "NosTale"

        window_detector = WindowDetector(title_filter)

        diagnostic_service = GameDiagnosticService(window_detector)
        self.diagnostic_controller = DiagnosticController(
            diagnostic_service,
            interval_ms=1500,
            parent=self,
        )

        settings_service = SettingsService(
            JsonSettingsRepository(Path("app/config/config.local.json"))
        )
        self.settings_controller = SettingsController(
            settings_service,
            parent=self,
        )

        calibration_service = CalibrationService(
            JsonCalibrationRepository(
                Path("app/config/calibration.local.json")
            )
        )
        self.calibration_controller = CalibrationController(
            calibration_service,
            window_detector,
            parent=self,
        )

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        sidebar = self._build_sidebar()
        self.pages = QStackedWidget()
        self.dashboard = DashboardPage(
            __version__,
            self.diagnostic_controller,
        )

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(ProductionPlannerPage())
        self.pages.addWidget(WorkflowPage())
        self.pages.addWidget(CalibrationPage(self.calibration_controller))
        self.pages.addWidget(TemplateEditorPage())
        self.pages.addWidget(VisionDebugPage())
        self.pages.addWidget(LogsPage())
        self.pages.addWidget(SettingsPage(self.settings_controller))

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.pages, 1)

        self.statusBar().showMessage("État : surveillance active")
        self._nav_buttons[0].setChecked(True)
        self.pages.setCurrentIndex(0)

        QTimer.singleShot(250, self.dashboard.start_monitoring)

    def closeEvent(self, event) -> None:
        self.dashboard.stop_monitoring()
        super().closeEvent(event)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        title = QLabel("NosMate Studio")
        title.setObjectName("AppTitle")

        subtitle = QLabel("Automation workspace")
        subtitle.setObjectName("Muted")

        nav_layout = QVBoxLayout(sidebar)
        nav_layout.setContentsMargins(16, 20, 16, 16)
        nav_layout.setSpacing(8)
        nav_layout.addWidget(title)
        nav_layout.addWidget(subtitle)
        nav_layout.addSpacing(20)

        labels = [
            "Dashboard",
            "Planificateur",
            "Workflow",
            "Calibration",
            "Templates",
            "Vision Debug",
            "Logs",
            "Paramètres",
        ]

        self._nav_buttons: list[QPushButton] = []
        group = QButtonGroup(self)
        group.setExclusive(True)

        for index, label in enumerate(labels):
            button = QPushButton(label)
            button.setCheckable(True)
            button.clicked.connect(
                lambda checked=False, i=index: self._switch_page(i)
            )
            group.addButton(button)
            self._nav_buttons.append(button)
            nav_layout.addWidget(button)

        nav_layout.addStretch(1)

        version = QLabel(f"v{__version__}")
        version.setObjectName("Muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(version)
        return sidebar

    def _switch_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        self.statusBar().showMessage(
            f"Page active : {self._nav_buttons[index].text()}"
        )
