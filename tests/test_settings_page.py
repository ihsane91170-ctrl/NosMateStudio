from app.configuration.models import Environment, Hotkeys, Settings
from app.ui.pages.settings_page import SettingsPage


class ControllerStub:
    def __init__(self) -> None:
        from PySide6.QtCore import QObject, Signal

        class Signals(QObject):
            settings_loaded = Signal(object)
            settings_saved = Signal(object)
            settings_reset = Signal(object)
            validation_failed = Signal(object)
            unexpected_error = Signal(str)

        self.signals = Signals()
        self.settings_loaded = self.signals.settings_loaded
        self.settings_saved = self.signals.settings_saved
        self.settings_reset = self.signals.settings_reset
        self.validation_failed = self.signals.validation_failed
        self.unexpected_error = self.signals.unexpected_error
        self.loaded = False

    def load(self):
        self.loaded = True
        self.settings_loaded.emit(
            Settings(
                profile="Default",
                environment=Environment.RECETTE,
                hotkeys=Hotkeys(
                    go_to_pet_xp_zone="_",
                    capture_new_pet="W",
                    summon_weak="1",
                    summon_normal="2",
                    summon_strong="3",
                ),
            )
        )

    def save(self, settings):
        self.settings_saved.emit(settings)

    def reset(self):
        pass


def test_settings_page_loads_current_values(qtbot) -> None:
    controller = ControllerStub()
    page = SettingsPage(controller)
    qtbot.addWidget(page)

    assert controller.loaded is True
    assert (
        page._selectors["go_to_pet_xp_zone"].text()
        == "_"
    )
    assert page._selectors["capture_new_pet"].text() == "W"
