from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FarmTokensAction:
    required_tokens: int
    missing_tokens: int


@dataclass(frozen=True, slots=True)
class UpgradePetAction:
    profile_id: str
    current_stars: int
    target_stars: int
    cost: int


@dataclass(frozen=True, slots=True)
class StopAction:
    reason: str


PlanningAction = (
    FarmTokensAction
    | UpgradePetAction
    | StopAction
)