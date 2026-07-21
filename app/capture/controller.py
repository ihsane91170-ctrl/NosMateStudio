from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Protocol


class CaptureAttemptKind(Enum):
    """Nature de la dernière exécution du service de capture.

    SEARCH_REJECTED signifie qu'aucune cible sûre n'a été engagée. Ce cas ne
    consomme jamais le quota de tentatives de capture.
    """

    SEARCH_REJECTED = auto()
    CAPTURE_FAILED = auto()
    CAPTURED = auto()


class CaptureOneChicken(Protocol):
    """Capture exactement une poule et confirme le succès métier."""

    def capture_one(self) -> bool:
        ...


class ReturnToExpZone(Protocol):
    """Retourne dans la zone d'XP une fois le lot de captures terminé."""

    def return_to_exp_zone(self) -> bool:
        ...


class StopRequested(Protocol):
    def __call__(self) -> bool:
        ...


class CaptureBatchStatus(Enum):
    COMPLETED = auto()
    STOPPED = auto()
    CAPTURE_FAILED = auto()
    SEARCH_EXHAUSTED = auto()
    RETURN_FAILED = auto()
    STANDBY_FAILED = auto()


@dataclass(frozen=True, slots=True)
class CaptureBatchConfig:
    target_count: int
    max_capture_attempts_per_chicken: int = 10
    max_search_attempts_per_chicken: int = 100

    def __post_init__(self) -> None:
        if self.target_count < 1:
            raise ValueError("target_count doit être supérieur ou égal à 1")
        if self.max_capture_attempts_per_chicken < 1:
            raise ValueError(
                "max_capture_attempts_per_chicken doit être supérieur ou égal à 1"
            )
        if self.max_search_attempts_per_chicken < 1:
            raise ValueError(
                "max_search_attempts_per_chicken doit être supérieur ou égal à 1"
            )


@dataclass(frozen=True, slots=True)
class CaptureBatchProgress:
    captured_count: int
    target_count: int
    current_attempt: int
    message: str = ""
    search_attempts: int = 0
    capture_attempts: int = 0
    phase: str = "search"


@dataclass(frozen=True, slots=True)
class CaptureBatchResult:
    status: CaptureBatchStatus
    captured_count: int
    target_count: int
    total_capture_attempts: int
    message: str
    total_search_attempts: int = 0

    @property
    def completed(self) -> bool:
        return self.status is CaptureBatchStatus.COMPLETED


