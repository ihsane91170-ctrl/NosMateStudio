from app.configuration.models import Environment, Hotkeys, Settings
from app.core.controllers.settings_controller import SettingsController


class ServiceStub:
    def __init__(self) -> None:
        self.settings = Settings(
            profile="Default",
            environment=Environment.RECETTE,
            hotkeys=Hotkeys("Q", "W", "_", "1", "2", "3"),
        )

    def load(self):
        return self.settings

    def save(self, settings):
        self.settings = settings
        return settings

    def reset_to_defaults(self):
        return self.settings

    def update_hotkey(self, action, key):
        return self.settings


def test_controller_emits_loaded_settings(qtbot) -> None:
    controller = SettingsController(ServiceStub())
    received = []
    controller.settings_loaded.connect(received.append)

    controller.load()

    assert len(received) == 1
    assert received[0].profile == "Default"
