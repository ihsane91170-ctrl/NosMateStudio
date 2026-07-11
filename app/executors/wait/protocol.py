from typing import Protocol


class WaitExecutor(Protocol):
    def wait(self, seconds: float) -> None:
        ...