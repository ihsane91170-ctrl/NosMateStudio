from app.executors.keyboard import SimulationKeyboardExecutor
from app.executors.mouse import SimulationMouseExecutor
from app.executors.wait import SimulationWaitExecutor
from app.runtime import AutomationRuntime


def test_runtime_holds_all_executors() -> None:
    runtime = AutomationRuntime(
        keyboard=SimulationKeyboardExecutor(),
        mouse=SimulationMouseExecutor(),
        wait=SimulationWaitExecutor(),
    )

    assert runtime.keyboard is not None
    assert runtime.mouse is not None
    assert runtime.wait is not None