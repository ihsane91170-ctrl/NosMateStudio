from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.planning.production_planner import ProductionPlan, TokenProductionPlanner
from app.production import ProductionEvent, ProductionOrchestrator, ProductionStage


class ProductionPlannerPage(QWidget):
    """Écran métier permettant de calculer un plan de production de jetons."""

    def __init__(self, planner: TokenProductionPlanner | None = None, parent=None) -> None:
        super().__init__(parent)
        self._planner = planner or TokenProductionPlanner()
        self.current_plan: ProductionPlan | None = None
        self._orchestrator = ProductionOrchestrator(self._on_production_event)

        title = QLabel("Planificateur de jetons")
        title.setObjectName("PageTitle")

        description = QLabel(
            "Choisissez la quantité et le niveau des jetons. "
            "NosMate Studio calcule les lots intermédiaires et le nombre de poules à capturer."
        )
        description.setObjectName("Muted")
        description.setWordWrap(True)

        form_frame = QFrame()
        form_frame.setObjectName("Card")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        self.quantity_input = QSpinBox()
        self.quantity_input.setObjectName("TokenQuantityInput")
        self.quantity_input.setRange(1, 999_999)
        self.quantity_input.setValue(34)

        self.stars_input = QComboBox()
        self.stars_input.setObjectName("TokenStarsInput")
        for stars in range(1, 7):
            self.stars_input.addItem(f"{stars}★", stars)
        self.stars_input.setCurrentIndex(2)

        self.calculate_button = QPushButton("Calculer le plan")
        self.calculate_button.setObjectName("PrimaryButton")
        self.calculate_button.clicked.connect(self.calculate_plan)

        form_layout.addRow("Quantité", self.quantity_input)
        form_layout.addRow("Niveau du jeton", self.stars_input)
        form_layout.addRow("", self.calculate_button)

        self.summary_label = QLabel("Aucun plan calculé.")
        self.summary_label.setObjectName("PlanSummary")
        self.summary_label.setWordWrap(True)

        self.simulation_radio = QRadioButton("Simulation")
        self.real_radio = QRadioButton("Réel (verrouillé)")
        self.simulation_radio.setChecked(True)
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.simulation_radio)
        mode_layout.addWidget(self.real_radio)
        mode_layout.addStretch(1)

        self.produce_button = QPushButton("Produire")
        self.produce_button.setObjectName("PrimaryButton")
        self.produce_button.clicked.connect(self.start_production)

        self.stop_button = QPushButton("Arrêt d'urgence")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_production)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.produce_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addStretch(1)

        self.production_state = QLabel("Production : prête")
        self.production_state.setObjectName("Muted")

        self.production_progress = QProgressBar()
        self.production_progress.setRange(0, 100)
        self.production_progress.setValue(0)

        self.production_log = QTextEdit()
        self.production_log.setReadOnly(True)
        self.production_log.setMinimumHeight(150)
        self.production_log.setPlaceholderText("Le journal de production apparaîtra ici.")

        self.batch_table = QTableWidget(0, 4)
        self.batch_table.setObjectName("ProductionPlanTable")
        self.batch_table.setHorizontalHeaderLabels(
            ["Jeton", "Quantité", "Niveau d'extraction", "Destination"]
        )
        self.batch_table.horizontalHeader().setStretchLastSection(True)
        self.batch_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.batch_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        note = QLabel(
            "La simulation déroule la chaîne complète. Le mode réel reste verrouillé tant que "
            "les confirmations visuelles NosTale ne sont pas validées."
        )
        note.setObjectName("Muted")
        note.setWordWrap(True)

        content_row = QHBoxLayout()
        content_row.setSpacing(16)
        content_row.addWidget(form_frame, 0)
        content_row.addWidget(self.batch_table, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addLayout(content_row)
        layout.addWidget(self.summary_label)
        layout.addLayout(mode_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.production_state)
        layout.addWidget(self.production_progress)
        layout.addWidget(self.production_log)
        layout.addWidget(note)
        layout.addStretch(1)

        self.calculate_plan()

    def calculate_plan(self) -> ProductionPlan:
        quantity = self.quantity_input.value()
        stars = int(self.stars_input.currentData())
        plan = self._planner.plan(quantity=quantity, stars=stars)
        self.current_plan = plan
        self._display_plan(plan)
        return plan

    def _display_plan(self, plan: ProductionPlan) -> None:
        self.summary_label.setText(
            f"Objectif : {plan.target_quantity} jetons {plan.target_stars}★ — "
            f"{plan.chickens_to_capture} poules à capturer au total."
        )

        self.batch_table.setRowCount(len(plan.batches))
        for row, batch in enumerate(plan.batches):
            destination = (
                "Jeton final" if batch.stars == plan.target_stars else "Jeton intermédiaire"
            )
            values = (
                f"{batch.stars}★",
                str(batch.quantity),
                f"Niveau {batch.max_level}",
                destination,
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {0, 1, 2}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.batch_table.setItem(row, column, item)

    def start_production(self) -> None:
        if self.real_radio.isChecked():
            QMessageBox.warning(
                self,
                "Mode réel verrouillé",
                "Le mode réel n'est pas encore autorisé : les confirmations de capture, "
                "niveau, amélioration et extraction doivent d'abord être validées sous NosTale.",
            )
            return

        plan = self.calculate_plan()
        self.production_log.clear()
        self.production_progress.setValue(0)
        self.production_state.setText("Production : simulation en cours")
        self.produce_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        result = self._orchestrator.run_simulation(plan)

        self.stop_button.setEnabled(False)
        self.produce_button.setEnabled(True)
        if result.succeeded:
            self.production_state.setText(
                f"Production : terminée — {result.produced_tokens}/{result.requested_tokens}"
            )
        elif result.stage is ProductionStage.STOPPED:
            self.production_state.setText("Production : arrêtée")
        else:
            self.production_state.setText(f"Production : erreur — {result.message}")

    def stop_production(self) -> None:
        self._orchestrator.request_stop()
        self.production_state.setText("Production : arrêt demandé")

    def _on_production_event(self, event: ProductionEvent) -> None:
        self.production_progress.setValue(event.progress_percent)
        self.production_log.append(f"[{event.stage.value}] {event.message}")
