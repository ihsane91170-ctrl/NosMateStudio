from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path(__file__).with_name("config.default.json")
LOCAL_CONFIG = Path(__file__).with_name("config.local.json")


def load_settings() -> dict[str, Any]:
    """Charge la configuration locale si elle existe, sinon la configuration par défaut."""
    source = LOCAL_CONFIG if LOCAL_CONFIG.exists() else DEFAULT_CONFIG
    return json.loads(source.read_text(encoding="utf-8"))
