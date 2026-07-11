from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class CalibrationTarget(StrEnum):
    PET_ICON_1 = "pet_icon_1"
    PET_ICON_2 = "pet_icon_2"
    PET_ICON_3 = "pet_icon_3"
    ACCOMPANY_BUTTON = "accompany_button"
    PROTOMONSTER_WEAK = "protomonster_weak"
    PROTOMONSTER_NORMAL = "protomonster_normal"
    PROTOMONSTER_STRONG = "protomonster_strong"


TARGET_LABELS: dict[CalibrationTarget, str] = {
    CalibrationTarget.PET_ICON_1: "Icône du familier 1",
    CalibrationTarget.PET_ICON_2: "Icône du familier 2",
    CalibrationTarget.PET_ICON_3: "Icône du familier 3",
    CalibrationTarget.ACCOMPANY_BUTTON: "Bouton Accompagner",
    CalibrationTarget.PROTOMONSTER_WEAK: "Protomonstre faible",
    CalibrationTarget.PROTOMONSTER_NORMAL: "Protomonstre",
    CalibrationTarget.PROTOMONSTER_STRONG: "Protomonstre fort",
}


@dataclass(frozen=True, slots=True)
class RelativePoint:
    x: int
    y: int

    def to_absolute(self, window_left: int, window_top: int) -> tuple[int, int]:
        return window_left + self.x, window_top + self.y


@dataclass(slots=True)
class CalibrationProfile:
    points: dict[CalibrationTarget, RelativePoint] = field(default_factory=dict)

    def is_complete(self) -> bool:
        return all(target in self.points for target in CalibrationTarget)

    def completion(self) -> tuple[int, int]:
        return len(self.points), len(CalibrationTarget)

    def to_dict(self) -> dict[str, Any]:
        return {
            "points": {
                target.value: asdict(point)
                for target, point in self.points.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CalibrationProfile:
        raw_points = data.get("points", {})
        return cls(
            points={
                CalibrationTarget(target): RelativePoint(**point)
                for target, point in raw_points.items()
            }
        )
