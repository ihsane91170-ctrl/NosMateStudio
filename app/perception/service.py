from __future__ import annotations

from app.inventory.models import Inventory
from app.inventory.registry import PetProfileRegistry
from app.perception.inventory_builder import InventoryBuilder
from app.perception.models import DetectedPet
from app.perception.scanner import MultiPetScanner


class PerceptionService:
    def __init__(
        self,
        scanner: MultiPetScanner,
        inventory_builder: InventoryBuilder,
        registry: PetProfileRegistry,
    ) -> None:
        self._scanner = scanner
        self._inventory_builder = inventory_builder
        self._registry = registry

    def detect_pets(self) -> tuple[DetectedPet, ...]:
        return self._scanner.scan()

    def build_inventory(self) -> Inventory:
        return self._inventory_builder.build(
            self.detect_pets()
        )

    @property
    def registry(self) -> PetProfileRegistry:
        return self._registry