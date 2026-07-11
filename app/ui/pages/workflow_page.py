from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
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
from app.monitor import WorkflowMonitor
from app.runtime import AutomationRuntime, RuntimeFactory, RuntimeMode
from app.vision.window_detector import GameWindow
from app.workflows import WorkflowLibrary


class WorkflowPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.library = WorkflowLibrary()
        self.library.register_defaults()

        title = QLabel("Workflow")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Sélectionnez un workflow, un mode d'exécution et le nombre "
            "de cycles. Le mode réel sera activé dans la prochaine étape."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        self.workflow_selector = QComboBox()
        self.workflow_selector.addItems(self.library.names())

        self.simulation_radio = QRadioButton("Simulation")
        self.real_radio = QRadioButton("Réel")
        self.simulation_radio.setChecked(True)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.simulation_radio)
        mode_layout.addWidget(self.real_radio)
        mode_layout.addStretch(1)

        mode_container = QWidget()
        mode_container.setLayout(mode_layout)

        self.cycles_input = QSpinBox()
        self.cycles_input.setRange(1, 1000)
        self.cycles_input.setValue(1)

        form = QFormLayout()
        form.addRow("Workflow", self.workflow_selector)
        form.addRow("Mode", mode_container)
        form.addRow("Nombre de cycles", self.cycles_input)

        self.state_label = QLabel("État : prêt")
        self.state_label.setObjectName("Muted")

        self.cycle_label = QLabel("Cycle : —")
        self.cycle_label.setObjectName("Muted")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.current_step_label = QLabel("Étape : —")
        self.current_step_label.setObjectName("Muted")

        self.run_button = QPushButton("Démarrer")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self._run_selected_workflow)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._request_stop)

        buttons = QHBoxLayout()
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.stop_button)
        buttons.addStretch(1)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText(
            "Les événements du workflow apparaîtront ici."
        )

        self.monitor = WorkflowMonitor(
            workflow_name="",
            total_steps=0,
        )

        self._stop_requested = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addWidget(self.state_label)
        layout.addWidget(self.cycle_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.current_step_label)
        layout.addLayout(buttons)
        layout.addWidget(self.log_output, 1)

    def _create_runtime(self) -> AutomationRuntime:
        mode = (
            RuntimeMode.REAL
            if self.real_radio.isChecked()
            else RuntimeMode.SIMULATION
        )

        return RuntimeFactory.create(mode)

    def _run_selected_workflow(self) -> None:
        if self.real_radio.isChecked():
            self.state_label.setText(
                "État : le mode réel n'est pas encore activé"
            )
            self.log_output.setPlainText(
                "Le mode réel sera branché avec les contrôles de sécurité "
                "dans la prochaine étape du MVP."
            )
            return

        self._set_running_state(True)
        self._stop_requested = False
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.current_step_label.setText("Étape : —")

        selected_name = self.workflow_selector.currentText()
        workflow = self.library.get(selected_name)
        steps = workflow.steps()
        total_cycles = self.cycles_input.value()

        runtime = self._create_runtime()

        keyboard = runtime.keyboard
        mouse = runtime.mouse
        waiter = runtime.wait

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

        self.log_output.append(f"Workflow : {workflow.name}")
        self.log_output.append("Mode : simulation")
        self.log_output.append(f"Cycles demandés : {total_cycles}")
        self.log_output.append("")

        final_state = WorkflowState.FINISHED

        for cycle_number in range(1, total_cycles + 1):
            if self._stop_requested:
                self.log_output.append("Arrêt demandé par l'utilisateur.")
                final_state = WorkflowState.IDLE
                break

            self.cycle_label.setText(
                f"Cycle : {cycle_number} / {total_cycles}"
            )
            self.log_output.append(
                f"--- Cycle {cycle_number} / {total_cycles} ---"
            )

            self.monitor = WorkflowMonitor(
                workflow_name=workflow.name,
                total_steps=len(steps),
            )

            engine = WorkflowEngine(on_event=self._on_workflow_event)
            final_state = engine.run(steps, context)

            if final_state is not WorkflowState.FINISHED:
                error = engine.last_error or "Erreur inconnue"
                self.log_output.append(f"Erreur : {error}")
                break

        if final_state is WorkflowState.FINISHED:
            self.state_label.setText("État : terminé")
        elif self._stop_requested:
            self.state_label.setText("État : arrêté")
        else:
            self.state_label.setText("État : erreur")

        self._append_runtime_summary(
            keyboard=keyboard,
            mouse=mouse,
            waiter=waiter,
        )
        self._set_running_state(False)

    def _request_stop(self) -> None:
        self._stop_requested = True
        self.state_label.setText("État : arrêt demandé")
        self.log_output.append("Demande d'arrêt enregistrée.")

    def _set_running_state(self, running: bool) -> None:
        self.run_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.workflow_selector.setEnabled(not running)
        self.simulation_radio.setEnabled(not running)
        self.real_radio.setEnabled(not running)
        self.cycles_input.setEnabled(not running)

        if running:
            self.state_label.setText("État : exécution")

    def _on_workflow_event(self, event: WorkflowEvent) -> None:
        line = event.name

        if event.step_name:
            line += f" — {event.step_name}"

        if event.message:
            line += f" — {event.message}"

        self.log_output.append(line)

        if event.name == "workflow_started":
            self.monitor.start()

        elif event.name == "step_started":
            self.monitor.update(
                self.monitor.progress.current_index,
                event.step_name or "",
            )

        elif event.name == "workflow_finished":
            self.monitor.finish()

        self.progress_bar.setValue(
            self.monitor.progress.percentage
        )
        self.current_step_label.setText(
            f"Étape : {self.monitor.progress.current_step}"
        )

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