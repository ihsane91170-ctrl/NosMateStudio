from dataclasses import dataclass, field


@dataclass(slots=True)
class MouseEvent:
    action: str
    x: int
    y: int


@dataclass(slots=True)
class SimulationMouseExecutor:
    history: list[MouseEvent] = field(default_factory=list)

    def click(self, x: int, y: int) -> None:
        self.history.append(
            MouseEvent(
                action="click",
                x=x,
                y=y,
            )
        )

    def double_click(self, x: int, y: int) -> None:
        self.history.append(
            MouseEvent(
                action="double_click",
                x=x,
                y=y,
            )
        )

    def clear(self) -> None:
        self.history.clear()