from typing import Protocol


class KeyboardExecutor(Protocol):
    def press(self, key: str) -> None:
        """Press one configured keyboard key."""