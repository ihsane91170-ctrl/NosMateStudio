from app.executors.exceptions import ExecutorError


def validate_coordinates(x: int, y: int) -> None:
    if x < 0 or y < 0:
        raise ExecutorError(
            "Les coordonnées de la souris doivent être positives."
        )