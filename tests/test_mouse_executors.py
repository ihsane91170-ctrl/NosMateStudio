import pytest

from app.executors.exceptions import (
    ExecutorDisabledError,
    ExecutorError,
)
from app.executors.mouse.pyautogui_executor import (
    PyAutoGUIMouseExecutor,
)
from app.executors.mouse.simulation_executor import (
    MouseEvent,
    SimulationMouseExecutor,
)
from app.executors.mouse.validation import validate_coordinates


def test_simulation_executor_records_history() -> None:
    executor = SimulationMouseExecutor()

    executor.click(100, 200)
    executor.double_click(300, 400)

    assert executor.history == [
        MouseEvent("click", 100, 200),
        MouseEvent("double_click", 300, 400),
    ]


def test_simulation_executor_can_clear_history() -> None:
    executor = SimulationMouseExecutor()

    executor.click(1, 2)

    executor.clear()

    assert executor.history == []

def test_real_executor_disabled() -> None:
    executor = PyAutoGUIMouseExecutor()

    with pytest.raises(ExecutorDisabledError):
        executor.click(100, 200)


def test_negative_coordinates_are_rejected() -> None:
    with pytest.raises(ExecutorError):
        validate_coordinates(-10, 50)