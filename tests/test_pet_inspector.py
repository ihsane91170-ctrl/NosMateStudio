import pytest
from PIL import Image

from app.inspection import (
    InspectionRegions,
    PetInspectionError,
    PetInspector,
    RegionOfInterest,
    StarsReading,
)
from app.inventory import PetProfile
from app.perception import DetectedPet
from app.pets.models import VisiblePet


class RegionExtractorFake:
    def extract(self, detection):
        return InspectionRegions(
            name=RegionOfInterest(0, 0, 50, 20),
            stars=RegionOfInterest(50, 0, 90, 20),
            level=RegionOfInterest(140, 0, 40, 20),
        )


class StarsReaderFake:
    def __init__(self, reading):
        self.reading = reading
        self.received_region = None

    def read(self, screenshot, region):
        self.received_region = region
        return self.reading


def detected_pet() -> DetectedPet:
    return DetectedPet(
        visible_pet=VisiblePet(
            index=1,
            left=100,
            top=200,
            width=200,
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


def test_inspector_reads_pet_stars() -> None:
    stars_reader = StarsReaderFake(
        StarsReading(
            stars=4,
            confidence=0.96,
            template_name="stars_4",
        )
    )

    inspector = PetInspector(
        RegionExtractorFake(),
        stars_reader,
    )

    result = inspector.inspect(
        Image.new("RGB", (500, 300)),
        detected_pet(),
    )

    assert result.profile.id == "ratufu"
    assert result.stars == 4
    assert result.level is None
    assert result.stars_confidence == 0.96
    assert result.to_pet_instance().needs_upgrade is True


def test_inspector_fails_when_stars_are_unknown() -> None:
    inspector = PetInspector(
        RegionExtractorFake(),
        StarsReaderFake(None),
    )

    with pytest.raises(PetInspectionError):
        inspector.inspect(
            Image.new("RGB", (500, 300)),
            detected_pet(),
        )