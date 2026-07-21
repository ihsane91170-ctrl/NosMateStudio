from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Protocol

from PIL import Image

from app.vision.match import TemplateMatch


class MultiTemplateMatcherProtocol(Protocol):
    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> TemplateMatch | None: ...

    def find_all(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]: ...


@dataclass(frozen=True, slots=True)
class ChickenCandidate:
    match: TemplateMatch
    chicken_score: float
    other_monster_score: float
    margin: float
    accepted: bool
    reason: str

    @property
    def center(self) -> tuple[int, int]:
        return self.match.center


@dataclass(frozen=True, slots=True)
class ChickenDetectionReport:
    candidates: tuple[ChickenCandidate, ...]
    positive_templates: tuple[str, ...]
    negative_templates: tuple[str, ...]

    @property
    def accepted(self) -> tuple[ChickenCandidate, ...]:
        return tuple(candidate for candidate in self.candidates if candidate.accepted)

    @property
    def ambiguous(self) -> tuple[ChickenCandidate, ...]:
        return tuple(candidate for candidate in self.candidates if not candidate.accepted)


class ChickenDetector:
    """Détection multi-templates avec exclusion des faux positifs connus."""

    POSITIVE_PREFIXES = ("chicken",)
    NEGATIVE_PREFIXES = ("not_chicken",)

    def __init__(self, matcher: MultiTemplateMatcherProtocol) -> None:
        self._matcher = matcher

    @classmethod
    def classify_template_names(
        cls, names: tuple[str, ...]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        positive = tuple(
            sorted(
                name
                for name in names
                if name == "chicken" or name.startswith("chicken_")
            )
        )
        negative = tuple(
            sorted(
                name
                for name in names
                if name == "not_chicken" or name.startswith("not_chicken_")
            )
        )
        return positive, negative

    def detect(
        self,
        screenshot: Image.Image,
        *,
        template_names: tuple[str, ...],
        threshold: float,
        negative_threshold: float = 0.45,
        minimum_margin: float = 0.12,
        minimum_distance: int = 40,
        require_negative_templates: bool = False,
    ) -> ChickenDetectionReport:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Le seuil poule doit être compris entre 0 et 1.")
        if not 0.0 <= negative_threshold <= 1.0:
            raise ValueError("Le seuil négatif doit être compris entre 0 et 1.")
        if not 0.0 <= minimum_margin <= 1.0:
            raise ValueError("La marge minimale doit être comprise entre 0 et 1.")

        positive_names, negative_names = self.classify_template_names(template_names)
        if not positive_names:
            return ChickenDetectionReport((), (), negative_names)

        positive_matches: list[TemplateMatch] = []
        for name in positive_names:
            positive_matches.extend(
                self._matcher.find_all(
                    screenshot,
                    name,
                    threshold=threshold,
                    minimum_distance=minimum_distance,
                )
            )
        positives = self._deduplicate(tuple(positive_matches), minimum_distance)

        negative_matches: list[TemplateMatch] = []
        for name in negative_names:
            negative_matches.extend(
                self._matcher.find_all(
                    screenshot,
                    name,
                    threshold=negative_threshold,
                    minimum_distance=minimum_distance,
                )
            )

        candidates: list[ChickenCandidate] = []
        for positive in positives:
            negative_score = self._local_negative_score(
                screenshot,
                positive,
                negative_names,
                tuple(negative_matches),
                minimum_distance,
            )
            margin = positive.confidence - negative_score
            has_negative_filter = bool(negative_names)
            accepted = margin >= minimum_margin and (
                has_negative_filter or not require_negative_templates
            )
            if accepted:
                reason = "poule confirmée"
            elif require_negative_templates and not has_negative_filter:
                reason = "filtrage négatif indisponible"
            elif negative_score >= positive.confidence:
                reason = "autre monstre plus probable"
            else:
                reason = "détection ambiguë"
            candidates.append(
                ChickenCandidate(
                    match=positive,
                    chicken_score=positive.confidence,
                    other_monster_score=negative_score,
                    margin=margin,
                    accepted=accepted,
                    reason=reason,
                )
            )

        candidates.sort(
            key=lambda candidate: (
                candidate.accepted,
                candidate.margin,
                candidate.chicken_score,
            ),
            reverse=True,
        )
        return ChickenDetectionReport(
            tuple(candidates), positive_names, negative_names
        )

    def _local_negative_score(
        self,
        screenshot: Image.Image,
        positive: TemplateMatch,
        negative_names: tuple[str, ...],
        global_negatives: tuple[TemplateMatch, ...],
        minimum_distance: int,
    ) -> float:
        """Mesure les templates négatifs autour de la candidate positive.

        La comparaison globale par distance de centres rate les templates de tailles
        différentes. On analyse donc une zone locale élargie autour de la candidate,
        puis on conserve également les scores globaux voisins comme filet de sécurité.
        """
        px, py = positive.center
        padding = max(minimum_distance, positive.width, positive.height)
        left = max(0, positive.left - padding)
        top = max(0, positive.top - padding)
        right = min(screenshot.width, positive.left + positive.width + padding)
        bottom = min(screenshot.height, positive.top + positive.height + padding)
        local_image = screenshot.crop((left, top, right, bottom))

        scores: list[float] = []
        finder = getattr(self._matcher, "find", None)
        if callable(finder):
            for name in negative_names:
                try:
                    match = finder(local_image, name, threshold=0.0)
                except (ValueError, RuntimeError):
                    match = None
                if match is not None:
                    scores.append(match.confidence)

        # Compatibilité avec les matchers de test et filet de sécurité global.
        radius = padding * 2
        for negative in global_negatives:
            nx, ny = negative.center
            if hypot(px - nx, py - ny) <= radius:
                scores.append(negative.confidence)
        return max(scores, default=0.0)

    @staticmethod
    def _deduplicate(
        matches: tuple[TemplateMatch, ...], minimum_distance: int
    ) -> tuple[TemplateMatch, ...]:
        ordered = sorted(matches, key=lambda match: match.confidence, reverse=True)
        accepted: list[TemplateMatch] = []
        for candidate in ordered:
            cx, cy = candidate.center
            if all(
                hypot(cx - ex, cy - ey) >= minimum_distance
                for existing in accepted
                for ex, ey in (existing.center,)
            ):
                accepted.append(candidate)
        return tuple(accepted)
