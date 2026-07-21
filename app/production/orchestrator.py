from __future__ import annotations

from collections.abc import Callable

from app.planning.production_planner import ProductionPlan, ProductionPlanner
from app.production.models import ProductionEvent, ProductionResult, ProductionState

EventListener = Callable[[ProductionEvent], None]


class ProductionStopped(RuntimeError):
    pass


class ProductionOrchestrator:
    """Orchestre un cycle de production pilote en simulation.

    Le mode réel est volontairement refusé tant que les confirmations visuelles
    de capture, niveau, amélioration et extraction ne sont pas branchées.
    """

    def __init__(self, planner: ProductionPlanner | None = None) -> None:
        self._planner = planner or ProductionPlanner()
        self._stop_requested = False

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(
        self,
        quantity: int,
        stars: int,
        *,
        simulation: bool = True,
        listener: EventListener | None = None,
    ) -> ProductionResult:
        if not simulation:
            raise RuntimeError(
                "Le mode réel est verrouillé tant que les confirmations NosTale ne sont pas validées."
            )

        self._stop_requested = False
        events: list[ProductionEvent] = []
        plan = self._planner.plan(quantity, stars)
        total_units = self._total_units(plan)
        completed = 0

        def emit(state: ProductionState, message: str, advance: int = 0) -> None:
            nonlocal completed
            self._check_stop()
            completed += advance
            event = ProductionEvent(state, message, completed, total_units)
            events.append(event)
            if listener is not None:
                listener(event)

        try:
            emit(ProductionState.PLANNING, f"Plan calculé : {plan.chickens_to_capture} poule(s) à capturer.")
            emit(ProductionState.PREFLIGHT, "Préflight simulation validé.", 1)

            for batch in plan.batches:
                emit(
                    ProductionState.CAPTURING,
                    f"Capture simulée de {batch.quantity} poule(s) pour le lot {batch.stars}★.",
                    batch.quantity,
                )
                emit(
                    ProductionState.RESERVING,
                    f"Envoi simulé de {batch.quantity} poule(s) vers la réserve XP.",
                    batch.quantity,
                )
                emit(
                    ProductionState.LEVELING,
                    f"XP simulée jusqu'au niveau {batch.extraction_level} pour le lot {batch.stars}★.",
                    batch.quantity,
                )
                if batch.stars > 1:
                    emit(
                        ProductionState.UPGRADING,
                        f"Améliorations simulées jusqu'à {batch.stars}★ avec retour niveau 1 après chaque amélioration.",
                        batch.quantity * (batch.stars - 1),
                    )
                emit(
                    ProductionState.EXTRACTING,
                    f"Extraction simulée de {batch.quantity} jeton(s) {batch.stars}★ au niveau maximal.",
                    batch.quantity,
                )

            emit(
                ProductionState.FINISHED,
                f"Objectif atteint : {quantity}/{quantity} jeton(s) {stars}★.",
            )
            return ProductionResult(ProductionState.FINISHED, quantity, quantity, tuple(events))
        except ProductionStopped:
            event = ProductionEvent(
                ProductionState.STOPPED,
                "Production arrêtée à la demande de l'utilisateur.",
                completed,
                total_units,
            )
            events.append(event)
            if listener is not None:
                listener(event)
            return ProductionResult(ProductionState.STOPPED, 0, quantity, tuple(events))

    def _check_stop(self) -> None:
        if self._stop_requested:
            raise ProductionStopped

    @staticmethod
    def _total_units(plan: ProductionPlan) -> int:
        capture = plan.chickens_to_capture
        reserve = capture
        leveling = capture
        extraction = capture
        upgrades = sum(batch.quantity * (batch.stars - 1) for batch in plan.batches)
        return 1 + capture + reserve + leveling + upgrades + extraction
