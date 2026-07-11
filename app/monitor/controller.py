from app.monitor.models import WorkflowProgress


class WorkflowMonitor:
    def __init__(self, workflow_name: str, total_steps: int) -> None:
        self.progress = WorkflowProgress(
            workflow_name=workflow_name,
            current_step="",
            current_index=0,
            total_steps=total_steps,
            running=False,
        )

    def start(self) -> None:
        self.progress.running = True

    def update(self, index: int, step_name: str) -> None:
        self.progress.current_index = index + 1
        self.progress.current_step = step_name

    def finish(self) -> None:
        self.progress.running = False
        self.progress.current_step = "Terminé"