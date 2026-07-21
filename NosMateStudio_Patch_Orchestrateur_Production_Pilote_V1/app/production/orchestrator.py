from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from app.planning.production_planner import ProductionPlan


class ProductionStage(str, Enum):
    PREFLIGHT = "preflight"
    CAPTURE = "capture"
    RESERVE_XP = "reserve_xp"
    LEVELING = "leveling"
    UPGRADE = "upgrade"
    EXTRACTION = "extraction"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ProductionEvent:
    stage: ProductionStage
    message: str
    completed_units: int
    total_units: int

    @property
    def progress_percent(self) -> int:
        if self.total_units <= 0:
            return 100
        return min(100, round(self.completed_units * 100 / self.total_units))


@dataclass(frozen=True, slots=True)
class ProductionResult:
    stage: ProductionStage
    produced_tokens: int
    requested_tokens: int
    message: str

    @property
    def succeeded(self) -> bool:
        return self.stage is ProductionStage.COMPLETED


EventHandler = Callable[[ProductionEvent], None]


class ProductionOrchestrator:
    """Orchestre un plan de production sans dépendre de Qt ni de NosTale.

    Cette itération exécute un scénario déterministe de simulation. Les ports
    réels de capture, XP, amélioration et extraction seront branchés étape par
    étape après calibration et validation sur Windows/NosTale.
    """

    def __init__(self, on_event: EventHandler | None = None) -> None:
        self._on_event = on_event
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    def run_simulation(self, plan: ProductionPlan) -> ProductionResult:
        self._stop_requested = False
        if plan.target_quantity <= 0:
            return ProductionResult(
                stage=ProductionStage.COMPLETED,
                produced_tokens=0,
                requested_tokens=0,
                message="Aucune production demandée.",
            )

        actions = self._build_simulation_actions(plan)
        total = len(actions)
        completed = 0

        self._emit(
            ProductionStage.PREFLIGHT,
            "Préflight simulation validé.",
            completed,
            total,
        )

        for stage, message in actions:
            if self._stop_requested:
                self._emit(
                    ProductionStage.STOPPED,
                    "Arrêt demandé par l'utilisateur.",
                    completed,
                    total,
                )
                return ProductionResult(
                    stage=ProductionStage.STOPPED,
                    produced_tokens=0,
                    requested_tokens=plan.target_quantity,
                    message="Production interrompue.",
                )
            completed += 1
            self._emit(stage, message, completed, total)

        self._emit(
            ProductionStage.COMPLETED,
            f"Objectif atteint : {plan.target_quantity}/{plan.target_quantity} jetons {plan.target_stars}★.",
            total,
            total,
        )
        return ProductionResult(
            stage=ProductionStage.COMPLETED,
            produced_tokens=plan.target_quantity,
            requested_tokens=plan.target_quantity,
            message="Simulation terminée avec succès.",
        )

    @staticmethod
    def _build_simulation_actions(
        plan: ProductionPlan,
    ) -> list[tuple[ProductionStage, str]]:
        actions: list[tuple[ProductionStage, str]] = []
        actions.append(
            (
                ProductionStage.CAPTURE,
                f"Capturer {plan.chickens_to_capture} poules et vérifier chaque capture.",
            )
        )
        actions.append(
            (
                ProductionStage.RESERVE_XP,
                f"Envoyer {plan.chickens_to_capture} poules vers la réserve XP.",
            )
        )

        for batch in plan.batches:
            actions.append(
                (
                    ProductionStage.LEVELING,
                    f"Monter {batch.quantity} poules {batch.stars}★ au niveau {batch.max_level}.",
                )
            )
            actions.append(
                (
                    ProductionStage.EXTRACTION,
                    f"Extraire {batch.quantity} jetons {batch.stars}★ au niveau maximal.",
                )
            )

        for upgrade in plan.upgrades:
            actions.append(
                (
                    ProductionStage.UPGRADE,
                    f"Améliorer {upgrade.chickens_to_upgrade} poules de {upgrade.from_stars}★ vers {upgrade.to_stars}★ "
                    f"avec {upgrade.required_tokens} jetons {upgrade.from_stars}★; retour niveau 1 attendu.",
                )
            )
        return actions

    def _emit(
        self,
        stage: ProductionStage,
        message: str,
        completed: int,
        total: int,
    ) -> None:
        if self._on_event is not None:
            self._on_event(
                ProductionEvent(
                    stage=stage,
                    message=message,
                    completed_units=completed,
                    total_units=total,
                )
            )
