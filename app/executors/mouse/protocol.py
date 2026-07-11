from typing import Protocol


class MouseExecutor(Protocol):
    def click(self, x: int, y: int) -> None:
        ...

    def double_click(self, x: int, y: int) -> None:
        ...