from __future__ import annotations

from typing import Protocol

from app.inventory.registry import PetProfileRegistry
from app.perception.models import DetectedPet
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


class MultiPetScanner:
    def __init__(
        self,
        vision: VisionProtocol,
        registry: PetProfileRegistry,
        *,
        threshold: float = 0.80,
        minimum_distance: int = 20,
    ) -> None:
        self._vision = vision
        self._registry = registry
        self._threshold = threshold
        self._minimum_distance = minimum_distance

    def scan(self) -> tuple[DetectedPet, ...]:
        detections: list[DetectedPet] = []

        for profile in self._registry.all():
            if profile.template_name is None:
                continue

            matches = self._vision.find_all(
                profile.template_name,
                threshold=self._threshold,
                minimum_distance=self._minimum_distance,
            )

            for match in matches:
                detections.append(
                    DetectedPet(
                        visible_pet=VisiblePet(
                            index=0,
                            left=match.left,
                            top=match.top,
                            width=match.width,
                            height=match.height,
                            confidence=match.confidence,
                        ),
                        profile=profile,
                        template_name=profile.template_name,
                    )
                )

        detections.sort(
            key=lambda detection: (
                detection.visible_pet.top,
                detection.visible_pet.left,
                detection.profile.id,
            )
        )

        return tuple(
            DetectedPet(
                visible_pet=VisiblePet(
                    index=index,
                    left=detection.visible_pet.left,
                    top=detection.visible_pet.top,
                    width=detection.visible_pet.width,
                    height=detection.visible_pet.height,
                    confidence=detection.visible_pet.confidence,
                ),
                profile=detection.profile,
                template_name=detection.template_name,
            )
            for index, detection in enumerate(detections, start=1)
        )