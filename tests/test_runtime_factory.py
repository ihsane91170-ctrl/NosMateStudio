from app.executors.keyboard import (
    PyAutoGUIKeyboardExecutor,
    SimulationKeyboardExecutor,
)
from app.executors.mouse import (
    PyAutoGUIMouseExecutor,
    SimulationMouseExecutor,
)
from app.executors.wait import (
    RealWaitExecutor,
    SimulationWaitExecutor,
)
from app.runtime import RuntimeFactory, RuntimeMode


def test_factory_creates_simulation_runtime() -> None:
    runtime = RuntimeFactory.create(RuntimeMode.SIMULATION)

    assert isinstance(runtime.keyboard, SimulationKeyboardExecutor)
    assert isinstance(runtime.mouse, SimulationMouseExecutor)
    assert isinstance(runtime.wait, SimulationWaitExecutor)


def test_factory_creates_enabled_real_runtime() -> None:
    runtime = RuntimeFactory.create(RuntimeMode.REAL)

    assert isinstance(runtime.keyboard, PyAutoGUIKeyboardExecutor)
    assert isinstance(runtime.mouse, PyAutoGUIMouseExecutor)
    assert isinstance(runtime.wait, RealWaitExecutor)

    assert runtime.keyboard.enabled is True
    assert runtime.mouse.enabled is True
    assert runtime.wait.enabled is True