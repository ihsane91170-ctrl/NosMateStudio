import pydirectinput

from app.executors.exceptions import ExecutorDisabledError
from app.executors.keyboard.validation import normalize_and_validate_key
from app.keyboard.layout import KeyboardLayout
from app.keyboard.translator import KeyboardLayoutTranslator

translator = KeyboardLayoutTranslator(
    KeyboardLayout.AZERTY
)


class PyAutoGUIKeyboardExecutor:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def press(self, key: str) -> None:
        normalized = normalize_and_validate_key(key)

        if not self.enabled:
            raise ExecutorDisabledError(
                "Le Keyboard Executor est désactivé."
            )

        physical_key = translator.translate(normalized)
        pydirectinput.press(physical_key)