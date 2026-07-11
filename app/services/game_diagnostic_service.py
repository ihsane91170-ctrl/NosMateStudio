from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.vision.window_detector import GameWindow, WindowDetector


class DiagnosticStatus(StrEnum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class GameDiagnosticResult:
    status: DiagnosticStatus
    message: str
    window: GameWindow | None = None

    @property
    def can_start(self) -> bool:
        return (
            self.status is DiagnosticStatus.FOUND
            and self.window is not None
            and self.window.is_usable
        )


class GameDiagnosticService:
    def __init__(self, detector: WindowDetector) -> None:
        self._detector = detector

    def run(self) -> GameDiagnosticResult:
        try:
            window = self._detector.detect()

            if window is None:
                return GameDiagnosticResult(
                    status=DiagnosticStatus.NOT_FOUND,
                    message="Client NosTale introuvable.",
                )

            if not window.is_usable:
                return GameDiagnosticResult(
                    status=DiagnosticStatus.ERROR,
                    message="La fenêtre NosTale est inutilisable.",
                    window=window,
                )

            return GameDiagnosticResult(
                status=DiagnosticStatus.FOUND,
                message="Client NosTale détecté.",
                window=window,
            )

        except Exception as exc:
            return GameDiagnosticResult(
                status=DiagnosticStatus.ERROR,
                message=f"Erreur de détection : {exc}",
            )