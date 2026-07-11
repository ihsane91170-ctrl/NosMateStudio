import pytest

from app.workflows import (
    DemoWorkflow,
    DuplicateWorkflowError,
    WorkflowLibrary,
    WorkflowNotFoundError,
)


def test_library_registers_and_returns_workflow() -> None:
    workflow = DemoWorkflow()
    library = WorkflowLibrary()

    library.register(workflow)

    assert library.get("Demo Workflow") is workflow
    assert library.names() == ("Demo Workflow",)
    assert len(library) == 1


def test_library_rejects_duplicate_workflow_name() -> None:
    library = WorkflowLibrary()
    library.register(DemoWorkflow())

    with pytest.raises(DuplicateWorkflowError):
        library.register(DemoWorkflow())


def test_library_rejects_unknown_workflow() -> None:
    library = WorkflowLibrary()

    with pytest.raises(WorkflowNotFoundError):
        library.get("Unknown")


def test_library_returns_all_registered_workflows() -> None:
    workflow = DemoWorkflow()
    library = WorkflowLibrary()
    library.register(workflow)

    assert library.all() == (workflow,)