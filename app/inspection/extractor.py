from __future__ import annotations

from app.inspection.models import (
    InspectionRegions,
    RegionOfInterest,
)
from app.perception.models import DetectedPet


class RegionExtractor:

    NAME_OFFSET_X = 48
    NAME_OFFSET_Y = 2
    NAME_WIDTH = 135
    NAME_HEIGHT = 18

    STARS_OFFSET_X = 210
    STARS_OFFSET_Y = 2
    STARS_WIDTH = 90
    STARS_HEIGHT = 18

    LEVEL_OFFSET_X = 308
    LEVEL_OFFSET_Y = 2
    LEVEL_WIDTH = 42
    LEVEL_HEIGHT = 18

    def extract(
        self,
        pet: DetectedPet,
    ) -> InspectionRegions:

        left = pet.visible_pet.left
        top = pet.visible_pet.top

        return InspectionRegions(
            name=RegionOfInterest(
                left + self.NAME_OFFSET_X,
                top + self.NAME_OFFSET_Y,
                self.NAME_WIDTH,
                self.NAME_HEIGHT,
            ),
            stars=RegionOfInterest(
                left + self.STARS_OFFSET_X,
                top + self.STARS_OFFSET_Y,
                self.STARS_WIDTH,
                self.STARS_HEIGHT,
            ),
            level=RegionOfInterest(
                left + self.LEVEL_OFFSET_X,
                top + self.LEVEL_OFFSET_Y,
                self.LEVEL_WIDTH,
                self.LEVEL_HEIGHT,
            ),
        )