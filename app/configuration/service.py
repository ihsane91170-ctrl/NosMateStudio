from __future__ import annotations

from copy import deepcopy

from app.configuration.defaults import DEFAULT_SETTINGS
from app.configuration.models import Action, Settings
from app.configuration.repository import SettingsRepository
from app.configuration.validators import normalize_key, validate_settings


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository
        self._settings: Settings | None = None

    def load(self) -> Settings:
        loaded = self._repository.load()
        settings = loaded if loaded is not None else deepcopy(DEFAULT_SETTINGS)
        validate_settings(settings)
        self._settings = settings
        return settings

    def current(self) -> Settings:
        if self._settings is None:
            return self.load()
        return self._settings

    def update_hotkey(self, action: Action, key: str) -> Settings:
        current = self.current()
        updated = Settings(
            profile=current.profile,
            environment=current.environment,
            hotkeys=current.hotkeys.with_updated(action, normalize_key(key)),
        )
        validate_settings(updated)
        self._repository.save(updated)
        self._settings = updated
        return updated

    def save(self, settings: Settings) -> Settings:
        validate_settings(settings)
        self._repository.save(settings)
        self._settings = settings
        return settings

    def reset_to_defaults(self) -> Settings:
        settings = deepcopy(DEFAULT_SETTINGS)
        self._repository.save(settings)
        self._settings = settings
        return settings
