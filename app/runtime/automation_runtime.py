from dataclasses import dataclass

from app.executors.keyboard import KeyboardExecutor
from app.executors.mouse import MouseExecutor
from app.executors.wait import WaitExecutor


@dataclass(slots=True)
class AutomationRuntime:
    keyboard: KeyboardExecutor
    mouse: MouseExecutor
    wait: WaitExecutor