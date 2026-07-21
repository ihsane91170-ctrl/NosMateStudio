from __future__ import annotations

from dataclasses import dataclass

UPGRADE_TOKEN_COSTS: dict[int, int] = {1: 1, 2: 2, 3: 3, 4: 3, 5: 4}
MIN_STARS = 1
MAX_STARS = 6


@dataclass(frozen=True, slots=True)
class TokenBatch:
    stars: int
    quantity: int

    @property
    def extraction_level(self) -> int:
        return self.stars * 10


@dataclass(frozen=True, slots=True)
class ProductionPlan:
    target_quantity: int
    target_stars: int
    batches: tuple[TokenBatch, ...]

    @property
    def chickens_to_capture(self) -> int:
        return sum(batch.quantity for batch in self.batches)

    def quantity_for(self, stars: int) -> int:
        return next((batch.quantity for batch in self.batches if batch.stars == stars), 0)


class ProductionPlanner:
    """Calcule tous les lots à extraire pour produire des jetons cibles.

    Chaque poule extraite produit un jeton de son étoile. Les poules utilisées
    pour produire les jetons intermédiaires doivent elles-mêmes être montées
    depuis 1 étoile, ce qui rend le calcul récursif.
    """

    def plan(self, quantity: int, stars: int) -> ProductionPlan:
        if quantity <= 0:
            raise ValueError("La quantité doit être strictement positive.")
        if not MIN_STARS <= stars <= MAX_STARS:
            raise ValueError(f"Le niveau d'étoiles doit être compris entre {MIN_STARS} et {MAX_STARS}.")

        needs = {level: 0 for level in range(MIN_STARS, stars + 1)}
        needs[stars] = quantity

        for level in range(stars - 1, MIN_STARS - 1, -1):
            hens_requiring_upgrade = sum(needs[higher] for higher in range(level + 1, stars + 1))
            needs[level] = UPGRADE_TOKEN_COSTS[level] * hens_requiring_upgrade

        batches = tuple(TokenBatch(level, needs[level]) for level in range(MIN_STARS, stars + 1))
        return ProductionPlan(quantity, stars, batches)
