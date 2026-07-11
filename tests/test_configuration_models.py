from app.configuration.models import Action, Environment, Hotkeys, Settings


def test_settings_round_trip() -> None:
    settings = Settings(
        profile="Default",
        environment=Environment.RECETTE,
        hotkeys=Hotkeys("Q", "W", "_", "1", "2", "3"),
    )

    restored = Settings.from_dict(settings.to_dict())

    assert restored == settings
    assert restored.hotkeys.get(Action.XP_MAP) == "_"


def test_hotkey_update_is_immutable() -> None:
    original = Hotkeys("Q", "W", "_", "1", "2", "3")
    updated = original.with_updated(Action.PET_STORAGE, "E")

    assert original.pet_storage == "Q"
    assert updated.pet_storage == "E"
