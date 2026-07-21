from __future__ import annotations

from typing import Any

from app.planning.production_planner import (
    MAX_STARS,
    MIN_STARS,
    UPGRADE_TOKEN_COSTS,
    ProductionPlan,
    ProductionPlanner,
    TokenBatch,
)

__all__ = [
    "FarmTokensAction",
    "MAX_STARS",
    "MIN_STARS",
    "PlanningAction",
    "ProductionPlan",
    "ProductionPlanner",
    "StopAction",
    "TokenBatch",
    "UPGRADE_COSTS",
    "UPGRADE_TOKEN_COSTS",
    "UpgradePetAction",
    "UpgradePlanner",
]


def __getattr__(name: str) -> Any:
    """Charge l'ancien planificateur seulement lorsqu'il est demandé.

    Cela garde le calcul de production indépendant des modules de vision Windows.
    """
    if name in {"FarmTokensAction", "PlanningAction", "StopAction", "UpgradePetAction"}:
        from app.planning import models

        return getattr(models, name)
    if name in {"UPGRADE_COSTS", "UpgradePlanner"}:
        from app.planning import planner

        return getattr(planner, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
