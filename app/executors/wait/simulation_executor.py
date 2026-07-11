from dataclasses import dataclass, field

from app.executors.wait.validation import validate_duration


@dataclass(slots=True)
class WaitEvent:
    seconds: float


@dataclass(slots=True)
class SimulationWaitExecutor:
    history: list[WaitEvent] = field(default_factory=list)

    def wait(self, seconds: float) -> None:
        validate_duration(seconds)
        self.history.append(WaitEvent(seconds))

    def clear(self) -> None:
        self.history.clear()