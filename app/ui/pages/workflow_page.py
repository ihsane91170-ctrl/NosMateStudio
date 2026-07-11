from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.calibration.models import (
    CalibrationProfile,
    CalibrationTarget,
    RelativePoint,
)
from app.configuration.defaults import DEFAULT_SETTINGS
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_engine import WorkflowEngine, WorkflowEvent
from app.engine.workflow_state import WorkflowState
from app.executors.keyboard import SimulationKeyboardExecutor
from app.executors.mouse import SimulationMouseExecutor
from app.executors.wait import SimulationWaitExecutor
from app.runtime import AutomationRuntime
from app.vision.window_detector import GameWindow
from app.workflows import DemoWorkflow


class WorkflowPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        title = QLabel("Workflow")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Exécutez le workflow de démonstration en mode simulation. "
            "Aucune action réelle ne sera envoyée au système."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        self.state_label = QLabel("État : prêt")
        self.state_label.setObjectName("Muted")

        self.run_button = QPushButton("Lancer la simulation")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self._run_demo_workflow)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText(
            "Les événements du workflow apparaîtront ici."
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self.state_label)
        layout.addWidget(self.run_button)
        layout.addWidget(self.log_output, 1)

    def _run_demo_workflow(self) -> None:
        self.run_button.setEnabled(False)
        self.log_output.clear()
        self.state_label.setText("État : exécution")

        keyboard = SimulationKeyboardExecutor()
        mouse = SimulationMouseExecutor()
        waiter = SimulationWaitExecutor()

        runtime = AutomationRuntime(
            keyboard=keyboard,
            mouse=mouse,
            wait=waiter,
        )

        calibration = CalibrationProfile(
            points={
                CalibrationTarget.PET_ICON_1: RelativePoint(100, 50),
                CalibrationTarget.ACCOMPANY_BUTTON: RelativePoint(300, 200),
            }
        )

        window = GameWindow(
            title="NosTale",
            left=400,
            top=200,
            width=1280,
            height=720,
        )

        context = WorkflowContext(
            runtime=runtime,
            data={
                "settings": DEFAULT_SETTINGS,
                "calibration": calibration,
                "game_window": window,
            },
        )

        engine = WorkflowEngine(on_event=self._on_workflow_event)
        workflow = DemoWorkflow()

        state = engine.run(workflow.steps(), context)

        if state is WorkflowState.FINISHED:
            self.state_label.setText("État : terminé")
        else:
            error = engine.last_error or "Erreur inconnue"
            self.state_label.setText(f"État : erreur — {error}")

        self._append_runtime_summary(
            keyboard=keyboard,
            mouse=mouse,
            waiter=waiter,
        )
        self.run_button.setEnabled(True)

    def _on_workflow_event(self, event: WorkflowEvent) -> None:
        line = event.name

        if event.step_name:
            line += f" — {event.step_name}"

        if event.message:
            line += f" — {event.message}"

        self.log_output.append(line)

    def _append_runtime_summary(
        self,
        keyboard: SimulationKeyboardExecutor,
        mouse: SimulationMouseExecutor,
        waiter: SimulationWaitExecutor,
    ) -> None:
        self.log_output.append("")
        self.log_output.append("Résumé de la simulation")
        self.log_output.append(f"Clavier : {keyboard.history}")
        self.log_output.append(f"Souris : {mouse.history}")
        self.log_output.append(f"Attentes : {waiter.history}")