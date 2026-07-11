from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameWindow:
    title: str
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> tuple[int, int]:
        return (
            self.left + self.width // 2,
            self.top + self.height // 2,
        )

    @property
    def is_usable(self) -> bool:
        return self.width > 0 and self.height > 0


def find_nostale_window(title_contains: str = "NosTale") -> GameWindow | None:
    """US001 — implémentation prévue dans la branche dédiée."""
    raise NotImplementedError("US001 n'est pas encore développée.")
