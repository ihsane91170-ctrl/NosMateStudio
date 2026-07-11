from __future__ import annotations

from dataclasses import dataclass

from app.inventory.models import PetInstance
from app.perception.models import DetectedPet


@dataclass(frozen=True, slots=True)
class InspectedPet:
    detection: DetectedPet
    level: int
    stars: int
    level_confidence: float
    stars_confidence: float

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 99:
            raise ValueError(
                "Le niveau doit être compris entre 1 et 99."
            )

        if not 0 <= self.stars <= 6:
            raise ValueError(
                "Le nombre d'étoiles doit être compris entre 0 et 6."
            )

        self._validate_confidence(
            self.level_confidence,
            "niveau",
        )
        self._validate_confidence(
            self.stars_confidence,
            "étoiles",
        )

    @property
    def profile(self):
        return self.detection.profile

    @property
    def center(self) -> tuple[int, int]:
        return self.detection.center

    @property
    def confidence(self) -> float:
        return min(
            self.detection.visible_pet.confidence,
            self.level_confidence,
            self.stars_confidence,
        )

    def to_pet_instance(
        self,
        *,
        locked: bool = False,
        favorite: bool = False,
    ) -> PetInstance:
        return PetInstance(
            profile=self.profile,
            level=self.level,
            stars=self.stars,
            locked=locked,
            favorite=favorite,
        )

    @staticmethod
    def _validate_confidence(
        confidence: float,
        label: str,
    ) -> None:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                f"La confiance de lecture du {label} "
                "doit être comprise entre 0 et 1."
            )