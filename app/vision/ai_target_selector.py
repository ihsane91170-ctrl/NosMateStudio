from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from app.vision.ai_detector import ObjectDetection


@dataclass(frozen=True, slots=True)
class RankedTarget:
    detection: ObjectDetection
    score: float
    confidence_score: float
    center_score: float


class AITargetSelector:
    """Classe et choisit les cibles IA sans dépendre de Qt ou de Windows."""

    def __init__(
        self,
        *,
        target_class: str = "chicken",
        confidence_weight: float = 0.70,
        center_weight: float = 0.30,
    ) -> None:
        if confidence_weight < 0 or center_weight < 0:
            raise ValueError("Les pondérations doivent être positives.")
        total = confidence_weight + center_weight
        if total <= 0:
            raise ValueError("Au moins une pondération doit être non nulle.")
        self.target_class = target_class
        self.confidence_weight = confidence_weight / total
        self.center_weight = center_weight / total

    def rank(
        self,
        detections: tuple[ObjectDetection, ...],
        *,
        image_width: int,
        image_height: int,
    ) -> tuple[RankedTarget, ...]:
        if image_width <= 0 or image_height <= 0:
            raise ValueError("La taille de l'image doit être positive.")

        center_x = image_width / 2.0
        center_y = image_height / 2.0
        max_distance = hypot(center_x, center_y) or 1.0
        ranked: list[RankedTarget] = []

        for detection in detections:
            if detection.class_name != self.target_class:
                continue
            x, y = detection.center
            distance = hypot(x - center_x, y - center_y)
            center_score = max(0.0, 1.0 - distance / max_distance)
            confidence_score = min(1.0, max(0.0, detection.confidence))
            score = (
                self.confidence_weight * confidence_score
                + self.center_weight * center_score
            )
            ranked.append(
                RankedTarget(
                    detection=detection,
                    score=score,
                    confidence_score=confidence_score,
                    center_score=center_score,
                )
            )

        ranked.sort(
            key=lambda target: (
                target.score,
                target.detection.confidence,
            ),
            reverse=True,
        )
        return tuple(ranked)

    def choose(
        self,
        detections: tuple[ObjectDetection, ...],
        *,
        image_width: int,
        image_height: int,
    ) -> RankedTarget | None:
        ranked = self.rank(
            detections,
            image_width=image_width,
            image_height=image_height,
        )
        return ranked[0] if ranked else None
