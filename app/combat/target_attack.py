from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.automation.action_engine import ActionEngine


class AttackAttempt(str, Enum):
    SPACE = "SPACE"
    DOUBLE_CLICK = "DOUBLE_CLICK"


@dataclass(frozen=True, slots=True)
class AttackConfig:
    max_attempts: int = 2
    selection_delay_seconds: float = 0.40
    retry_delay_seconds: float = 0.70

    def __post_init__(self) -> None:
        if not 1 <= self.max_attempts <= 5:
            raise ValueError("Le nombre de tentatives doit être compris entre 1 et 5.")
        if self.selection_delay_seconds < 0:
            raise ValueError("Le délai de sélection ne peut pas être négatif.")
        if self.retry_delay_seconds < 0:
            raise ValueError("Le délai entre tentatives ne peut pas être négatif.")


@dataclass(frozen=True, slots=True)
class AttackResult:
    attempts: tuple[AttackAttempt, ...]


class TargetAttackService:
    """Sélectionne une cible puis envoie des attaques bornées, jamais la capture."""

    def __init__(self, action_engine: ActionEngine) -> None:
        self._actions = action_engine

    def execute(self, *, x: int, y: int, config: AttackConfig) -> AttackResult:
        self._actions.click(x, y)
        self._actions.wait(config.selection_delay_seconds)

        attempts: list[AttackAttempt] = []
        for index in range(config.max_attempts):
            if index % 2 == 0:
                self._actions.press("space")
                attempts.append(AttackAttempt.SPACE)
            else:
                self._actions.double_click(x, y)
                attempts.append(AttackAttempt.DOUBLE_CLICK)

            if index + 1 < config.max_attempts:
                self._actions.wait(config.retry_delay_seconds)

        return AttackResult(tuple(attempts))
