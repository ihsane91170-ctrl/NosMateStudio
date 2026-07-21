from app.vision.chicken_selector import ChickenSelector
from app.vision.match import TemplateMatch
from app.vision.window_detector import GameWindow


def window() -> GameWindow:
    return GameWindow("NosTale", left=100, top=200, width=1000, height=600)


def match(confidence: float, left: int, top: int) -> TemplateMatch:
    return TemplateMatch("chicken", confidence, left, top, 40, 40)


def test_choose_returns_none_without_candidates() -> None:
    assert ChickenSelector().choose((), window()) is None


def test_choose_prefers_high_confidence_candidate() -> None:
    candidates = (
        match(0.82, 480, 280),
        match(0.95, 100, 100),
    )
    assert ChickenSelector().choose(candidates, window()) == candidates[1]


def test_choose_uses_window_center_as_tie_breaker() -> None:
    candidates = (
        match(0.90, 10, 10),
        match(0.90, 480, 280),
    )
    assert ChickenSelector().choose(candidates, window()) == candidates[1]


def test_converts_relative_match_to_screen_coordinates() -> None:
    selected = match(0.95, 20, 30)
    assert ChickenSelector.to_screen_coordinates(selected, window()) == (140, 250)
