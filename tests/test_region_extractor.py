from app.inspection import RegionExtractor
from app.inventory import PetProfile
from app.perception import DetectedPet
from app.pets.models import VisiblePet


def build_detected_pet():

    return DetectedPet(
        visible_pet=VisiblePet(
            index=1,
            left=100,
            top=200,
            width=360,
            height=22,
            confidence=0.98,
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


def test_region_extractor_builds_regions():

    extractor = RegionExtractor()

    regions = extractor.extract(
        build_detected_pet()
    )

    assert regions.name.left == 148
    assert regions.name.top == 202

    assert regions.stars.left == 310
    assert regions.level.left == 408


def test_regions_have_positive_size():

    regions = RegionExtractor().extract(
        build_detected_pet()
    )

    assert regions.name.width > 0
    assert regions.name.height > 0

    assert regions.stars.width > 0
    assert regions.level.width > 0