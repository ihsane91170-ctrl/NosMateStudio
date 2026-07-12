from __future__ import annotations

from app.inventory import Inventory, PetInstance
from app.planning.models import (
    FarmTokensAction,
    PlanningAction,
    StopAction,
    UpgradePetAction,
)

UPGRADE_COSTS: dict[int, int] = {
    1: 1,
    2: 2,
    3: 3,
    4: 3,
    5: 4,
}


class UpgradePlanner:
    def plan(
        self,
        inventory: Inventory,
        *,
        tokens: int,
        goal_profile_id: str,
    ) -> PlanningAction:
        if tokens < 0:
            raise ValueError(
                "Le nombre de jetons ne peut pas être négatif."
            )

        goal_pet = self._find_goal_pet(
            inventory,
            goal_profile_id,
        )

        if goal_pet is None:
            return StopAction(
                reason=(
                    f"Aucun familier {goal_profile_id!r} "
                    "n'est présent dans l'inventaire."
                )
            )

        if not goal_pet.needs_upgrade:
            return StopAction(
                reason=(
                    f"L'objectif est atteint pour "
                    f"{goal_pet.profile.display_name}."
                )
            )

        try:
            cost = UPGRADE_COSTS[goal_pet.stars]
        except KeyError as exc:
            raise ValueError(
                
                    "Impossible de calculer le coût pour un familier "
                    f"à {goal_pet.stars} étoile(s)."
                
            ) from exc

        if tokens >= cost:
            return UpgradePetAction(
                profile_id=goal_pet.profile.id,
                current_stars=goal_pet.stars,
                target_stars=goal_pet.stars + 1,
                cost=cost,
            )

        return FarmTokensAction(
            required_tokens=cost,
            missing_tokens=cost - tokens,
        )

    @staticmethod
    def _find_goal_pet(
        inventory: Inventory,
        goal_profile_id: str,
    ) -> PetInstance | None:
        normalized_id = goal_profile_id.strip().lower()

        if not normalized_id:
            raise ValueError(
                "L'identifiant du familier objectif "
                "ne peut pas être vide."
            )

        candidates = [
            pet
            for pet in inventory
            if pet.profile.id == normalized_id
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda pet: pet.stars,
        )