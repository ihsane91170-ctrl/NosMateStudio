from app.configuration.defaults import ALLOWED_KEYS
from app.executors.exceptions import InvalidKeyError


def normalize_and_validate_key(key: str) -> str:
    normalized = key.strip().upper()

    if normalized not in ALLOWED_KEYS:
        allowed = ", ".join(sorted(ALLOWED_KEYS))
        raise InvalidKeyError(
            f"La touche {normalized!r} n'est pas autorisée. "
            f"Touches disponibles : {allowed}."
        )

    return normalized