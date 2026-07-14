from PIL import Image

from app.inspection import (
    RegionOfInterest,
    StarsReader,
)
from app.vision.match import TemplateMatch


class MatcherFake:
    def __init__(
        self,
        confidences: dict[str, float],
    ) -> None:
        self.confidences = confidences
        self.calls: list[
            tuple[tuple[int, int], str, float | None]
        ] = []

    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> TemplateMatch | None:
        self.calls.append(
            (
                screenshot.size,
                template_name,
                threshold,
            )
        )

        confidence = self.confidences.get(template_name)

        if confidence is None:
            return None

        if threshold is not None and confidence < threshold:
            return None

        return TemplateMatch(
            template_name=template_name,
            confidence=confidence,
            left=0,
            top=0,
            width=20,
            height=10,
        )


def test_stars_reader_returns_best_match() -> None:
    matcher = MatcherFake(
        {
            "stars_3": 0.91,
            "stars_4": 0.97,
        }
    )

    reader = StarsReader(
        matcher,
        threshold=0.85,
    )

    reading = reader.read(
        Image.new("RGB", (500, 300)),
        RegionOfInterest(
            left=100,
            top=50,
            width=90,
            height=18,
        ),
    )

    assert reading is not None
    assert reading.stars == 4
    assert reading.confidence == 0.97
    assert reading.template_name == "stars_4"


def test_stars_reader_analyzes_only_requested_region() -> None:
    matcher = MatcherFake(
        {
            "stars_2": 0.95,
        }
    )

    reader = StarsReader(matcher)

    reader.read(
        Image.new("RGB", (500, 300)),
        RegionOfInterest(
            left=100,
            top=50,
            width=90,
            height=18,
        ),
    )

    assert all(
        size == (90, 18)
        for size, _, _ in matcher.calls
    )


def test_stars_reader_returns_none_without_match() -> None:
    reader = StarsReader(
        MatcherFake({}),
    )

    reading = reader.read(
        Image.new("RGB", (500, 300)),
        RegionOfInterest(
            left=100,
            top=50,
            width=90,
            height=18,
        ),
    )

    assert reading is None


def test_stars_reader_checks_zero_to_six_stars() -> None:
    matcher = MatcherFake({})

    StarsReader(matcher).read(
        Image.new("RGB", (500, 300)),
        RegionOfInterest(
            left=100,
            top=50,
            width=90,
            height=18,
        ),
    )

    assert tuple(
        template_name
        for _, template_name, _ in matcher.calls
    ) == (
        "stars_1",
        "stars_2",
        "stars_3",
        "stars_4",
        "stars_5",
        "stars_6",
    )