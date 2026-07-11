from typing import Protocol

from app.calibration.models import CalibrationProfile
from app.configuration.models import Settings
from app.configuration.validators import (
    SettingsValidationError,
    validate_settings,
)
from app.execution.models import PreflightResult, PreflightStatus
from app.vision.window_detector import GameWindow


class WindowDetectorProtocol(Protocol):
    def detect(self) -> GameWindow | None:
        ...


class PreflightCheck:
    def __init__(
        self,
        window_detector: WindowDetectorProtocol,
    ) -> None:
        self._window_detector = window_detector

    def run(
        self,
        settings: Settings,
        calibration: CalibrationProfile,
        require_calibration: bool,
    ) -> PreflightResult:
        try:
            validate_settings(settings)
        except SettingsValidationError:
            return PreflightResult(
                status=PreflightStatus.INVALID_SETTINGS,
                message="La configuration des raccourcis est invalide.",
            )

        window = self._window_detector.detect()

        if window is None:
            return PreflightResult(
                status=PreflightStatus.WINDOW_NOT_FOUND,
                message="La fenêtre NosTale est introuvable.",
            )

        if not window.is_usable:
            return PreflightResult(
                status=PreflightStatus.WINDOW_NOT_USABLE,
                message="La fenêtre NosTale n'est pas exploitable.",
            )

        if require_calibration and not calibration.points:
            return PreflightResult(
                status=PreflightStatus.CALIBRATION_MISSING,
                message="Aucune cible n'a encore été calibrée.",
            )

        return PreflightResult(
            status=PreflightStatus.READY,
            message="Les vérifications préalables sont validées.",
        )