import time

from app.executors.exceptions import ExecutorDisabledError
from app.executors.wait.validation import validate_duration


class RealWaitExecutor:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def wait(self, seconds: float) -> None:
        validate_duration(seconds)

        if not self.enabled:
            raise ExecutorDisabledError(
                "Le Wait Executor est désactivé."
            )

        time.sleep(seconds)