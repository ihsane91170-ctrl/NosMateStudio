from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from app.vision.ai_detector import ObjectDetection
from app.vision.ai_target_selector import AITargetSelector, RankedTarget


@dataclass(frozen=True, slots=True)
class TemporalTargetValidation:
    accepted: bool
    target: RankedTarget | None
    reason: str
    matched_frames: int
    total_frames: int
    best_confidence: float | None = None


class TemporalTargetValidator:
    """Valide une cible sur plusieurs images avant toute action réelle.

    Le principe est volontairement conservateur : une cible incertaine est
    ignorée. Une poule doit être retrouvée au même emplacement sur plusieurs
    images et dépasser un seuil de confiance dédié aux clics réels.
    """

    def __init__(
        self,
        *,
        selector: AITargetSelector | None = None,
        minimum_confidence: float = 0.90,
        required_frames: int = 2,
        maximum_center_distance: float = 45.0,
        competing_class: str = "not_chicken",
        competing_iou_threshold: float = 0.10,
    ) -> None:
        if not 0.0 < minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence doit être comprise entre 0 et 1.")
        if required_frames < 1:
            raise ValueError("required_frames doit être supérieur ou égal à 1.")
        if maximum_center_distance < 0:
            raise ValueError("maximum_center_distance doit être positif.")
        self._selector = selector or AITargetSelector()
        self.minimum_confidence = minimum_confidence
        self.required_frames = required_frames
        self.maximum_center_distance = maximum_center_distance
        self.competing_class = competing_class
        self.competing_iou_threshold = competing_iou_threshold

    def validate(
        self,
        frames: tuple[tuple[ObjectDetection, ...], ...],
        *,
        image_width: int,
        image_height: int,
    ) -> TemporalTargetValidation:
        if len(frames) < self.required_frames:
            return TemporalTargetValidation(
                False,
                None,
                "Pas assez d'images pour confirmer la cible.",
                0,
                len(frames),
            )

        ranked_by_frame: list[tuple[RankedTarget, ...]] = []
        for detections in frames:
            ranked = tuple(
                target
                for target in self._selector.rank(
                    detections,
                    image_width=image_width,
                    image_height=image_height,
                )
                if target.detection.confidence >= self.minimum_confidence
                and not self._overlaps_competing(target.detection, detections)
            )
            ranked_by_frame.append(ranked)

        anchors = ranked_by_frame[0]
        best: tuple[int, float, RankedTarget] | None = None
        for anchor in anchors:
            matches = 1
            confidence_sum = anchor.detection.confidence
            representative = anchor
            for candidates in ranked_by_frame[1:]:
                match = self._closest_match(anchor.detection, candidates)
                if match is None:
                    continue
                matches += 1
                confidence_sum += match.detection.confidence
                if match.detection.confidence > representative.detection.confidence:
                    representative = match
            average_confidence = confidence_sum / matches
            candidate_key = (matches, average_confidence, representative)
            if best is None or candidate_key[:2] > best[:2]:
                best = candidate_key

        if best is None or best[0] < self.required_frames:
            max_confidence = max(
                (
                    target.detection.confidence
                    for ranked in ranked_by_frame
                    for target in ranked
                ),
                default=None,
            )
            return TemporalTargetValidation(
                False,
                None,
                (
                    "Aucune poule suffisamment fiable et stable sur "
                    f"{self.required_frames} image(s)."
                ),
                best[0] if best is not None else 0,
                len(frames),
                max_confidence,
            )

        return TemporalTargetValidation(
            True,
            best[2],
            "Cible poule confirmée sur plusieurs images.",
            best[0],
            len(frames),
            best[2].detection.confidence,
        )

    def _closest_match(
        self,
        anchor: ObjectDetection,
        candidates: tuple[RankedTarget, ...],
    ) -> RankedTarget | None:
        closest: RankedTarget | None = None
        closest_distance = float("inf")
        ax, ay = anchor.center
        for candidate in candidates:
            bx, by = candidate.detection.center
            distance = hypot(ax - bx, ay - by)
            if distance <= self.maximum_center_distance and distance < closest_distance:
                closest = candidate
                closest_distance = distance
        return closest

    def _overlaps_competing(
        self,
        target: ObjectDetection,
        detections: tuple[ObjectDetection, ...],
    ) -> bool:
        for detection in detections:
            if detection.class_name.casefold() != self.competing_class.casefold():
                continue
            if self._iou(target, detection) >= self.competing_iou_threshold:
                return True
        return False

    @staticmethod
    def _iou(a: ObjectDetection, b: ObjectDetection) -> float:
        left = max(a.left, b.left)
        top = max(a.top, b.top)
        right = min(a.right, b.right)
        bottom = min(a.bottom, b.bottom)
        intersection = max(0, right - left) * max(0, bottom - top)
        if intersection == 0:
            return 0.0
        area_a = max(0, a.right - a.left) * max(0, a.bottom - a.top)
        area_b = max(0, b.right - b.left) * max(0, b.bottom - b.top)
        union = area_a + area_b - intersection
        return intersection / union if union else 0.0
