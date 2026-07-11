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