from app.configuration.models import Environment, Hotkeys, Settings
from app.configuration.repository import JsonSettingsRepository


def test_repository_returns_none_when_file_is_missing(tmp_path) -> None:
    repository = JsonSettingsRepository(tmp_path / "config.local.json")
    assert repository.load() is None


def test_repository_saves_and_loads_settings(tmp_path) -> None:
    repository = JsonSettingsRepository(tmp_path / "config.local.json")
    expected = Settings(
        profile="Default",
        environment=Environment.RECETTE,
        hotkeys=Hotkeys("Q", "W", "_", "1", "2", "3"),
    )

    repository.save(expected)

    assert repository.load() == expected
