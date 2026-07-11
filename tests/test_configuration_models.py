from app.configuration.models import (
    Action,
    Environment,
    Hotkeys,
    Settings,
)


def test_settings_round_trip() -> None:
    settings = Settings(
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

    restored = Settings.from_dict(settings.to_dict())

    assert restored == settings
    assert (
        restored.hotkeys.get(Action.GO_TO_PET_XP_ZONE)
        == "_"
    )


def test_hotkeys_can_be_updated() -> None:
    original = Hotkeys(
        go_to_pet_xp_zone="_",
        capture_new_pet="W",
        summon_weak="1",
        summon_normal="2",
        summon_strong="3",
    )

    updated = original.with_updated(
        Action.GO_TO_PET_XP_ZONE,
        "E",
    )

    assert original.go_to_pet_xp_zone == "_"
    assert updated.go_to_pet_xp_zone == "E"