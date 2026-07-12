from PIL import Image

from app.inspection import (
    InspectedPet,
    InventoryInspector,
    PetInspectionError,
)
from app.inventory import PetProfile
from app.perception import DetectedPet
from app.pets.models import VisiblePet


def build_detection(
    index: int,
    profile_id: str,
) -> DetectedPet:
    return DetectedPet(
        visible_pet=VisiblePet(
            index=index,
            left=100,
            top=100 + index * 40,
            width=80,
            height=30,
            confidence=0.97,
        ),
        profile=PetProfile(
            id=profile_id,
            display_name=profile_id.title(),
            disposable=profile_id == "chicken",
            desired_stars=0 if profile_id == "chicken" else 6,
            template_name=f"pet_{profile_id}_row",
        ),
        template_name=f"pet_{profile_id}_row",
    )


class PetInspectorFake:
    def __init__(
        self,
        failures: set[str] | None = None,
    ) -> None:
        self.failures = failures or set()
        self.calls: list[str] = []

    def inspect(
        self,
        screenshot: Image.Image,
        detection: DetectedPet,
    ) -> InspectedPet:
        profile_id = detection.profile.id
        self.calls.append(profile_id)

        if profile_id in self.failures:
            raise PetInspectionError(
                f"Inspection impossible pour {profile_id}."
            )

        return InspectedPet(
            detection=detection,
            stars=1 if profile_id == "chicken" else 4,
            stars_confidence=0.96,
        )


def test_inventory_inspector_inspects_all_detections() -> None:
    pet_inspector = PetInspectorFake()

    detections = (
        build_detection(1, "chicken"),
        build_detection(2, "ratufu"),
    )

    result = InventoryInspector(
        pet_inspector,
    ).inspect_all(
        Image.new("RGB", (1280, 720)),
        detections,
    )

    assert result.total == 2
    assert result.success_count == 2
    assert result.failure_count == 0

    assert tuple(
        pet.profile.id
        for pet in result.inspected_pets
    ) == (
        "chicken",
        "ratufu",
    )

    assert pet_inspector.calls == [
        "chicken",
        "ratufu",
    ]


def test_inventory_inspector_keeps_failures_separate() -> None:
    pet_inspector = PetInspectorFake(
        failures={"ratufu"},
    )

    detections = (
        build_detection(1, "chicken"),
        build_detection(2, "ratufu"),
    )

    result = InventoryInspector(
        pet_inspector,
    ).inspect_all(
        Image.new("RGB", (1280, 720)),
        detections,
    )

    assert result.total == 2
    assert result.success_count == 1
    assert result.failure_count == 1

    assert result.inspected_pets[0].profile.id == "chicken"
    assert result.failures[0].detection.profile.id == "ratufu"
    assert (
        result.failures[0].message
        == "Inspection impossible pour ratufu."
    )


def test_inventory_inspector_handles_empty_detection_list() -> None:
    result = InventoryInspector(
        PetInspectorFake(),
    ).inspect_all(
        Image.new("RGB", (1280, 720)),
        (),
    )

    assert result.total == 0
    assert result.inspected_pets == ()
    assert result.failures == ()