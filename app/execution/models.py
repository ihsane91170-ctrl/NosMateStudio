from dataclasses import dataclass
from enum import StrEnum


class PreflightStatus(StrEnum):
    READY = "ready"
    WINDOW_NOT_FOUND = "window_not_found"
    WINDOW_NOT_USABLE = "window_not_usable"
    INVALID_SETTINGS = "invalid_settings"
    CALIBRATION_MISSING = "calibration_missing"


@dataclass(frozen=True, slots=True)
class PreflightResult:
    status: PreflightStatus
    message: str

    @property
    def allowed(self) -> bool:
        return self.status is PreflightStatus.READY