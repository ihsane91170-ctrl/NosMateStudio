from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.runtime import AutomationRuntime
    from app.safety import SafetyManager


@dataclass(slots=True)
class WorkflowContext:
    """Dependencies and mutable data shared by workflow steps."""

    runtime: AutomationRuntime | None = None
    safety: SafetyManager | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def require_runtime(self) -> AutomationRuntime:
        if self.runtime is None:
            raise RuntimeError(
                "Aucun AutomationRuntime n'est associé au workflow."
            )

        return self.runtime

    def ensure_safe(self) -> None:
        if self.safety is not None:
            self.safety.ensure_safe()

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def require(self, key: str) -> Any:
        if key not in self.data:
            raise KeyError(
                f"Valeur requise absente du contexte : {key}"
            )

        return self.data[key]