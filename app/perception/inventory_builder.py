from __future__ import annotations

from app.inventory.models import Inventory, PetInstance
from app.perception.models import DetectedPet


class InventoryBuilder:
    def build(
        self,
        detections: tuple[DetectedPet, ...],
    ) -> Inventory:
        inventory = Inventory()

        for detection in detections:
            inventory.add(
                PetInstance(
                    profile=detection.profile,
                    level=1,
                    stars=(
                        0
                        if detection.profile.disposable
                        else 1
                    ),
                )
            )

        return inventory