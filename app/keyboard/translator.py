from app.keyboard.layout import KeyboardLayout


class KeyboardLayoutTranslator:
    def __init__(self, layout: KeyboardLayout) -> None:
        self.layout = layout

    def translate(self, key: str) -> str:
        normalized = key.strip().upper()

        if self.layout is KeyboardLayout.QWERTY:
            return normalized.lower()

        azerty_mapping = {
            "A": "q",
            "Q": "a",
            "W": "z",
            "Z": "w",
        }

        return azerty_mapping.get(
            normalized,
            normalized.lower(),
        )