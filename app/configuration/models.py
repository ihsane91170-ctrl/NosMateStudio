from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class Environment(StrEnum):
    DEVELOPMENT = "development"
    RECETTE = "recette"
    PRODUCTION = "production"


class Action(StrEnum):
    PET_STORAGE = "pet_storage"
    CAPTURE_NEW_PET = "capture_new_pet"
    XP_MAP = "xp_map"
    SUMMON_WEAK = "summon_weak"
    SUMMON_NORMAL = "summon_normal"
    SUMMON_STRONG = "summon_strong"


@dataclass(slots=True)
class Hotkeys:
    pet_storage: str
    capture_new_pet: str
    xp_map: str
    summon_weak: str
    summon_normal: str
    summon_strong: str

    def as_mapping(self) -> dict[Action, str]:
        return {
            Action.PET_STORAGE: self.pet_storage,
            Action.CAPTURE_NEW_PET: self.capture_new_pet,
            Action.XP_MAP: self.xp_map,
            Action.SUMMON_WEAK: self.summon_weak,
            Action.SUMMON_NORMAL: self.summon_normal,
            Action.SUMMON_STRONG: self.summon_strong,
        }

    def get(self, action: Action) -> str:
        return self.as_mapping()[action]

    def with_updated(self, action: Action, key: str) -> Hotkeys:
        values = {
            "pet_storage": self.pet_storage,
            "capture_new_pet": self.capture_new_pet,
            "xp_map": self.xp_map,
            "summon_weak": self.summon_weak,
            "summon_normal": self.summon_normal,
            "summon_strong": self.summon_strong,
        }
        values[action.value] = key
        return Hotkeys(**values)

@dataclass(slots=True)
class Settings:
    profile: str
    environment: Environment
    hotkeys: Hotkeys

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["environment"] = self.environment.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Settings:
        return cls(
            profile=str(data["profile"]),
            environment=Environment(data["environment"]),
            hotkeys=Hotkeys(**data["hotkeys"]),
        )
