from dataclasses import dataclass


@dataclass(slots=True)
class WorkflowProgress:
    workflow_name: str
    current_step: str
    current_index: int
    total_steps: int
    running: bool

    @property
    def percentage(self) -> int:
        if self.total_steps == 0:
            return 0

        return int(
            self.current_index * 100 / self.total_steps
        )