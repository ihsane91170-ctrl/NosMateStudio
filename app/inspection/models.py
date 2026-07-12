from __future__ import annotations

from dataclasses import dataclass

from app.inventory.models import PetInstance
from app.perception.models import DetectedPet


@dataclass(frozen=True, slots=True)
class InspectedPet:
    detection: DetectedPet
    stars: int
    stars_confidence: float
    level: int | None = None
    level_confidence: float | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.stars <= 6:
            raise ValueError(
                "Le nombre d'étoiles doit être compris entre 1 et 6."
            )

        self._validate_confidence(
            self.stars_confidence,
            "étoiles",
        )

        if self.level is not None:
            if not 1 <= self.level <= 99:
                raise ValueError(
                    "Le niveau doit être compris entre 1 et 99."
                )

            if self.level_confidence is None:
                raise ValueError(
                    "La confiance du niveau est obligatoire "
                    "lorsqu'un niveau est fourni."
                )

        if self.level_confidence is not None:
            self._validate_confidence(
                self.level_confidence,
                "niveau",
            )

    @property
    def profile(self):
        return self.detection.profile

    @property
    def center(self) -> tuple[int, int]:
        return self.detection.center

    @property
    def confidence(self) -> float:
        confidences = [
            self.detection.visible_pet.confidence,
            self.stars_confidence,
        ]

        if self.level_confidence is not None:
            confidences.append(self.level_confidence)

        return min(confidences)

    def to_pet_instance(
        self,
        *,
        locked: bool = False,
        favorite: bool = False,
    ) -> PetInstance:
        return PetInstance(
            profile=self.profile,
            level=self.level or 1,
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

@dataclass(frozen=True, slots=True)
class RegionOfInterest:
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

    def to_box(self) -> tuple[int, int, int, int]:
        return (
            self.left,
            self.top,
            self.right,
            self.bottom,
        )


@dataclass(frozen=True, slots=True)
class InspectionRegions:
    name: RegionOfInterest
    stars: RegionOfInterest
    level: RegionOfInterest