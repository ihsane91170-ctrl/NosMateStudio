from app.monitor import WorkflowMonitor


def test_monitor_tracks_workflow_progress() -> None:
    monitor = WorkflowMonitor(
        workflow_name="Demo",
        total_steps=7,
    )

    monitor.start()

    monitor.update(0, "PressKey")
    assert monitor.progress.running is True
    assert monitor.progress.current_step == "PressKey"
    assert monitor.progress.current_index == 1

    monitor.update(4, "DoubleClick")
    assert monitor.progress.percentage == 71

    monitor.finish()

    assert monitor.progress.running is False
    assert monitor.progress.current_step == "Terminé"