from app.configuration.models import Environment, Hotkeys, Settings

DEFAULT_SETTINGS = Settings(
    profile="Default",
    environment=Environment.RECETTE,
    hotkeys=Hotkeys(
        pet_storage="Q",
        capture_new_pet="W",
        xp_map="_",
        summon_weak="1",
        summon_normal="2",
        summon_strong="3",
    ),
)