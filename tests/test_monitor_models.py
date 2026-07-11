from app.monitor import WorkflowProgress


def test_progress_percentage() -> None:
    progress = WorkflowProgress(
        workflow_name="Demo",
        current_step="Click",
        current_index=2,
        total_steps=8,
        running=True,
    )

    assert progress.percentage == 25


def test_progress_empty_workflow() -> None:
    progress = WorkflowProgress(
        workflow_name="Empty",
        current_step="",
        current_index=0,
        total_steps=0,
        running=False,
    )

    assert progress.percentage == 0