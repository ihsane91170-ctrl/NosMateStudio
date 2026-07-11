import pytest

from app.executors.exceptions import (
    ExecutorDisabledError,
    ExecutorError,
)
from app.executors.wait import (
    RealWaitExecutor,
    SimulationWaitExecutor,
    WaitEvent,
)
from app.executors.wait.validation import validate_duration


def test_simulation_records_wait() -> None:
    executor = SimulationWaitExecutor()

    executor.wait(0.5)

    assert executor.history == [
        WaitEvent(0.5),
    ]


def test_simulation_can_clear() -> None:
    executor = SimulationWaitExecutor()

    executor.wait(1.0)
    executor.clear()

    assert executor.history == []


def test_negative_duration_is_rejected() -> None:
    with pytest.raises(ExecutorError):
        validate_duration(-1)


def test_real_executor_disabled() -> None:
    executor = RealWaitExecutor()

    with pytest.raises(ExecutorDisabledError):
        executor.wait(0.5)