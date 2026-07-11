from typing import Protocol

from app.engine.workflow_step import WorkflowStep


class Workflow(Protocol):
    @property
    def name(self) -> str:
        """Return the user-facing workflow name."""

    def steps(self) -> list[WorkflowStep]:
        """Build and return the ordered workflow steps."""