from app.inventory import PetProfile
from app.perception import DetectedPet, InventoryBuilder
from app.pets.models import VisiblePet


def test_builder_creates_inventory_from_detections() -> None:
    chicken = PetProfile(
        id="chicken",
        display_name="Poule",
        disposable=True,
        desired_stars=0,
        template_name="pet_chicken_row",
    )

    ratufu = PetProfile(
        id="ratufu",
        display_name="Ratufu",
        disposable=False,
        desired_stars=6,
        template_name="pet_ratufu_row",
    )

    detections = (
        DetectedPet(
            visible_pet=VisiblePet(
                index=1,
                left=10,
                top=20,
                width=30,
                height=40,
                confidence=0.98,
            ),
            profile=chicken,
            template_name="pet_chicken_row",
        ),
        DetectedPet(
            visible_pet=VisiblePet(
                index=2,
                left=10,
                top=80,
                width=30,
                height=40,
                confidence=0.95,
            ),
            profile=ratufu,
            template_name="pet_ratufu_row",
        ),
    )

    inventory = InventoryBuilder().build(detections)

    assert len(inventory) == 2
    assert inventory.count("chicken") == 1
    assert inventory.count("ratufu") == 1
    assert len(inventory.disposable_pets()) == 1
    assert len(inventory.protected_pets()) == 1