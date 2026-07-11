import pytest

from app.inventory import (
    Inventory,
    PetInstance,
    PetProfile,
)


def chicken_profile() -> PetProfile:
    return PetProfile(
        id="chicken",
        display_name="Poule",
        disposable=True,
        desired_stars=0,
    )


def ratufu_profile() -> PetProfile:
    return PetProfile(
        id="ratufu",
        display_name="Ratufu",
        disposable=False,
        desired_stars=6,
    )


def test_pet_profile_normalizes_values() -> None:
    profile = PetProfile(
        id=" Chicken ",
        display_name=" Poule ",
        disposable=True,
        desired_stars=0,
    )

    assert profile.id == "chicken"
    assert profile.display_name == "Poule"


def test_disposable_pet_can_be_sacrificed() -> None:
    pet = PetInstance(
        profile=chicken_profile(),
        stars=0,
    )

    assert pet.can_be_sacrificed is True


@pytest.mark.parametrize(
    ("locked", "favorite"),
    [
        (True, False),
        (False, True),
        (True, True),
    ],
)
def test_locked_or_favorite_pet_cannot_be_sacrificed(
    locked: bool,
    favorite: bool,
) -> None:
    pet = PetInstance(
        profile=chicken_profile(),
        stars=0,
        locked=locked,
        favorite=favorite,
    )

    assert pet.can_be_sacrificed is False


def test_protected_pet_cannot_be_sacrificed() -> None:
    pet = PetInstance(
        profile=ratufu_profile(),
        stars=3,
    )

    assert pet.can_be_sacrificed is False


def test_pet_needs_upgrade_until_desired_stars() -> None:
    pet = PetInstance(
        profile=ratufu_profile(),
        stars=3,
    )

    assert pet.needs_upgrade is True

    pet.stars = 6

    assert pet.needs_upgrade is False


def test_inventory_counts_and_filters_pets() -> None:
    inventory = Inventory()

    inventory.add(
        PetInstance(
            profile=chicken_profile(),
            stars=0,
        )
    )
    inventory.add(
        PetInstance(
            profile=chicken_profile(),
            stars=0,
            locked=True,
        )
    )
    inventory.add(
        PetInstance(
            profile=ratufu_profile(),
            stars=3,
        )
    )

    assert len(inventory) == 3
    assert inventory.count("chicken") == 2
    assert inventory.count("ratufu") == 1
    assert len(inventory.disposable_pets()) == 1
    assert len(inventory.protected_pets()) == 2
    assert len(inventory.pets_needing_upgrade()) == 1


def test_inventory_removes_pet() -> None:
    inventory = Inventory()
    pet = PetInstance(
        profile=ratufu_profile(),
        stars=3,
    )

    inventory.add(pet)
    inventory.remove(pet)

    assert len(inventory) == 0


def test_inventory_rejects_removing_unknown_pet() -> None:
    inventory = Inventory()
    pet = PetInstance(
        profile=ratufu_profile(),
        stars=3,
    )

    with pytest.raises(ValueError):
        inventory.remove(pet)

def test_pet_profile_normalizes_template_name() -> None:
    profile = PetProfile(
        id="chicken",
        display_name="Poule",
        disposable=True,
        desired_stars=0,
        template_name=" pet_chicken_row ",
    )

    assert profile.template_name == "pet_chicken_row"