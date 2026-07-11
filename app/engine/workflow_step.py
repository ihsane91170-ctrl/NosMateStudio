from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from app.engine.workflow_context import WorkflowContext


class StepResultStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


@dataclass(frozen=True, slots=True)
class StepResult:
    status: StepResultStatus
    message: str = ""

    @classmethod
    def success(cls, message: str = "") -> StepResult:
        return cls(StepResultStatus.SUCCESS, message)

    @classmethod
    def failed(cls, message: str) -> StepResult:
        return cls(StepResultStatus.FAILED, message)

    @classmethod
    def retry(cls, message: str = "") -> StepResult:
        return cls(StepResultStatus.RETRY, message)


class WorkflowStep(ABC):
    """A single executable unit in a workflow."""

    name: str

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__

    @abstractmethod
    def execute(self, context: WorkflowContext) -> StepResult:
        """Execute the step and return an explicit result."""
