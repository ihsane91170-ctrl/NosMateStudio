import numpy as np
import pytest
from PIL import Image

from app.vision.template_matcher import (
    TemplateMatcher,
    TemplateTooLargeError,
)
from app.vision.template_repository import TemplateRepository


def build_pattern() -> Image.Image:
    pixels = np.zeros((20, 30, 3), dtype=np.uint8)

    pixels[2:18, 3:27] = (220, 220, 220)
    pixels[5:15, 8:22] = (40, 40, 40)
    pixels[8:12, 12:18] = (255, 255, 255)

    return Image.fromarray(pixels, mode="RGB")


def test_matcher_finds_template_position(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    template = build_pattern()
    repository.save("accompany_button", template)

    screenshot_pixels = np.zeros(
        (100, 160, 3),
        dtype=np.uint8,
    )

    template_pixels = np.asarray(template)
    screenshot_pixels[40:60, 70:100] = template_pixels

    screenshot = Image.fromarray(
        screenshot_pixels,
        mode="RGB",
    )

    matcher = TemplateMatcher(
        repository,
        default_threshold=0.90,
    )

    match = matcher.find(
        screenshot,
        "accompany_button",
    )

    assert match is not None
    assert match.template_name == "accompany_button"
    assert match.left == 70
    assert match.top == 40
    assert match.width == 30
    assert match.height == 20
    assert match.center == (85, 50)
    assert match.confidence >= 0.90


def test_matcher_returns_none_below_threshold(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    repository.save(
        "accompany_button",
        build_pattern(),
    )

    screenshot = Image.new(
        "RGB",
        (160, 100),
        (120, 120, 120),
    )

    matcher = TemplateMatcher(repository)

    match = matcher.find(
        screenshot,
        "accompany_button",
        threshold=0.99,
    )

    assert match is None


def test_matcher_rejects_template_larger_than_image(
    tmp_path,
) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    repository.save(
        "large_template",
        Image.new("RGB", (200, 200)),
    )

    matcher = TemplateMatcher(repository)

    with pytest.raises(TemplateTooLargeError):
        matcher.find(
            Image.new("RGB", (100, 100)),
            "large_template",
        )


def test_matcher_rejects_invalid_threshold(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")

    with pytest.raises(ValueError):
        TemplateMatcher(
            repository,
            default_threshold=1.5,
        )

def test_matcher_finds_multiple_occurrences(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    template = build_pattern()
    repository.save("pet_row", template)

    screenshot_pixels = np.zeros(
        (160, 220, 3),
        dtype=np.uint8,
    )

    template_pixels = np.asarray(template)

    screenshot_pixels[20:40, 30:60] = template_pixels
    screenshot_pixels[80:100, 120:150] = template_pixels

    screenshot = Image.fromarray(
        screenshot_pixels,
        mode="RGB",
    )

    matcher = TemplateMatcher(
        repository,
        default_threshold=0.90,
    )

    matches = matcher.find_all(
        screenshot,
        "pet_row",
        minimum_distance=20,
    )

    assert len(matches) == 2
    assert matches[0].left == 30
    assert matches[0].top == 20
    assert matches[1].left == 120
    assert matches[1].top == 80


def test_matcher_deduplicates_close_occurrences(tmp_path) -> None:
    repository = TemplateRepository(tmp_path / "templates")
    template = build_pattern()
    repository.save("pet_row", template)

    screenshot_pixels = np.zeros(
        (100, 160, 3),
        dtype=np.uint8,
    )

    screenshot_pixels[30:50, 60:90] = np.asarray(template)

    screenshot = Image.fromarray(
        screenshot_pixels,
        mode="RGB",
    )

    matcher = TemplateMatcher(
        repository,
        default_threshold=0.80,
    )

    matches = matcher.find_all(
        screenshot,
        "pet_row",
        minimum_distance=15,
    )

    assert len(matches) == 1