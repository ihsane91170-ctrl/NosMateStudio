from app.configuration.models import Environment, Hotkeys, Settings

ALLOWED_KEYS = frozenset({"1", "2", "3", "4", "5", "Q", "W", "E", "R", "T"})

DEFAULT_SETTINGS = Settings(
    profile="Default",
    environment=Environment.RECETTE,
    hotkeys=Hotkeys(
        pet_storage="Q",
        xp_map="W",
        summon_weak="1",
        summon_normal="2",
        summon_strong="3",
    ),
)
