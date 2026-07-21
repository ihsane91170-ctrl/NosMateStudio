from __future__ import annotations

from app.production.models import ProductionPlan, TokenGoal

# Nombre de jetons du niveau courant consommés pour passer au niveau suivant.
UPGRADE_COSTS: tuple[int, int, int, int] = (1, 2, 3, 3)


class TokenProductionPlanner:
    """Calcule la chaîne complète sans piloter le jeu."""

    def build(self, goal: TokenGoal) -> ProductionPlan:
        requested = list(goal.quantities)
        to_extract = requested.copy()
        upgrades = [0, 0, 0, 0]

        # Une poule destinée à un jeton N★ doit elle-même atteindre N★.
        # Pour créer ces poules, on ajoute récursivement les jetons requis
        # aux étages inférieurs.
        for lower_stars in range(4, 0, -1):
            # Tous les familiers destinés à finir au-dessus de ce palier
            # doivent franchir l'amélioration lower_stars -> lower_stars + 1.
            pets_crossing_boundary = sum(to_extract[lower_stars:])
            upgrades[lower_stars - 1] = pets_crossing_boundary
            to_extract[lower_stars - 1] += (
                pets_crossing_boundary * UPGRADE_COSTS[lower_stars - 1]
            )

        pets_to_level = to_extract.copy()
        chickens_required = sum(pets_to_level)

        return ProductionPlan(
            requested_tokens=tuple(requested),
            tokens_to_extract=tuple(to_extract),
            pets_to_level=tuple(pets_to_level),
            upgrades=tuple(upgrades),
            chickens_required=chickens_required,
        )
