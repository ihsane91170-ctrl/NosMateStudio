from __future__ import annotations

from typing import Any

from app.planning.production_planner import (
    PROTOMONSTER_LEVEL_CAPS,
    UPGRADE_TOKEN_COSTS,
    ProductionPlan,
    TokenBatch,
    TokenProductionPlanner,
    UpgradeRequirement,
    chicken_level_cap,
)

__all__ = [
    "FarmTokensAction",
    "PlanningAction",
    "StopAction",
    "UPGRADE_COSTS",
    "UpgradePetAction",
    "UpgradePlanner",
    "PROTOMONSTER_LEVEL_CAPS",
    "UPGRADE_TOKEN_COSTS",
    "ProductionPlan",
    "TokenBatch",
    "TokenProductionPlanner",
    "UpgradeRequirement",
    "chicken_level_cap",
]


def __getattr__(name: str) -> Any:
    """Préserve l'API existante sans charger les dépendances Windows inutilement."""

    if name in {
        "FarmTokensAction",
        "PlanningAction",
        "StopAction",
        "UpgradePetAction",
    }:
        from app.planning import models

        return getattr(models, name)

    if name in {"UPGRADE_COSTS", "UpgradePlanner"}:
        from app.planning import planner

        return getattr(planner, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
