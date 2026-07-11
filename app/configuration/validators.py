from __future__ import annotations

from dataclasses import dataclass

from app.configuration.models import Action, Settings


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    message: str


class SettingsValidationError(ValueError):
    def __init__(self, issues: list[ValidationIssue]) -> None:
        super().__init__("Configuration invalide.")
        self.issues = tuple(issues)


def normalize_key(key: str) -> str:
    normalized = key.strip()

    if len(normalized) == 1 and normalized.isalpha():
        return normalized.upper()

    return normalized.lower()


def validate_settings(settings: Settings) -> None:
    issues: list[ValidationIssue] = []

    if not settings.profile.strip():
        issues.append(ValidationIssue("profile", "Le nom du profil est obligatoire."))

    normalized: dict[Action, str] = {
        action: normalize_key(key)
        for action, key in settings.hotkeys.as_mapping().items()
    }

    for action, key in normalized.items():
        if not key:
            issues.append(
                ValidationIssue(action.value, "Le raccourci ne peut pas être vide.")
            )

    reverse: dict[str, list[Action]] = {}
    for action, key in normalized.items():
        reverse.setdefault(key, []).append(action)

    for key, actions in reverse.items():
        if key and len(actions) > 1:
            names = ", ".join(action.value for action in actions)
            issues.append(
                ValidationIssue(
                    "hotkeys",
                    f"La touche {key} est utilisée plusieurs fois : {names}.",
                )
            )

    if issues:
        raise SettingsValidationError(issues)
