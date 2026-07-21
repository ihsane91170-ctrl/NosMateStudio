from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenGoal:
    """Objectif de jetons à produire, indexé de 1 à 5 étoiles."""

    quantities: tuple[int, int, int, int, int]

    def __post_init__(self) -> None:
        if len(self.quantities) != 5:
            raise ValueError("Cinq quantités sont requises (1★ à 5★).")
        if any(value < 0 for value in self.quantities):
            raise ValueError("Les quantités ne peuvent pas être négatives.")

    def quantity(self, stars: int) -> int:
        if stars not in range(1, 6):
            raise ValueError("Le niveau d'étoiles doit être compris entre 1 et 5.")
        return self.quantities[stars - 1]

    @property
    def is_empty(self) -> bool:
        return not any(self.quantities)


@dataclass(frozen=True, slots=True)
class ProductionPlan:
    requested_tokens: tuple[int, int, int, int, int]
    tokens_to_extract: tuple[int, int, int, int, int]
    pets_to_level: tuple[int, int, int, int, int]
    upgrades: tuple[int, int, int, int]
    chickens_required: int

    def extracted(self, stars: int) -> int:
        return self.tokens_to_extract[stars - 1]

    def levelled(self, stars: int) -> int:
        return self.pets_to_level[stars - 1]
