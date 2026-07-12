from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PIL import Image

from app.inspection.models import RegionOfInterest
from app.vision.match import TemplateMatch


class MatcherProtocol(Protocol):
    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> TemplateMatch | None:
        ...


@dataclass(frozen=True, slots=True)
class StarsReading:
    stars: int
    confidence: float
    template_name: str


class StarsReader:
    def __init__(
        self,
        matcher: MatcherProtocol,
        *,
        threshold: float = 0.85,
        template_prefix: str = "stars_",
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "Le seuil doit être compris entre 0 et 1."
            )

        self._matcher = matcher
        self._threshold = threshold
        self._template_prefix = template_prefix

    def read(
        self,
        screenshot: Image.Image,
        region: RegionOfInterest,
    ) -> StarsReading | None:
        cropped = screenshot.crop(region.to_box())

        best_reading: StarsReading | None = None

        for stars in range(1, 7):
            template_name = f"{self._template_prefix}{stars}"

            match = self._matcher.find(
                cropped,
                template_name,
                threshold=self._threshold,
            )

            if match is None:
                continue

            reading = StarsReading(
                stars=stars,
                confidence=match.confidence,
                template_name=template_name,
            )

            if (
                best_reading is None
                or reading.confidence > best_reading.confidence
            ):
                best_reading = reading

        return best_reading