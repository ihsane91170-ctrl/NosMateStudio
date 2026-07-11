import pytest

from app.engine.workflow_context import WorkflowContext
from app.executors.keyboard import SimulationKeyboardExecutor
from app.executors.mouse import SimulationMouseExecutor
from app.executors.wait import SimulationWaitExecutor
from app.runtime import AutomationRuntime


def build_runtime() -> AutomationRuntime:
    return AutomationRuntime(
        keyboard=SimulationKeyboardExecutor(),
        mouse=SimulationMouseExecutor(),
        wait=SimulationWaitExecutor(),
    )


def test_context_exposes_runtime() -> None:
    runtime = build_runtime()
    context = WorkflowContext(runtime=runtime)

    assert context.require_runtime() is runtime
    assert context.require_runtime().keyboard is runtime.keyboard
    assert context.require_runtime().mouse is runtime.mouse
    assert context.require_runtime().wait is runtime.wait


def test_context_requires_runtime() -> None:
    context = WorkflowContext()

    with pytest.raises(RuntimeError):
        context.require_runtime()


def test_context_stores_and_returns_values() -> None:
    context = WorkflowContext()
    context.set("answer", 42)

    assert context.get("answer") == 42
    assert context.require("answer") == 42


def test_context_require_raises_for_missing_value() -> None:
    context = WorkflowContext()

    with pytest.raises(KeyError):
        context.require("missing")