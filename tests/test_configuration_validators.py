import pytest

from app.configuration.models import Environment, Hotkeys, Settings
from app.configuration.validators import SettingsValidationError, validate_settings


def test_rejects_unknown_key() -> None:
    settings = Settings(
        profile="Default",
        environment=Environment.RECETTE,
        hotkeys=Hotkeys("A", "W", "1", "2", "3"),
    )

    with pytest.raises(SettingsValidationError):
        validate_settings(settings)


def test_rejects_duplicate_keys() -> None:
    settings = Settings(
        profile="Default",
        environment=Environment.RECETTE,
        hotkeys=Hotkeys("Q", "Q", "1", "2", "3"),
    )

    with pytest.raises(SettingsValidationError) as exc_info:
        validate_settings(settings)

    assert any("utilisée plusieurs fois" in issue.message for issue in exc_info.value.issues)
