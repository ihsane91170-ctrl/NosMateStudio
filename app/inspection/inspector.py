from __future__ import annotations

from PIL import Image

from app.inspection.extractor import RegionExtractor
from app.inspection.models import InspectedPet
from app.inspection.stars_reader import StarsReader
from app.perception.models import DetectedPet


class PetInspectionError(RuntimeError):
    """Raised when a detected pet cannot be inspected reliably."""


class PetInspector:
    def __init__(
        self,
        region_extractor: RegionExtractor,
        stars_reader: StarsReader,
    ) -> None:
        self._region_extractor = region_extractor
        self._stars_reader = stars_reader

    def inspect(
        self,
        screenshot: Image.Image,
        detection: DetectedPet,
    ) -> InspectedPet:
        regions = self._region_extractor.extract(detection)

        stars_reading = self._stars_reader.read(
            screenshot,
            regions.stars,
        )

        if stars_reading is None:
            raise PetInspectionError(
                "Impossible de déterminer le nombre d'étoiles."
            )

        return InspectedPet(
            detection=detection,
            stars=stars_reading.stars,
            stars_confidence=stars_reading.confidence,
        )