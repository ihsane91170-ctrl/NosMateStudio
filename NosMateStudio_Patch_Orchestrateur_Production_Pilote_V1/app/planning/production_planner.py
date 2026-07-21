from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

UPGRADE_TOKEN_COSTS: Mapping[int, int] = MappingProxyType(
    {
        1: 1,
        2: 2,
        3: 3,
        4: 3,
        5: 4,
    }
)

PROTOMONSTER_LEVEL_CAPS: Mapping[str, int] = MappingProxyType(
    {
        "weak": 20,
        "normal": 40,
        "strong": 60,
    }
)

MIN_TOKEN_STARS = 1
MAX_TOKEN_STARS = 6


@dataclass(frozen=True, slots=True)
class TokenBatch:
    """Lot de poules élevé puis extrait pour produire un type de jeton."""

    stars: int
    quantity: int
    max_level: int


@dataclass(frozen=True, slots=True)
class UpgradeRequirement:
    """Besoin d'amélioration pour toutes les poules traversant un palier."""

    from_stars: int
    to_stars: int
    chickens_to_upgrade: int
    token_cost_per_chicken: int
    required_tokens: int


@dataclass(frozen=True, slots=True)
class ProductionPlan:
    """Plan métier complet, indépendant de Windows et de l'interface graphique."""

    target_quantity: int
    target_stars: int
    batches: tuple[TokenBatch, ...]
    upgrades: tuple[UpgradeRequirement, ...]
    chickens_to_capture: int

    def token_quantity(self, stars: int) -> int:
        for batch in self.batches:
            if batch.stars == stars:
                return batch.quantity
        return 0


class TokenProductionPlanner:
    """Calcule les lots intermédiaires nécessaires à un objectif de jetons."""

    def plan(self, quantity: int, stars: int) -> ProductionPlan:
        self._validate(quantity=quantity, stars=stars)

        if quantity == 0:
            return ProductionPlan(
                target_quantity=0,
                target_stars=stars,
                batches=(),
                upgrades=(),
                chickens_to_capture=0,
            )

        token_batches: dict[int, int] = {stars: quantity}
        upgrade_requirements: list[UpgradeRequirement] = []

        # Pour produire un jeton S★, une poule S★ doit être extraite au niveau 10*S.
        # Chaque lot destiné à un niveau supérieur traverse tous les paliers inférieurs.
        for current_stars in range(stars - 1, 0, -1):
            chickens_to_upgrade = sum(
                batch_quantity
                for batch_stars, batch_quantity in token_batches.items()
                if batch_stars > current_stars
            )
            cost = UPGRADE_TOKEN_COSTS[current_stars]
            required_tokens = chickens_to_upgrade * cost
            token_batches[current_stars] = required_tokens
            upgrade_requirements.append(
                UpgradeRequirement(
                    from_stars=current_stars,
                    to_stars=current_stars + 1,
                    chickens_to_upgrade=chickens_to_upgrade,
                    token_cost_per_chicken=cost,
                    required_tokens=required_tokens,
                )
            )

        batches = tuple(
            TokenBatch(
                stars=batch_stars,
                quantity=token_batches[batch_stars],
                max_level=chicken_level_cap(batch_stars),
            )
            for batch_stars in sorted(token_batches)
        )

        return ProductionPlan(
            target_quantity=quantity,
            target_stars=stars,
            batches=batches,
            upgrades=tuple(reversed(upgrade_requirements)),
            chickens_to_capture=sum(batch.quantity for batch in batches),
        )

    @staticmethod
    def _validate(*, quantity: int, stars: int) -> None:
        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise TypeError("La quantité doit être un entier.")
        if isinstance(stars, bool) or not isinstance(stars, int):
            raise TypeError("Le niveau de jeton doit être un entier.")
        if quantity < 0:
            raise ValueError("La quantité ne peut pas être négative.")
        if not MIN_TOKEN_STARS <= stars <= MAX_TOKEN_STARS:
            raise ValueError(
                f"Le niveau de jeton doit être compris entre "
                f"{MIN_TOKEN_STARS} et {MAX_TOKEN_STARS} étoiles."
            )


def chicken_level_cap(stars: int) -> int:
    """Retourne le niveau maximal d'une poule pour son nombre d'étoiles."""

    if isinstance(stars, bool) or not isinstance(stars, int):
        raise TypeError("Le nombre d'étoiles doit être un entier.")
    if not MIN_TOKEN_STARS <= stars <= MAX_TOKEN_STARS:
        raise ValueError(
            f"Le nombre d'étoiles doit être compris entre "
            f"{MIN_TOKEN_STARS} et {MAX_TOKEN_STARS}."
        )
    return stars * 10
