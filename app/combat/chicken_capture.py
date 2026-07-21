from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from PIL import Image

from app.automation.action_engine import ActionEngine
from app.vision.hp_state_reader import HpReadResult, HpState, HpStateReader


class CaptureOutcome(str, Enum):
    CAPTURE_SENT = "CAPTURE_SENT"
    MAX_ATTACKS_REACHED = "MAX_ATTACKS_REACHED"
    MAX_CAPTURE_ATTEMPTS_REACHED = "MAX_CAPTURE_ATTEMPTS_REACHED"
    HP_UNKNOWN = "HP_UNKNOWN"


@dataclass(frozen=True, slots=True)
class ChickenCaptureConfig:
    max_attacks: int = 3
    selection_delay_seconds: float = 0.40
    hp_update_delay_seconds: float = 0.80
    confirmation_reads: int = 2
    confirmation_delay_seconds: float = 0.15
    max_capture_attempts: int = 10
    capture_result_delay_seconds: float = 0.80
    capture_success_reads: int = 2
    capture_retry_delay_seconds: float = 0.25

    def __post_init__(self) -> None:
        if not 1 <= self.max_attacks <= 8:
            raise ValueError("Le nombre maximal d'attaques doit être compris entre 1 et 8.")
        if not 1 <= self.confirmation_reads <= 3:
            raise ValueError("Le nombre de confirmations doit être compris entre 1 et 3.")
        if not 1 <= self.max_capture_attempts <= 20:
            raise ValueError("Le nombre maximal de captures doit être compris entre 1 et 20.")
        if not 1 <= self.capture_success_reads <= 3:
            raise ValueError("Le nombre de confirmations de capture doit être compris entre 1 et 3.")
        for value in (
            self.selection_delay_seconds,
            self.hp_update_delay_seconds,
            self.confirmation_delay_seconds,
            self.capture_result_delay_seconds,
            self.capture_retry_delay_seconds,
        ):
            if value < 0:
                raise ValueError("Les délais ne peuvent pas être négatifs.")


@dataclass(frozen=True, slots=True)
class ChickenCaptureResult:
    outcome: CaptureOutcome
    attacks_sent: int
    hp_reads: tuple[HpReadResult, ...]
    capture_attempts: int = 0


class ChickenCaptureService:
    """Attaque jusqu'à 1 PV puis retente la capture jusqu'à confirmation.

    Une capture échouée laisse la cible sélectionnée à ``1 PV``. Dans ce cas,
    le service renvoie uniquement la touche de capture, sans attaquer à nouveau.
    Une capture est considérée réussie lorsque le panneau de cible disparaît
    pendant plusieurs lectures consécutives.
    """

    def __init__(self, actions: ActionEngine, hp_reader: HpStateReader) -> None:
        self._actions = actions
        self._hp_reader = hp_reader

    def execute(
        self,
        *,
        x: int,
        y: int,
        capture_image: Callable[[], Image.Image],
        config: ChickenCaptureConfig,
    ) -> ChickenCaptureResult:
        reads: list[HpReadResult] = []
        self._actions.click(x, y)
        self._actions.wait(config.selection_delay_seconds)

        for attack_index in range(config.max_attacks):
            if attack_index == 0:
                self._actions.press("space")
            else:
                self._actions.double_click(x, y)

            self._actions.wait(config.hp_update_delay_seconds)
            first = self._hp_reader.read(capture_image())
            reads.append(first)

            if first.state is HpState.FULL:
                continue
            if first.state is HpState.UNKNOWN:
                return ChickenCaptureResult(
                    CaptureOutcome.HP_UNKNOWN,
                    attack_index + 1,
                    tuple(reads),
                )

            if not self._confirm_one_hp(capture_image, config, reads):
                return ChickenCaptureResult(
                    CaptureOutcome.HP_UNKNOWN,
                    attack_index + 1,
                    tuple(reads),
                )

            return self._capture_until_success(
                capture_image=capture_image,
                config=config,
                reads=reads,
                attacks_sent=attack_index + 1,
            )

        return ChickenCaptureResult(
            CaptureOutcome.MAX_ATTACKS_REACHED,
            config.max_attacks,
            tuple(reads),
        )

    def _confirm_one_hp(
        self,
        capture_image: Callable[[], Image.Image],
        config: ChickenCaptureConfig,
        reads: list[HpReadResult],
    ) -> bool:
        confirmed = 1
        while confirmed < config.confirmation_reads:
            self._actions.wait(config.confirmation_delay_seconds)
            current = self._hp_reader.read(capture_image())
            reads.append(current)
            if current.state is not HpState.ONE:
                return False
            confirmed += 1
        return True

    def _capture_until_success(
        self,
        *,
        capture_image: Callable[[], Image.Image],
        config: ChickenCaptureConfig,
        reads: list[HpReadResult],
        attacks_sent: int,
    ) -> ChickenCaptureResult:
        for attempt in range(1, config.max_capture_attempts + 1):
            self._actions.press_capture_azerty()
            self._actions.wait(config.capture_result_delay_seconds)

            verification = self._hp_reader.read(capture_image())
            reads.append(verification)

            if verification.state is HpState.ONE:
                if attempt < config.max_capture_attempts:
                    self._actions.wait(config.capture_retry_delay_seconds)
                continue

            if verification.state is HpState.FULL:
                return ChickenCaptureResult(
                    CaptureOutcome.HP_UNKNOWN,
                    attacks_sent,
                    tuple(reads),
                    attempt,
                )

            # UNKNOWN après une capture peut signifier que le panneau cible a
            # disparu. Plusieurs lectures consécutives évitent un faux positif.
            unknown_reads = 1
            while unknown_reads < config.capture_success_reads:
                self._actions.wait(config.confirmation_delay_seconds)
                current = self._hp_reader.read(capture_image())
                reads.append(current)
                if current.state is HpState.ONE:
                    break
                if current.state is HpState.FULL:
                    return ChickenCaptureResult(
                        CaptureOutcome.HP_UNKNOWN,
                        attacks_sent,
                        tuple(reads),
                        attempt,
                    )
                unknown_reads += 1
            else:
                return ChickenCaptureResult(
                    CaptureOutcome.CAPTURE_SENT,
                    attacks_sent,
                    tuple(reads),
                    attempt,
                )

            if attempt < config.max_capture_attempts:
                self._actions.wait(config.capture_retry_delay_seconds)

        return ChickenCaptureResult(
            CaptureOutcome.MAX_CAPTURE_ATTEMPTS_REACHED,
            attacks_sent,
            tuple(reads),
            config.max_capture_attempts,
        )
