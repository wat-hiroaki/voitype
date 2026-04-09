"""Mutable runtime state and settings persistence."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from voitype.config import CFG


def _settings_path() -> Path:
    d = Path(os.path.expanduser(CFG.CONFIG_DIR))
    d.mkdir(parents=True, exist_ok=True)
    return d / CFG.SETTINGS_FILE


@dataclass
class AppState:
    # Runtime
    recording: bool = False
    processing: bool = False
    audio_buffer: list[np.ndarray] = field(default_factory=list)

    # Persisted settings
    formatting_enabled: bool = True

    # UI references (set at runtime)
    overlay: Any = None
    tray: Any = None

    def __post_init__(self) -> None:
        self._load_settings()

    def _load_settings(self) -> None:
        path = _settings_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if "formatting_enabled" in data:
                    self.formatting_enabled = bool(data["formatting_enabled"])
            except (json.JSONDecodeError, OSError):
                pass

    def save_settings(self) -> None:
        path = _settings_path()
        data = {"formatting_enabled": self.formatting_enabled}
        try:
            path.write_text(json.dumps(data, indent=2))
        except OSError:
            pass


STATE = AppState()
