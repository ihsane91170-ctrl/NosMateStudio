from app.configuration.models import Environment, Hotkeys, Settings

DEFAULT_SETTINGS = Settings(
    profile="Default",
    environment=Environment.RECETTE,
    hotkeys=Hotkeys(
        go_to_pet_xp_zone="-",
        capture_new_pet="W",
        summon_weak="1",
        summon_normal="2",
        summon_strong="3",
    ),
)