class CaptureBatchController:
    """Capture N poules puis revient une seule fois dans la zone d'XP.

    Les recherches IA rejetées et les captures réellement tentées disposent de
    quotas indépendants. Une mauvaise cible désélectionnée ne réduit donc jamais
    les chances de capturer la quantité demandée.
    """

    def __init__(
        self,
        capture_service: CaptureOneChicken,
        return_service: ReturnToExpZone,
        *,
        stop_requested: StopRequested | None = None,
        on_progress: Callable[[CaptureBatchProgress], None] | None = None,
    ) -> None:
        self._capture_service = capture_service
        self._return_service = return_service
        self._stop_requested = stop_requested or (lambda: False)
        self._on_progress = on_progress

    def run(self, config: CaptureBatchConfig) -> CaptureBatchResult:
        captured_count = 0
        total_capture_attempts = 0
        total_search_attempts = 0

        while captured_count < config.target_count:
            search_attempts = 0
            capture_attempts = 0
            captured = False

            while not captured:
                if self._stop_requested():
                    return self._result(
                        CaptureBatchStatus.STOPPED,
                        captured_count,
                        config,
                        total_capture_attempts,
                        total_search_attempts,
                        "Capture arrêtée par l'utilisateur.",
                    )

                if search_attempts >= config.max_search_attempts_per_chicken:
                    return self._result(
                        CaptureBatchStatus.SEARCH_EXHAUSTED,
                        captured_count,
                        config,
                        total_capture_attempts,
                        total_search_attempts,
                        "Aucune poule sûre trouvée dans la limite de recherches prévue.",
                    )

                if capture_attempts >= config.max_capture_attempts_per_chicken:
                    return self._result(
                        CaptureBatchStatus.CAPTURE_FAILED,
                        captured_count,
                        config,
                        total_capture_attempts,
                        total_search_attempts,
                        "Impossible de capturer la prochaine poule dans la limite prévue.",
                    )

                search_attempts += 1
                total_search_attempts += 1
                self._notify(
                    captured_count,
                    config.target_count,
                    search_attempts,
                    search_attempts=search_attempts,
                    capture_attempts=capture_attempts,
                    phase="search",
                )

                success = self._capture_service.capture_one()
                kind = self._attempt_kind(success)
                message = str(
                    getattr(self._capture_service, "last_message", "")
                    or "La tentative n'a produit aucune action confirmée."
                )

                if kind is CaptureAttemptKind.SEARCH_REJECTED:
                    self._notify(
                        captured_count,
                        config.target_count,
                        search_attempts,
                        message,
                        search_attempts=search_attempts,
                        capture_attempts=capture_attempts,
                        phase="search_rejected",
                    )
                    continue

                capture_attempts += 1
                total_capture_attempts += 1

                if kind is CaptureAttemptKind.CAPTURED or success:
                    captured = True
                    self._notify(
                        captured_count,
                        config.target_count,
                        capture_attempts,
                        message,
                        search_attempts=search_attempts,
                        capture_attempts=capture_attempts,
                        phase="captured",
                    )
                    break

                self._notify(
                    captured_count,
                    config.target_count,
                    capture_attempts,
                    message,
                    search_attempts=search_attempts,
                    capture_attempts=capture_attempts,
                    phase="capture_failed",
                )

            captured_count += 1

            if captured_count == 1:
                standby_action = getattr(
                    self._capture_service,
                    "put_first_companion_on_standby",
                    None,
                )
                if callable(standby_action):
                    self._notify(
                        captured_count,
                        config.target_count,
                        0,
                        "Première poule capturée : mise en standby avec S…",
                        search_attempts=search_attempts,
                        capture_attempts=capture_attempts,
                        phase="standby",
                    )
                    if not standby_action():
                        message = str(
                            getattr(self._capture_service, "last_message", "")
                            or "Impossible de mettre la première poule en standby."
                        )
                        return self._result(
                            CaptureBatchStatus.STANDBY_FAILED,
                            captured_count,
                            config,
                            total_capture_attempts,
                            total_search_attempts,
                            message,
                        )

            self._notify(
                captured_count,
                config.target_count,
                0,
                search_attempts=search_attempts,
                capture_attempts=capture_attempts,
                phase="counted",
            )

        self._notify(
            captured_count,
            config.target_count,
            0,
            "Lot terminé : retour vers la zone d'XP…",
            phase="return",
        )
        if not self._return_service.return_to_exp_zone():
            return self._result(
                CaptureBatchStatus.RETURN_FAILED,
                captured_count,
                config,
                total_capture_attempts,
                total_search_attempts,
                "Lot capturé, mais retour en zone d'XP non confirmé.",
            )

        return self._result(
            CaptureBatchStatus.COMPLETED,
            captured_count,
            config,
            total_capture_attempts,
            total_search_attempts,
            f"{captured_count} poule(s) capturée(s), puis retour en zone d'XP confirmé.",
        )

    def _attempt_kind(self, success: bool) -> CaptureAttemptKind:
        raw = getattr(self._capture_service, "last_attempt_kind", None)
        if isinstance(raw, CaptureAttemptKind):
            return raw
        if isinstance(raw, str):
            try:
                return CaptureAttemptKind[raw]
            except KeyError:
                pass
        return CaptureAttemptKind.CAPTURED if success else CaptureAttemptKind.CAPTURE_FAILED

    def _notify(
        self,
        captured_count: int,
        target_count: int,
        attempt: int,
        message: str = "",
        *,
        search_attempts: int = 0,
        capture_attempts: int = 0,
        phase: str = "search",
    ) -> None:
        if self._on_progress is not None:
            self._on_progress(
                CaptureBatchProgress(
                    captured_count=captured_count,
                    target_count=target_count,
                    current_attempt=attempt,
                    message=message,
                    search_attempts=search_attempts,
                    capture_attempts=capture_attempts,
                    phase=phase,
                )
            )

    @staticmethod
    def _result(
        status: CaptureBatchStatus,
        captured_count: int,
        config: CaptureBatchConfig,
        total_capture_attempts: int,
        total_search_attempts: int,
        message: str,
    ) -> CaptureBatchResult:
        return CaptureBatchResult(
            status=status,
            captured_count=captured_count,
            target_count=config.target_count,
            total_capture_attempts=total_capture_attempts,
            total_search_attempts=total_search_attempts,
            message=message,
        )
