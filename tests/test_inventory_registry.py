from app.inventory import (
    PetProfile,
    PetProfileRegistry,
    PetProfileResolver,
)
from app.pets.models import VisiblePet


def test_resolver_creates_pet_instance_from_template() -> None:
    registry = PetProfileRegistry()

    registry.register(
        PetProfile(
            id="chicken",
            display_name="Poule",
            disposable=True,
            desired_stars=0,
            template_name="pet_chicken_row",
        )
    )

    resolver = PetProfileResolver(registry)

    visible_pet = VisiblePet(
        index=1,
        left=100,
        top=200,
        width=80,
        height=30,
        confidence=0.97,
    )

    pet = resolver.resolve(
        visible_pet,
        template_name="pet_chicken_row",
        level=12,
        stars=0,
    )

    assert pet.profile.id == "chicken"
    assert pet.profile.display_name == "Poule"
    assert pet.level == 12
    assert pet.stars == 0
    assert pet.can_be_sacrificed is True


def test_resolver_can_create_protected_instance() -> None:
    registry = PetProfileRegistry()

    registry.register(
        PetProfile(
            id="ratufu",
            display_name="Ratufu",
            disposable=False,
            desired_stars=6,
            template_name="pet_ratufu_row",
        )
    )

    resolver = PetProfileResolver(registry)

    visible_pet = VisiblePet(
        index=1,
        left=100,
        top=200,
        width=80,
        height=30,
        confidence=0.95,
    )

    pet = resolver.resolve(
        visible_pet,
        template_name="pet_ratufu_row",
        level=80,
        stars=3,
    )

    assert pet.profile.id == "ratufu"
    assert pet.can_be_sacrificed is False
    assert pet.needs_upgrade is True