from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameWindow:
    title: str
    left: int
    top: int
    width: int
    height: int


def find_nostale_window(title_contains: str = "NosTale") -> GameWindow | None:
    """US001 — implémentation prévue dans la branche dédiée."""
    raise NotImplementedError("US001 n'est pas encore développée.")
