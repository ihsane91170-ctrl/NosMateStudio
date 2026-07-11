from dataclasses import dataclass
from enum import StrEnum


class SafetyStatus(StrEnum):
    SAFE = "safe"
    STOP_REQUESTED = "stop_requested"
    WINDOW_NOT_FOUND = "window_not_found"
    WINDOW_NOT_USABLE = "window_not_usable"


@dataclass(frozen=True, slots=True)
class SafetyCheckResult:
    status: SafetyStatus
    message: str

    @property
    def is_safe(self) -> bool:
        return self.status is SafetyStatus.SAFE