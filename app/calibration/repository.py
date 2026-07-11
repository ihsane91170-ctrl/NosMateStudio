from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from app.calibration.models import CalibrationProfile


class CalibrationRepository(Protocol):
    def load(self) -> CalibrationProfile:
        ...

    def save(self, profile: CalibrationProfile) -> None:
        ...


class JsonCalibrationRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> CalibrationProfile:
        if not self.path.exists():
            return CalibrationProfile()

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return CalibrationProfile.from_dict(raw)

    def save(self, profile: CalibrationProfile) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temporary.write_text(
            json.dumps(profile.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary.replace(self.path)
