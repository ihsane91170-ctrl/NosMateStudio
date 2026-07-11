import pyautogui

from app.configuration.validators import normalize_key
from app.executors.exceptions import InvalidKeyError


def to_pyautogui_key(key: str) -> str:
    normalized = normalize_key(key)

    if len(normalized) == 1 and normalized.isalpha():
        return normalized.lower()

    return normalized


def normalize_and_validate_key(key: str) -> str:
    normalized = normalize_key(key)
    pyautogui_key = to_pyautogui_key(normalized)

    if not normalized:
        raise InvalidKeyError("Le raccourci clavier ne peut pas être vide.")

    if pyautogui_key not in pyautogui.KEYBOARD_KEYS:
        raise InvalidKeyError(
            f"La touche {normalized!r} n'est pas reconnue par PyAutoGUI."
        )


    return normalized