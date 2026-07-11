from __future__ import annotations

from dataclasses import dataclass

from app.calibration.models import (
    CalibrationProfile,
    CalibrationTarget,
    RelativePoint,
)
from app.calibration.repository import CalibrationRepository
from app.vision.window_detector import GameWindow


class CalibrationError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class CalibrationCapture:
    target: CalibrationTarget
    absolute_x: int
    absolute_y: int
    relative_point: RelativePoint


class CalibrationService:
    def __init__(self, repository: CalibrationRepository) -> None:
        self._repository = repository
        self._profile = repository.load()

    def current(self) -> CalibrationProfile:
        return self._profile

    def capture(
        self,
        target: CalibrationTarget,
        absolute_x: int,
        absolute_y: int,
        window: GameWindow,
    ) -> CalibrationCapture:
        if not window.is_usable:
            raise CalibrationError("La fenêtre NosTale n'est pas exploitable.")

        if not (
            window.left <= absolute_x < window.right
            and window.top <= absolute_y < window.bottom
        ):
            raise CalibrationError(
                "La souris doit se trouver à l'intérieur de la fenêtre NosTale."
            )

        relative = RelativePoint(
            x=absolute_x - window.left,
            y=absolute_y - window.top,
        )
        self._profile.points[target] = relative
        self._repository.save(self._profile)

        return CalibrationCapture(
            target=target,
            absolute_x=absolute_x,
            absolute_y=absolute_y,
            relative_point=relative,
        )

    def reset(self) -> CalibrationProfile:
        self._profile = CalibrationProfile()
        self._repository.save(self._profile)
        return self._profile
