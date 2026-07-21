from __future__ import annotations

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QProgressBar,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.capture.worker import CaptureBatchWorker
from app.production import ProductionPlan, TokenGoal, TokenProductionPlanner


class ProductionPage(QWidget):
    """Point d'entrée des deux workflows séparés."""

    capture_requested = Signal(int)
    production_plan_ready = Signal(object)

    def __init__(
        self,
        planner: TokenProductionPlanner | None = None,
        capture_service=None,
        return_service=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._planner = planner or TokenProductionPlanner()
        self._last_plan: ProductionPlan | None = None
        self._token_inputs: list[QSpinBox] = []
        self._capture_service = capture_service
        self._return_service = return_service
        self._capture_thread: QThread | None = None
        self._capture_worker: CaptureBatchWorker | None = None
        self._build_ui()

    @property
    def last_plan(self) -> ProductionPlan | None:
        return self._last_plan

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(18)

        title = QLabel("Production de jetons")
        title.setObjectName("PageTitle")
        subtitle = QLabel(
            "Deux workflows indépendants : capturer les poules, puis transformer "
            "les familiers jusqu'aux jetons demandés."
        )
        subtitle.setWordWrap(True)
        subtitle.setObjectName("Muted")
        root.addWidget(title)
        root.addWidget(subtitle)

        columns = QHBoxLayout()
        columns.setSpacing(16)
        columns.addWidget(self._build_capture_card(), 1)
        columns.addWidget(self._build_goal_card(), 2)
        root.addLayout(columns)
        root.addWidget(self._build_plan_card(), 1)

    def _card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Card")
        return frame

    def _build_capture_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        heading = QLabel("1 — Capturer des poules")
        heading.setObjectName("SectionTitle")
        description = QLabel(
            "Le module capture s'arrête une fois le nombre demandé atteint."
        )
        description.setWordWrap(True)
        description.setObjectName("Muted")
        self.capture_count = QSpinBox()
        self.capture_count.setObjectName("captureCount")
        self.capture_count.setRange(1, 999)
        self.capture_count.setValue(10)
        self.save_capture_diagnostics = QCheckBox("Sauvegarder les captures de diagnostic")
        self.save_capture_diagnostics.setObjectName("saveCaptureDiagnostics")
        self.save_capture_diagnostics.setChecked(True)
        self.save_capture_diagnostics.setToolTip(
            "Enregistre chaque image, toutes les détections IA et la cible choisie "
            "dans vision_logs/capture_batch."
        )
        self.capture_button = QPushButton("Lancer la capture")
        self.capture_button.setObjectName("captureButton")
        self.capture_button.clicked.connect(self._request_capture)
        self.stop_capture_button = QPushButton("Arrêter")
        self.stop_capture_button.setEnabled(False)
        self.stop_capture_button.clicked.connect(self._stop_capture)
        self.capture_progress = QProgressBar()
        self.capture_progress.setRange(0, 10)
        self.capture_progress.setValue(0)
        self.capture_status = QLabel("Prêt.")
        self.capture_status.setObjectName("Muted")
        self.capture_status.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Nombre de poules", self.capture_count)
        layout.addWidget(heading)
        layout.addWidget(description)
        layout.addLayout(form)
        layout.addWidget(self.save_capture_diagnostics)
        actions = QHBoxLayout()
        actions.addWidget(self.capture_button)
        actions.addWidget(self.stop_capture_button)
        layout.addLayout(actions)
        layout.addWidget(self.capture_progress)
        layout.addWidget(self.capture_status)
        layout.addStretch(1)
        return card

    def _build_goal_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        heading = QLabel("2 — Produire des jetons")
        heading.setObjectName("SectionTitle")
        description = QLabel(
            "Indique le stock final souhaité. Le plan inclut XP, montées "
            "d'étoiles et extractions intermédiaires."
        )
        description.setWordWrap(True)
        description.setObjectName("Muted")
        layout.addWidget(heading)
        layout.addWidget(description)

        grid = QGridLayout()
        for stars in range(1, 6):
            label = QLabel(f"Jetons {stars}★")
            spin = QSpinBox()
            spin.setObjectName(f"tokenGoal{stars}")
            spin.setRange(0, 9999)
            self._token_inputs.append(spin)
            grid.addWidget(label, 0, stars - 1)
            grid.addWidget(spin, 1, stars - 1)
        layout.addLayout(grid)

        self.calculate_button = QPushButton("Calculer le plan")
        self.calculate_button.setObjectName("calculatePlanButton")
        self.calculate_button.clicked.connect(self._calculate_plan)
        self.goal_status = QLabel("Saisis au moins un objectif.")
        self.goal_status.setObjectName("Muted")
        self.goal_status.setWordWrap(True)
        layout.addWidget(self.calculate_button)
        layout.addWidget(self.goal_status)
        return card

    def _build_plan_card(self) -> QFrame:
        card = self._card()
        layout = QVBoxLayout(card)
        heading = QLabel("Plan calculé")
        heading.setObjectName("SectionTitle")
        self.summary = QLabel("Aucun plan calculé.")
        self.summary.setObjectName("productionSummary")
        self.summary.setWordWrap(True)

        self.plan_table = QTableWidget(5, 4)
        self.plan_table.setObjectName("productionPlanTable")
        self.plan_table.setHorizontalHeaderLabels(
            ["Étoiles", "Objectif final", "Jetons à extraire", "Poules à maxer"]
        )
        self.plan_table.verticalHeader().setVisible(False)
        self.plan_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.plan_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for row, stars in enumerate(range(1, 6)):
            self.plan_table.setItem(row, 0, QTableWidgetItem(f"{stars}★"))
            for column in range(1, 4):
                self.plan_table.setItem(row, column, QTableWidgetItem("0"))

        layout.addWidget(heading)
        layout.addWidget(self.summary)
        layout.addWidget(self.plan_table)
        return card

    def _request_capture(self) -> None:
        if self._capture_thread is not None:
            return

        count = self.capture_count.value()
        self.capture_requested.emit(count)
        if self._capture_service is None or self._return_service is None:
            self.capture_status.setText(
                "Capture indisponible : les services réels ne sont pas configurés."
            )
            return

        set_recording = getattr(self._capture_service, "set_recording_enabled", None)
        if callable(set_recording):
            set_recording(self.save_capture_diagnostics.isChecked())

        self.capture_progress.setRange(0, count)
        self.capture_progress.setValue(0)
        self.capture_button.setEnabled(False)
        self.stop_capture_button.setEnabled(True)
        self.capture_count.setEnabled(False)
        self.save_capture_diagnostics.setEnabled(False)
        self.capture_status.setText(f"Capture en cours : 0/{count}.")

        thread = QThread(self)
        worker = CaptureBatchWorker(
            self._capture_service, self._return_service, count
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_capture_progress)
        worker.finished.connect(self._on_capture_finished)
        worker.failed.connect(self._on_capture_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_capture_job)
        self._capture_thread = thread
        self._capture_worker = worker
        thread.start()

    def _stop_capture(self) -> None:
        if self._capture_worker is not None:
            self.capture_status.setText("Arrêt demandé ; fin de l'action en cours…")
            self._capture_worker.request_stop()
            self.stop_capture_button.setEnabled(False)

    def _on_capture_progress(self, progress) -> None:
        self.capture_progress.setValue(progress.captured_count)
        phase = str(getattr(progress, "phase", ""))
        searches = int(getattr(progress, "search_attempts", 0))
        captures = int(getattr(progress, "capture_attempts", 0))
        detail = str(getattr(progress, "message", "") or "").strip()
        prefix = f"Poule {progress.captured_count + 1}/{progress.target_count}"

        if phase == "search":
            self.capture_status.setText(
                f"{prefix} — recherche IA {searches}/100 ; "
                f"captures réelles consommées : {captures}/10."
            )
        elif phase == "search_rejected":
            self.capture_status.setText(
                f"{prefix} — cible rejetée à la recherche {searches}/100 ; "
                f"quota capture inchangé : {captures}/10. {detail}"
            )
        elif phase == "capture_failed":
            self.capture_status.setText(
                f"{prefix} — tentative réelle de capture {captures}/10 échouée. "
                f"{detail}"
            )
        elif phase == "captured":
            self.capture_status.setText(
                f"{prefix} — capture confirmée après {searches} recherche(s) "
                f"et {captures} tentative(s) réelle(s)."
            )
        elif phase == "standby":
            self.capture_status.setText(detail)
        elif phase == "return":
            self.capture_status.setText(detail)
        elif phase == "counted":
            self.capture_status.setText(
                f"Poule confirmée : {progress.captured_count}/{progress.target_count}."
            )
        elif detail:
            self.capture_status.setText(detail)

    def _on_capture_finished(self, result) -> None:
        self.capture_progress.setValue(result.captured_count)
        self.capture_status.setText(result.message)

    def _on_capture_failed(self, message: str) -> None:
        self.capture_status.setText(f"Erreur pendant la capture : {message}")

    def _clear_capture_job(self) -> None:
        self._capture_thread = None
        self._capture_worker = None
        self.capture_button.setEnabled(True)
        self.stop_capture_button.setEnabled(False)
        self.capture_count.setEnabled(True)
        self.save_capture_diagnostics.setEnabled(True)

    def _calculate_plan(self) -> None:
        goal = TokenGoal(tuple(spin.value() for spin in self._token_inputs))
        if goal.is_empty:
            self._last_plan = None
            self.goal_status.setText("Ajoute au moins un jeton à produire.")
            self.summary.setText("Aucun plan calculé.")
            return

        plan = self._planner.build(goal)
        self._last_plan = plan
        self._render_plan(plan)
        self.production_plan_ready.emit(plan)

    def _render_plan(self, plan: ProductionPlan) -> None:
        for row in range(5):
            values = (
                plan.requested_tokens[row],
                plan.tokens_to_extract[row],
                plan.pets_to_level[row],
            )
            for column, value in enumerate(values, start=1):
                self.plan_table.item(row, column).setText(str(value))

        upgrade_count = sum(plan.upgrades)
        self.summary.setText(
            f"Besoin total : {plan.chickens_required} poule(s), "
            f"{upgrade_count} montée(s) d'étoiles et "
            f"{sum(plan.tokens_to_extract)} extraction(s)."
        )
        self.goal_status.setText(
            "Plan prêt. Les actions réelles XP/étoiles/extraction seront "
            "branchées progressivement sur ce plan."
        )
