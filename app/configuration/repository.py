from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from app.configuration.models import Settings


class SettingsRepository(Protocol):
    def load(self) -> Settings | None:
        ...

    def save(self, settings: Settings) -> None:
        ...


class JsonSettingsRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Settings | None:
        if not self.path.exists():
            return None

        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return Settings.from_dict(raw)

    def save(self, settings: Settings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temporary_path.write_text(
            json.dumps(settings.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_path.replace(self.path)
