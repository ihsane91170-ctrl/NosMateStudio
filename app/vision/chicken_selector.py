from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from app.vision.match import TemplateMatch
from app.vision.window_detector import GameWindow


@dataclass(frozen=True, slots=True)
class ChickenVisionState:
    window_detected: bool
    candidates: tuple[TemplateMatch, ...] = ()
    selected: TemplateMatch | None = None
    message: str = ""

    @property
    def chicken_count(self) -> int:
        return len(self.candidates)


class ChickenSelector:
    """Choisit une candidate poule parmi les détections visuelles.

    La stratégie privilégie d'abord la confiance du template, puis la
    proximité du centre de la fenêtre afin d'éviter les cibles situées sur
    les bords. Aucun clic n'est effectué par cette classe.
    """

    def choose(
        self,
        matches: tuple[TemplateMatch, ...],
        window: GameWindow,
    ) -> TemplateMatch | None:
        if not matches:
            return None

        center_x = window.width / 2
        center_y = window.height / 2
        diagonal = max(hypot(window.width, window.height), 1.0)

        def score(match: TemplateMatch) -> tuple[float, float]:
            match_x, match_y = match.center
            distance = hypot(match_x - center_x, match_y - center_y)
            normalized_distance = distance / diagonal
            return (match.confidence - 0.15 * normalized_distance, match.confidence)

        return max(matches, key=score)

    @staticmethod
    def to_screen_coordinates(
        match: TemplateMatch,
        window: GameWindow,
    ) -> tuple[int, int]:
        center_x, center_y = match.center
        return window.left + center_x, window.top + center_y
