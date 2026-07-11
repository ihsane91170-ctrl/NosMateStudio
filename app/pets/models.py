from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VisiblePet:
    index: int
    left: int
    top: int
    width: int
    height: int
    confidence: float

    @property
    def center(self) -> tuple[int, int]:
        return (
            self.left + self.width // 2,
            self.top + self.height // 2,
        )