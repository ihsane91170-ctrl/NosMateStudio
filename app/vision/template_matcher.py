from __future__ import annotations

import cv2
import numpy as np
from PIL import Image

from app.vision.match import TemplateMatch
from app.vision.template_repository import TemplateRepository


class TemplateTooLargeError(ValueError):
    """Raised when a template is larger than the searched image."""


class TemplateMatcher:
    def __init__(
        self,
        repository: TemplateRepository,
        default_threshold: float = 0.85,
    ) -> None:
        if not 0.0 <= default_threshold <= 1.0:
            raise ValueError(
                "Le seuil de détection doit être compris entre 0 et 1."
            )

        self._repository = repository
        self._default_threshold = default_threshold

    def find(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
    ) -> TemplateMatch | None:
        effective_threshold = (
            self._default_threshold
            if threshold is None
            else threshold
        )

        if not 0.0 <= effective_threshold <= 1.0:
            raise ValueError(
                "Le seuil de détection doit être compris entre 0 et 1."
            )

        source = self._to_grayscale_array(screenshot)
        template_image = self._repository.load_image(template_name)
        template = self._to_grayscale_array(template_image)

        source_height, source_width = source.shape
        template_height, template_width = template.shape

        if (
            template_width > source_width
            or template_height > source_height
        ):
            raise TemplateTooLargeError(
                "Le template est plus grand que l'image analysée."
            )

        result = cv2.matchTemplate(
            source,
            template,
            cv2.TM_CCOEFF_NORMED,
        )

        _, maximum, _, maximum_location = cv2.minMaxLoc(result)

        confidence = float(maximum)

        if confidence < effective_threshold:
            return None

        left, top = maximum_location

        return TemplateMatch(
            template_name=template_name,
            confidence=confidence,
            left=int(left),
            top=int(top),
            width=int(template_width),
            height=int(template_height),
        )

    def find_all(
        self,
        screenshot: Image.Image,
        template_name: str,
        *,
        threshold: float | None = None,
        minimum_distance: int = 10,
    ) -> tuple[TemplateMatch, ...]:
        effective_threshold = (
            self._default_threshold
            if threshold is None
            else threshold
        )

        if not 0.0 <= effective_threshold <= 1.0:
            raise ValueError(
                "Le seuil de détection doit être compris entre 0 et 1."
            )

        if minimum_distance < 0:
            raise ValueError(
                "La distance minimale doit être positive ou nulle."
            )

        source = self._to_grayscale_array(screenshot)
        template_image = self._repository.load_image(template_name)
        template = self._to_grayscale_array(template_image)

        source_height, source_width = source.shape
        template_height, template_width = template.shape

        if (
            template_width > source_width
            or template_height > source_height
        ):
            raise TemplateTooLargeError(
                "Le template est plus grand que l'image analysée."
            )

        result = cv2.matchTemplate(
            source,
            template,
            cv2.TM_CCOEFF_NORMED,
        )

        y_coordinates, x_coordinates = np.where(
            result >= effective_threshold
        )

        candidates = [
            TemplateMatch(
                template_name=template_name,
                confidence=float(result[y, x]),
                left=int(x),
                top=int(y),
                width=int(template_width),
                height=int(template_height),
            )
            for x, y in zip(
                x_coordinates.tolist(),
                y_coordinates.tolist(),
                strict=True,
            )
        ]

        candidates.sort(
            key=lambda match: match.confidence,
            reverse=True,
        )

        accepted: list[TemplateMatch] = []

        for candidate in candidates:
            if all(
                self._center_distance(candidate, existing)
                >= minimum_distance
                for existing in accepted
            ):
                accepted.append(candidate)

        accepted.sort(
            key=lambda match: (
                match.top,
                match.left,
            )
        )

        return tuple(accepted)

    @staticmethod
    def _to_grayscale_array(image: Image.Image) -> np.ndarray:
        rgb = np.asarray(
            image.convert("RGB"),
            dtype=np.uint8,
        )

        return cv2.cvtColor(
            rgb,
            cv2.COLOR_RGB2GRAY,
        )

    @staticmethod
    def _center_distance(
        first: TemplateMatch,
        second: TemplateMatch,
    ) -> float:
        first_x, first_y = first.center
        second_x, second_y = second.center

        delta_x = first_x - second_x
        delta_y = first_y - second_y

        return float(
            (delta_x**2 + delta_y**2) ** 0.5
        )