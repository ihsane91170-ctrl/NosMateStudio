from app.engine.workflow_context import WorkflowContext
from app.engine.workflow_engine import WorkflowEngine
from app.engine.workflow_state import WorkflowState
from app.engine.workflow_step import StepResult, WorkflowStep


class RecordingStep(WorkflowStep):
    def __init__(self, label: str, result: StepResult | None = None) -> None:
        super().__init__(label)
        self.result = result or StepResult.success()
        self.executed = False

    def execute(self, context: WorkflowContext) -> StepResult:
        self.executed = True
        order = context.get("order", [])
        order.append(self.name)
        context.set("order", order)
        return self.result


class ExplodingStep(WorkflowStep):
    def execute(self, context: WorkflowContext) -> StepResult:
        raise RuntimeError("boom")


def test_engine_executes_steps_in_order() -> None:
    context = WorkflowContext()
    steps = [RecordingStep("one"), RecordingStep("two"), RecordingStep("three")]
    events = []
    engine = WorkflowEngine(events.append)

    state = engine.run(steps, context)

    assert state is WorkflowState.FINISHED
    assert context.require("order") == ["one", "two", "three"]
    assert events[0].name == "workflow_started"
    assert events[-1].name == "workflow_finished"


def test_engine_stops_on_failed_step() -> None:
    first = RecordingStep("first")
    failed = RecordingStep("failed", StepResult.failed("not available"))
    last = RecordingStep("last")
    engine = WorkflowEngine()

    state = engine.run([first, failed, last])

    assert state is WorkflowState.ERROR
    assert first.executed is True
    assert failed.executed is True
    assert last.executed is False
    assert engine.last_error == "not available"


def test_engine_converts_exception_to_error_state() -> None:
    engine = WorkflowEngine()

    state = engine.run([ExplodingStep()])

    assert state is WorkflowState.ERROR
    assert engine.last_error == "boom"


def test_engine_can_be_reset() -> None:
    engine = WorkflowEngine()
    engine.run([RecordingStep("one")])

    engine.reset()

    assert engine.state is WorkflowState.IDLE
    assert engine.current_step_index is None
    assert engine.last_error is None
