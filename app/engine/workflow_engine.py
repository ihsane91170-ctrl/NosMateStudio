from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_state import WorkflowState
from app.engine.workflow_step import StepResultStatus, WorkflowStep


@dataclass(frozen=True, slots=True)
class WorkflowEvent:
    name: str
    step_name: str | None = None
    message: str = ""


EventHandler = Callable[[WorkflowEvent], None]


class WorkflowEngine:
    """Generic synchronous workflow runner.

    The engine is intentionally independent from Qt, PyAutoGUI and NosTale.
    """

    def __init__(self, on_event: EventHandler | None = None) -> None:
        self.state = WorkflowState.IDLE
        self.current_step_index: int | None = None
        self.last_error: str | None = None
        self._stop_requested = False
        self._pause_requested = False
        self._on_event = on_event

    def run(
        self,
        steps: Sequence[WorkflowStep],
        context: WorkflowContext | None = None,
    ) -> WorkflowState:
        if self.state is WorkflowState.RUNNING:
            raise RuntimeError("Un workflow est déjà en cours d'exécution.")

        self._reset_runtime()
        self.state = WorkflowState.RUNNING
        execution_context = context or WorkflowContext()
        self._emit("workflow_started")

        try:
            for index, step in enumerate(steps):
                if self._stop_requested:
                    self.state = WorkflowState.STOPPING
                    self._emit("workflow_stopping")
                    break

                if self._pause_requested:
                    self.state = WorkflowState.PAUSED
                    self._emit("workflow_paused")
                    return self.state

                self.current_step_index = index
                self._emit("step_started", step.name)

                result = step.execute(execution_context)

                if result.status is StepResultStatus.SUCCESS:
                    self._emit("step_completed", step.name, result.message)
                    continue

                if result.status is StepResultStatus.RETRY:
                    self.state = WorkflowState.ERROR
                    self.last_error = (
                        f"L'étape {step.name} demande un retry non géré : "
                        f"{result.message}"
                    )
                    self._emit("workflow_failed", step.name, self.last_error)
                    return self.state

                self.state = WorkflowState.ERROR
                self.last_error = result.message or f"L'étape {step.name} a échoué."
                self._emit("workflow_failed", step.name, self.last_error)
                return self.state

            if self.state is WorkflowState.STOPPING:
                self.state = WorkflowState.IDLE
                self._emit("workflow_stopped")
                return self.state

            self.state = WorkflowState.FINISHED
            self._emit("workflow_finished")
            return self.state

        except Exception as exc:
            self.state = WorkflowState.ERROR
            self.last_error = str(exc)
            step_name = None
            if self.current_step_index is not None and self.current_step_index < len(steps):
                step_name = steps[self.current_step_index].name
            self._emit("workflow_failed", step_name, self.last_error)
            return self.state

    def request_stop(self) -> None:
        self._stop_requested = True

    def request_pause(self) -> None:
        self._pause_requested = True

    def reset(self) -> None:
        self.state = WorkflowState.IDLE
        self.current_step_index = None
        self.last_error = None
        self._stop_requested = False
        self._pause_requested = False
        self._emit("workflow_reset")

    def _reset_runtime(self) -> None:
        self.current_step_index = None
        self.last_error = None
        self._stop_requested = False
        self._pause_requested = False

    def _emit(
        self,
        name: str,
        step_name: str | None = None,
        message: str = "",
    ) -> None:
        if self._on_event is not None:
            self._on_event(
                WorkflowEvent(
                    name=name,
                    step_name=step_name,
                    message=message,
                )
            )
