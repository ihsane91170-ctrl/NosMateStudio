from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.calibration.repository import JsonCalibrationRepository
from app.configuration.defaults import DEFAULT_SETTINGS
from app.configuration.repository import JsonSettingsRepository
from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_engine import WorkflowEngine, WorkflowEvent
from app.engine.workflow_state import WorkflowState
from app.execution import PreflightCheck
from app.monitor import WorkflowMonitor
from app.runtime import AutomationRuntime, RuntimeFactory, RuntimeMode
from app.vision.window_detector import GameWindow, WindowDetector
from app.workflows import WorkflowLibrary


class WorkflowPage(QWidget):
    SETTINGS_PATH = Path("app/config/config.local.json")
    CALIBRATION_PATH = Path("app/config/calibration.local.json")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.library = WorkflowLibrary()
        self.library.register_defaults()

        self.window_detector = WindowDetector("NosTale")
        self.settings_repository = JsonSettingsRepository(
            self.SETTINGS_PATH
        )
        self.calibration_repository = JsonCalibrationRepository(
            self.CALIBRATION_PATH
        )

        self.monitor = WorkflowMonitor(
            workflow_name="",
            total_steps=0,
        )

        title = QLabel("Workflow")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Sélectionnez un workflow, un mode d'exécution et le nombre "
            "de cycles. Le mode réel envoie de vraies commandes au jeu."
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
        layout.addLayout(form)
        layout.addWidget(self.state_label)
        layout.addWidget(self.cycle_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.current_step_label)
        layout.addWidget(self.run_button)
        layout.addWidget(self.log_output, 1)

    def _run_selected_workflow(self) -> None:
        selected_name = self.workflow_selector.currentText()
        is_real = self.real_radio.isChecked()

        allowed_real_workflows = {
            "First Real Action",
            "Pet XP Workflow",
        }

        if is_real and selected_name not in allowed_real_workflows:
            QMessageBox.warning(
                self,
                "Workflow réel indisponible",
                "Ce workflow n'est pas encore autorisé en mode réel.",
            )
            return

        settings = self.settings_repository.load() or DEFAULT_SETTINGS
        calibration = self.calibration_repository.load()
        window = self.window_detector.detect()

        if is_real:
            preflight = PreflightCheck(self.window_detector)
            result = preflight.run(
                settings=settings,
                calibration=calibration,
                require_calibration=False,
            )

            if not result.allowed:
                self.state_label.setText(
                    f"État : impossible de démarrer — {result.message}"
                )
                self.log_output.setPlainText(result.message)
                return

            self.log_output.setPlainText("Préflight validé. Confirmation requise.")

            confirmation = QMessageBox.warning(
                self,
                "Confirmer l'exécution réelle",
                (
                    "NosMate Studio va envoyer de vraies commandes clavier.\n\n"
                    f"Workflow : {selected_name}\n"
                    f"Cycles : {self.cycles_input.value()}\n\n"
                    "Assurez-vous que NosTale est ouvert et prêt."
                ),
                (
                    QMessageBox.StandardButton.Ok
                    | QMessageBox.StandardButton.Cancel
                ),
                QMessageBox.StandardButton.Cancel,
            )

            if confirmation != QMessageBox.StandardButton.Ok:
                return

            self.log_output.clear()
            self.log_output.append("Confirmation acceptée.")
            self.log_output.append("Préflight validé.")

            if window is not None:
                self.log_output.append(
                    f"Fenêtre détectée : {window.title}"
                )

            self._set_controls_enabled(False)
            self._run_countdown()

        if window is None:
            if is_real:
                return

            window = GameWindow(
                title="NosTale Simulation",
                left=400,
                top=200,
                width=1280,
                height=720,
            )

        mode = (
            RuntimeMode.REAL
            if is_real
            else RuntimeMode.SIMULATION
        )
        runtime = RuntimeFactory.create(mode)

        context = WorkflowContext(
            runtime=runtime,
            data={
                "settings": settings,
                "calibration": calibration,
                "game_window": window,
            },
        )

        workflow = self.library.get(selected_name)
        steps = workflow.steps()
        total_cycles = self.cycles_input.value()

        if not is_real:
            self._set_controls_enabled(False)
            self.log_output.clear()

        self.progress_bar.setValue(0)
        self.current_step_label.setText("Étape : —")
        self.state_label.setText("État : exécution")

        self.log_output.append(f"Workflow : {workflow.name}")
        self.log_output.append(
            f"Mode : {'réel' if is_real else 'simulation'}"
        )
        self.log_output.append(f"Cycles : {total_cycles}")
        self.log_output.append("")

        final_state = WorkflowState.FINISHED
        last_error: str | None = None

        for cycle_number in range(1, total_cycles + 1):
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

            engine = WorkflowEngine(
                on_event=self._on_workflow_event
            )
            final_state = engine.run(steps, context)

            if final_state is not WorkflowState.FINISHED:
                last_error = engine.last_error
                break

        if final_state is WorkflowState.FINISHED:
            self.state_label.setText("État : terminé")
        else:
            message = last_error or "Erreur inconnue"
            self.state_label.setText(
                f"État : erreur — {message}"
            )
            self.log_output.append(f"Erreur : {message}")

        if not is_real:
            self._append_simulation_summary(runtime)

        self._set_controls_enabled(True)

    def _run_countdown(self, seconds: int = 3) -> None:
        self.log_output.append("")
        self.log_output.append(
            "Cliquez maintenant sur la fenêtre NosTale."
        )

        for remaining in range(seconds, 0, -1):
            message = f"Démarrage réel dans {remaining}..."
            self.state_label.setText(f"État : {message}")
            self.log_output.append(message)

            QApplication.processEvents()
            time.sleep(1)

        self.state_label.setText("État : exécution réelle")
        self.log_output.append("GO")
        QApplication.processEvents()

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

    def _append_simulation_summary(
        self,
        runtime: AutomationRuntime,
    ) -> None:
        self.log_output.append("")
        self.log_output.append("Résumé de la simulation")
        self.log_output.append(
            f"Clavier : {runtime.keyboard.history}"
        )
        self.log_output.append(
            f"Souris : {runtime.mouse.history}"
        )
        self.log_output.append(
            f"Attentes : {runtime.wait.history}"
        )

    def _set_controls_enabled(self, enabled: bool) -> None:
        self.run_button.setEnabled(enabled)
        self.workflow_selector.setEnabled(enabled)
        self.simulation_radio.setEnabled(enabled)
        self.real_radio.setEnabled(enabled)
        self.cycles_input.setEnabled(enabled)