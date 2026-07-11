import pytest

from app.configuration.defaults import DEFAULT_SETTINGS
from app.configuration.models import Action
from app.configuration.service import SettingsService
from app.configuration.validators import SettingsValidationError


class MemoryRepository:
    def __init__(self, settings=None) -> None:
        self.settings = settings

    def load(self):
        return self.settings

    def save(self, settings) -> None:
        self.settings = settings


def test_load_uses_defaults_when_no_local_settings_exist() -> None:
    service = SettingsService(MemoryRepository())
    assert service.load() == DEFAULT_SETTINGS


def test_update_hotkey_saves_normalized_value() -> None:
    repository = MemoryRepository()
    service = SettingsService(repository)

    updated = service.update_hotkey(Action.PET_STORAGE, "e")

    assert updated.hotkeys.pet_storage == "E"
    assert repository.settings == updated


def test_update_rejects_duplicate_hotkey() -> None:
    service = SettingsService(MemoryRepository())

    with pytest.raises(SettingsValidationError):
        service.update_hotkey(Action.PET_STORAGE, "W")
