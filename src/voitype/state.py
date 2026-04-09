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
    recording_start_time: float = 0.0

    # Persisted settings
    formatting_enabled: bool = True
    sound_enabled: bool = True
    hotkey_dictation: str = CFG.DEFAULT_HOTKEY_DICTATION
    hotkey_modifier: str = CFG.DEFAULT_HOTKEY_MODIFIER
    api_key: str = ""

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
                for key in ("formatting_enabled", "sound_enabled"):
                    if key in data:
                        setattr(self, key, bool(data[key]))
                for key in ("hotkey_dictation", "hotkey_modifier", "api_key"):
                    if key in data and isinstance(data[key], str):
                        setattr(self, key, data[key])
            except (json.JSONDecodeError, OSError):
                pass

    def save_settings(self) -> None:
        path = _settings_path()
        data = {
            "formatting_enabled": self.formatting_enabled,
            "sound_enabled": self.sound_enabled,
            "hotkey_dictation": self.hotkey_dictation,
            "hotkey_modifier": self.hotkey_modifier,
            "api_key": self.api_key,
        }
        try:
            path.write_text(json.dumps(data, indent=2))
        except OSError:
            pass

    @property
    def is_first_run(self) -> bool:
        return not _settings_path().exists()


STATE = AppState()
