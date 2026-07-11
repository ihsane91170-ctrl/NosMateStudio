from app.configuration.models import Environment, Hotkeys, Settings
from app.core.controllers.settings_controller import SettingsController


class ServiceStub:
    def __init__(self) -> None:
        self.settings = Settings(
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
