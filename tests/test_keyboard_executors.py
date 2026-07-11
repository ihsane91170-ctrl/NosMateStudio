import pytest

from app.executors.exceptions import (
    ExecutorDisabledError,
    InvalidKeyError,
)
from app.executors.keyboard.pyautogui_executor import (
    PyAutoGUIKeyboardExecutor,
)
from app.executors.keyboard.simulation_executor import (
    SimulationKeyboardExecutor,
)


def test_simulation_executor_records_normalized_keys() -> None:
    executor = SimulationKeyboardExecutor()

    executor.press("q")
    executor.press(" 3 ")

    assert executor.history == ["Q", "3"]


def test_simulation_executor_can_clear_history() -> None:
    executor = SimulationKeyboardExecutor()
    executor.press("W")

    executor.clear()

    assert executor.history == []


def test_executor_rejects_unknown_key() -> None:
    executor = SimulationKeyboardExecutor()

    with pytest.raises(InvalidKeyError):
        executor.press("F12")


def test_real_executor_is_disabled_by_default() -> None:
    executor = PyAutoGUIKeyboardExecutor()

    with pytest.raises(ExecutorDisabledError):
        executor.press("Q")