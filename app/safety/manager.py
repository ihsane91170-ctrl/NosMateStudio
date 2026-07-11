from app.safety.exceptions import SafetyViolationError
from app.safety.models import SafetyCheckResult, SafetyStatus
from app.safety.stop_token import StopToken
from app.vision.window_detector import WindowDetector


class SafetyManager:
    def __init__(
        self,
        window_detector: WindowDetector,
        stop_token: StopToken | None = None,
    ) -> None:
        self._window_detector = window_detector
        self.stop_token = stop_token or StopToken()

    def check(self) -> SafetyCheckResult:
        if self.stop_token.is_requested:
            return SafetyCheckResult(
                status=SafetyStatus.STOP_REQUESTED,
                message="Un arrêt d'urgence a été demandé.",
            )

        window = self._window_detector.detect()

        if window is None:
            return SafetyCheckResult(
                status=SafetyStatus.WINDOW_NOT_FOUND,
                message="La fenêtre NosTale est introuvable.",
            )

        if not window.is_usable:
            return SafetyCheckResult(
                status=SafetyStatus.WINDOW_NOT_USABLE,
                message="La fenêtre NosTale n'est pas exploitable.",
            )

        return SafetyCheckResult(
            status=SafetyStatus.SAFE,
            message="Les conditions de sécurité sont respectées.",
        )

    def ensure_safe(self) -> None:
        result = self.check()

        if not result.is_safe:
            raise SafetyViolationError(result.message)

    def request_stop(self) -> None:
        self.stop_token.request()

    def reset_stop(self) -> None:
        self.stop_token.reset()