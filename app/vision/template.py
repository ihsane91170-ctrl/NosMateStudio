from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class VisionTemplate:
    name: str
    path: Path

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "Le nom du template ne peut pas être vide."
            )

        object.__setattr__(self, "name", normalized_name)