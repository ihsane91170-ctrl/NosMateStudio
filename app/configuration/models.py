from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Environment(StrEnum):
    DEVELOPMENT = "development"
    RECETTE = "recette"
    PRODUCTION = "production"


class Action(StrEnum):
    GO_TO_PET_XP_ZONE = "go_to_pet_xp_zone"
    CAPTURE_NEW_PET = "capture_new_pet"
    SUMMON_WEAK = "summon_weak"
    SUMMON_NORMAL = "summon_normal"
    SUMMON_STRONG = "summon_strong"


@dataclass(slots=True)
class Hotkeys:
    go_to_pet_xp_zone: str
    capture_new_pet: str
    summon_weak: str
    summon_normal: str
    summon_strong: str

    def as_mapping(self) -> dict[Action, str]:
        return {
            Action.GO_TO_PET_XP_ZONE: self.go_to_pet_xp_zone,
            Action.CAPTURE_NEW_PET: self.capture_new_pet,
            Action.SUMMON_WEAK: self.summon_weak,
            Action.SUMMON_NORMAL: self.summon_normal,
            Action.SUMMON_STRONG: self.summon_strong,
        }

    def get(self, action: Action) -> str:
        return self.as_mapping()[action]

    def with_updated(self, action: Action, key: str) -> Hotkeys:
        values = {
            "go_to_pet_xp_zone": self.go_to_pet_xp_zone,
            "capture_new_pet": self.capture_new_pet,
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
        return {
            "profile": self.profile,
            "environment": self.environment.value,
            "hotkeys": {
                "go_to_pet_xp_zone": (
                    self.hotkeys.go_to_pet_xp_zone
                ),
                "capture_new_pet": self.hotkeys.capture_new_pet,
                "summon_weak": self.hotkeys.summon_weak,
                "summon_normal": self.hotkeys.summon_normal,
                "summon_strong": self.hotkeys.summon_strong,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Settings:
        raw_hotkeys = data["hotkeys"]

        hotkeys = Hotkeys(
            go_to_pet_xp_zone=str(
                raw_hotkeys.get(
                    "go_to_pet_xp_zone",
                    raw_hotkeys.get(
                        "xp_map",
                        raw_hotkeys.get("pet_storage", "_"),
                    ),
                )
            ),
            capture_new_pet=str(
                raw_hotkeys["capture_new_pet"]
            ),
            summon_weak=str(raw_hotkeys["summon_weak"]),
            summon_normal=str(raw_hotkeys["summon_normal"]),
            summon_strong=str(raw_hotkeys["summon_strong"]),
        )

        return cls(
            profile=str(data["profile"]),
            environment=Environment(data["environment"]),
            hotkeys=hotkeys,
        )