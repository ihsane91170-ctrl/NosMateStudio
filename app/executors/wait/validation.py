from app.executors.exceptions import ExecutorError


def validate_duration(seconds: float) -> None:
    if seconds < 0:
        raise ExecutorError(
            "La durée d'attente doit être positive."
        )