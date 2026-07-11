from __future__ import annotations

from typing import Protocol

from app.pets.models import VisiblePet
from app.vision.match import TemplateMatch


class VisionProtocol(Protocol):
    def find_all(
        self,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]:
        ...


class PetScanner:
    def __init__(
        self,
        vision: VisionProtocol,
        *,
        template_name: str = "pet_row",
        threshold: float = 0.80,
        minimum_distance: int = 40,
    ) -> None:
        self._vision = vision
        self._template_name = template_name
        self._threshold = threshold
        self._minimum_distance = minimum_distance

    def scan(self) -> tuple[VisiblePet, ...]:
        matches = self._vision.find_all(
            self._template_name,
            threshold=self._threshold,
            minimum_distance=self._minimum_distance,
        )

        ordered = sorted(
            matches,
            key=lambda match: (
                match.top,
                match.left,
            ),
        )

        return tuple(
            VisiblePet(
                index=index,
                left=match.left,
                top=match.top,
                width=match.width,
                height=match.height,
                confidence=match.confidence,
            )
            for index, match in enumerate(ordered, start=1)
        )