import pytest

from app.engine.workflow_context import WorkflowContext


def test_context_stores_and_returns_values() -> None:
    context = WorkflowContext()
    context.set("answer", 42)

    assert context.get("answer") == 42
    assert context.require("answer") == 42


def test_context_require_raises_for_missing_value() -> None:
    context = WorkflowContext()

    with pytest.raises(KeyError):
        context.require("missing")
