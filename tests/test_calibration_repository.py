from app.calibration.models import (
    CalibrationProfile,
    CalibrationTarget,
    RelativePoint,
)
from app.calibration.repository import JsonCalibrationRepository


def test_repository_round_trip(tmp_path) -> None:
    repository = JsonCalibrationRepository(
        tmp_path / "calibration.local.json"
    )
    expected = CalibrationProfile(
        points={
            CalibrationTarget.PET_ICON_1: RelativePoint(10, 20),
            CalibrationTarget.ACCOMPANY_BUTTON: RelativePoint(30, 40),
        }
    )

    repository.save(expected)

    assert repository.load() == expected
