import pytest

from app.inspection import InspectedPet
from app.inventory import PetProfile
from app.perception import DetectedPet
from app.pets.models import VisiblePet


def detected_ratufu() -> DetectedPet:
    return DetectedPet(
        visible_pet=VisiblePet(
            index=1,
            left=100,
            top=200,
            width=80,
            height=30,
            confidence=0.97,
        ),
        profile=PetProfile(
            id="ratufu",
            display_name="Ratufu",
            disposable=False,
            desired_stars=6,
            template_name="pet_ratufu_row",
        ),
        template_name="pet_ratufu_row",
    )


def test_inspected_pet_exposes_detection_data() -> None:
    pet = InspectedPet(
        detection=detected_ratufu(),
        level=81,
        stars=4,
        level_confidence=0.94,
        stars_confidence=0.98,
    )

    assert pet.profile.id == "ratufu"
    assert pet.center == (140, 215)
    assert pet.level == 81
    assert pet.stars == 4
    assert pet.confidence == 0.94


def test_inspected_pet_creates_domain_instance() -> None:
    inspected = InspectedPet(
        detection=detected_ratufu(),
        level=81,
        stars=4,
        level_confidence=0.95,
        stars_confidence=0.96,
    )

    instance = inspected.to_pet_instance(
        locked=True,
    )

    assert instance.profile.id == "ratufu"
    assert instance.level == 81
    assert instance.stars == 4
    assert instance.locked is True
    assert instance.can_be_sacrificed is False
    assert instance.needs_upgrade is True


@pytest.mark.parametrize(
    ("level", "stars"),
    [
        (0, 3),
        (100, 3),
        (50, -1),
        (50, 7),
    ],
)
def test_inspected_pet_rejects_invalid_values(
    level: int,
    stars: int,
) -> None:
    with pytest.raises(ValueError):
        InspectedPet(
            detection=detected_ratufu(),
            level=level,
            stars=stars,
            level_confidence=0.90,
            stars_confidence=0.90,
        )


@pytest.mark.parametrize(
    ("level_confidence", "stars_confidence"),
    [
        (-0.1, 0.90),
        (1.1, 0.90),
        (0.90, -0.1),
        (0.90, 1.1),
    ],
)
def test_inspected_pet_rejects_invalid_confidence(
    level_confidence: float,
    stars_confidence: float,
) -> None:
    with pytest.raises(ValueError):
        InspectedPet(
            detection=detected_ratufu(),
            level=50,
            stars=3,
            level_confidence=level_confidence,
            stars_confidence=stars_confidence,
        )