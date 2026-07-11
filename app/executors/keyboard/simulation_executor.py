from dataclasses import dataclass, field

from app.executors.keyboard.validation import normalize_and_validate_key


@dataclass(slots=True)
class SimulationKeyboardExecutor:
    history: list[str] = field(default_factory=list)

    def press(self, key: str) -> None:
        normalized = normalize_and_validate_key(key)
        self.history.append(normalized)

    def clear(self) -> None:
        self.history.clear()