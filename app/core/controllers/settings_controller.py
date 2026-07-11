from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from app.configuration.models import Action, Settings
from app.configuration.service import SettingsService
from app.configuration.validators import SettingsValidationError


class SettingsController(QObject):
    settings_loaded = Signal(object)
    settings_saved = Signal(object)
    settings_reset = Signal(object)
    validation_failed = Signal(object)
    unexpected_error = Signal(str)

    def __init__(
        self,
        service: SettingsService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service

    @Slot()
    def load(self) -> None:
        try:
            self.settings_loaded.emit(self._service.load())
        except SettingsValidationError as exc:
            self.validation_failed.emit(exc.issues)
        except Exception as exc:
            self.unexpected_error.emit(str(exc))

    @Slot(object)
    def save(self, settings: Settings) -> None:
        try:
            self.settings_saved.emit(self._service.save(settings))
        except SettingsValidationError as exc:
            self.validation_failed.emit(exc.issues)
        except Exception as exc:
            self.unexpected_error.emit(str(exc))

    @Slot()
    def reset(self) -> None:
        try:
            self.settings_reset.emit(self._service.reset_to_defaults())
        except Exception as exc:
            self.unexpected_error.emit(str(exc))

    @Slot(str, str)
    def update_hotkey(self, action_value: str, key: str) -> None:
        try:
            action = Action(action_value)
            self.settings_saved.emit(self._service.update_hotkey(action, key))
        except SettingsValidationError as exc:
            self.validation_failed.emit(exc.issues)
        except Exception as exc:
            self.unexpected_error.emit(str(exc))
