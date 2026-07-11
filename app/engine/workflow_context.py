from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowContext:
    """Mutable execution context shared by workflow steps."""

    data: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def require(self, key: str) -> Any:
        if key not in self.data:
            raise KeyError(f"Valeur requise absente du contexte : {key}")
        return self.data[key]
