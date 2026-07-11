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
from app.runtime.automation_runtime import AutomationRuntime
from app.runtime.mode import RuntimeMode


class RuntimeFactory:
    @staticmethod
    def create(mode: RuntimeMode) -> AutomationRuntime:
        if mode is RuntimeMode.SIMULATION:
            return AutomationRuntime(
                keyboard=SimulationKeyboardExecutor(),
                mouse=SimulationMouseExecutor(),
                wait=SimulationWaitExecutor(),
            )

        if mode is RuntimeMode.REAL:
            return AutomationRuntime(
                keyboard=PyAutoGUIKeyboardExecutor(enabled=True),
                mouse=PyAutoGUIMouseExecutor(enabled=True),
                wait=RealWaitExecutor(enabled=True),
            )

        raise ValueError(f"Mode de runtime inconnu : {mode}")