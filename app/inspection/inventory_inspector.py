from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from app.inspection.inspector import (
    PetInspectionError,
    PetInspector,
)
from app.inspection.models import InspectedPet
from app.perception.models import DetectedPet


@dataclass(frozen=True, slots=True)
class InspectionFailure:
    detection: DetectedPet
    message: str


@dataclass(frozen=True, slots=True)
class InventoryInspectionResult:
    inspected_pets: tuple[InspectedPet, ...]
    failures: tuple[InspectionFailure, ...]

    @property
    def total(self) -> int:
        return len(self.inspected_pets) + len(self.failures)

    @property
    def success_count(self) -> int:
        return len(self.inspected_pets)

    @property
    def failure_count(self) -> int:
        return len(self.failures)


class InventoryInspector:
    def __init__(
        self,
        pet_inspector: PetInspector,
    ) -> None:
        self._pet_inspector = pet_inspector

    def inspect_all(
        self,
        screenshot: Image.Image,
        detections: tuple[DetectedPet, ...],
    ) -> InventoryInspectionResult:
        inspected: list[InspectedPet] = []
        failures: list[InspectionFailure] = []

        for detection in detections:
            try:
                inspected.append(
                    self._pet_inspector.inspect(
                        screenshot,
                        detection,
                    )
                )
            except PetInspectionError as exc:
                failures.append(
                    InspectionFailure(
                        detection=detection,
                        message=str(exc),
                    )
                )

        return InventoryInspectionResult(
            inspected_pets=tuple(inspected),
            failures=tuple(failures),
        )