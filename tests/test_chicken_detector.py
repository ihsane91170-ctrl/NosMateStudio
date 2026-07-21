from PIL import Image

from app.vision.chicken_detector import ChickenDetector
from app.vision.match import TemplateMatch


class MatcherStub:
    def __init__(self, matches_by_name):
        self.matches_by_name = matches_by_name

    def find_all(self, screenshot, template_name, *, threshold=None, minimum_distance=10):
        return tuple(
            match
            for match in self.matches_by_name.get(template_name, ())
            if match.confidence >= (threshold or 0.0)
        )


def match(name, score, x, y):
    return TemplateMatch(name, score, x, y, 30, 20)


def test_classifies_multiple_positive_and_negative_templates():
    positive, negative = ChickenDetector.classify_template_names(
        ("chicken_02", "not_chicken_01", "pet_row", "chicken")
    )
    assert positive == ("chicken", "chicken_02")
    assert negative == ("not_chicken_01",)


def test_accepts_candidate_with_clear_positive_margin():
    detector = ChickenDetector(MatcherStub({
        "chicken_01": (match("chicken_01", 0.91, 100, 100),),
        "not_chicken_01": (match("not_chicken_01", 0.52, 102, 99),),
    }))
    report = detector.detect(
        Image.new("RGB", (500, 400)),
        template_names=("chicken_01", "not_chicken_01"),
        threshold=0.80,
        minimum_margin=0.12,
    )
    assert len(report.accepted) == 1
    assert report.accepted[0].margin == 0.39


def test_rejects_ambiguous_candidate():
    detector = ChickenDetector(MatcherStub({
        "chicken": (match("chicken", 0.84, 100, 100),),
        "not_chicken": (match("not_chicken", 0.79, 100, 100),),
    }))
    report = detector.detect(
        Image.new("RGB", (500, 400)),
        template_names=("chicken", "not_chicken"),
        threshold=0.80,
        minimum_margin=0.12,
    )
    assert report.accepted == ()
    assert report.ambiguous[0].reason == "détection ambiguë"


def test_rejects_when_negative_is_more_probable():
    detector = ChickenDetector(MatcherStub({
        "chicken": (match("chicken", 0.82, 100, 100),),
        "not_chicken": (match("not_chicken", 0.90, 100, 100),),
    }))
    report = detector.detect(
        Image.new("RGB", (500, 400)),
        template_names=("chicken", "not_chicken"),
        threshold=0.80,
    )
    assert report.accepted == ()
    assert report.ambiguous[0].reason == "autre monstre plus probable"


def test_deduplicates_same_chicken_found_by_two_animation_templates():
    detector = ChickenDetector(MatcherStub({
        "chicken_01": (match("chicken_01", 0.88, 100, 100),),
        "chicken_02": (match("chicken_02", 0.93, 104, 103),),
    }))
    report = detector.detect(
        Image.new("RGB", (500, 400)),
        template_names=("chicken_01", "chicken_02"),
        threshold=0.80,
        minimum_distance=40,
    )
    assert len(report.candidates) == 1
    assert report.candidates[0].match.template_name == "chicken_02"


def test_secure_mode_rejects_candidates_without_negative_templates():
    detector = ChickenDetector(MatcherStub({
        "chicken": (match("chicken", 0.95, 100, 100),),
    }))
    report = detector.detect(
        Image.new("RGB", (500, 400)),
        template_names=("chicken",),
        threshold=0.80,
        require_negative_templates=True,
    )
    assert report.accepted == ()
    assert report.ambiguous[0].reason == "filtrage négatif indisponible"
