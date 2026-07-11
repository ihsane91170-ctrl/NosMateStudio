from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from app.inventory.models import PetProfile
from app.inventory.registry import PetProfileRegistry


class PetProfileRepository(Protocol):
    def load_all(self) -> tuple[PetProfile, ...]:
        ...

    def load_into(self, registry: PetProfileRegistry) -> None:
        ...


class InvalidPetProfileError(ValueError):
    """Raised when a profile file is malformed or invalid."""


class JsonPetProfileRepository:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def load_all(self) -> tuple[PetProfile, ...]:
        if not self.directory.exists():
            return ()

        profiles: list[PetProfile] = []

        for path in sorted(self.directory.glob("*.json")):
            profiles.append(self._load_file(path))

        return tuple(profiles)

    def load_into(self, registry: PetProfileRegistry) -> None:
        for profile in self.load_all():
            registry.register(profile)

    @staticmethod
    def _load_file(path: Path) -> PetProfile:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise InvalidPetProfileError(
                f"Le fichier {path} contient un JSON invalide."
            ) from exc
        except OSError as exc:
            raise InvalidPetProfileError(
                f"Impossible de lire le fichier {path}."
            ) from exc

        if not isinstance(raw, dict):
            raise InvalidPetProfileError(
                f"Le fichier {path} doit contenir un objet JSON."
            )

        try:
            return PetProfile(
                id=str(raw["id"]),
                display_name=str(raw["display_name"]),
                disposable=bool(raw["disposable"]),
                desired_stars=int(raw.get("desired_stars", 6)),
                template_name=(
                    str(raw["template_name"])
                    if raw.get("template_name") is not None
                    else None
                ),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidPetProfileError(
                f"Le profil défini dans {path} est invalide."
            ) from exc