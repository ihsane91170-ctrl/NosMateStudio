from __future__ import annotations

from dataclasses import dataclass

from app.inventory.models import PetProfile
from app.pets.models import VisiblePet


@dataclass(frozen=True, slots=True)
class DetectedPet:
    visible_pet: VisiblePet
    profile: PetProfile
    template_name: str

    @property
    def center(self) -> tuple[int, int]:
        return self.visible_pet.center