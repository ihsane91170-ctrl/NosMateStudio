from __future__ import annotations

from app.inventory.models import PetInstance
from app.inventory.registry import PetProfileRegistry
from app.pets.models import VisiblePet


class PetProfileResolver:
    def __init__(
        self,
        registry: PetProfileRegistry,
    ) -> None:
        self._registry = registry

    def resolve(
        self,
        visible_pet: VisiblePet,
        *,
        template_name: str,
        level: int = 1,
        stars: int = 1,
        locked: bool = False,
        favorite: bool = False,
    ) -> PetInstance:
        profile = self._registry.get_by_template(
            template_name
        )

        return PetInstance(
            profile=profile,
            level=level,
            stars=stars,
            locked=locked,
            favorite=favorite,
        )