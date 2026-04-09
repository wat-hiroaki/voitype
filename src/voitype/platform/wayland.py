"""Wayland platform backends using wl-clipboard and wtype."""

from __future__ import annotations

import json
import subprocess

from voitype.config import CFG
from voitype.platform.base import ClipboardBackend, InputBackend


class WaylandClipboard(ClipboardBackend):
    def get_text(self) -> str:
        try:
            result = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def get_selection(self) -> str:
        try:
            result = subprocess.run(
                ["wl-paste", "--primary", "--no-newline"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def set_text(self, text: str) -> None:
        try:
            subprocess.run(
                ["wl-copy"], input=text, text=True, timeout=2,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass


class WaylandInput(InputBackend):
    def paste(self, terminal: bool = False) -> None:
        try:
            if terminal:
                subprocess.run(
                    ["wtype", "-M", "ctrl", "-M", "shift", "-k", "v",
                     "-m", "shift", "-m", "ctrl"],
                    timeout=2,
                )
            else:
                subprocess.run(
                    ["wtype", "-M", "ctrl", "-k", "v", "-m", "ctrl"],
                    timeout=2,
                )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def is_terminal(self) -> bool:
        # Try niri IPC first
        try:
            result = subprocess.run(
                ["niri", "msg", "-j", "focused-window"],
                capture_output=True, text=True, timeout=2,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                app_id = (data.get("app_id") or "").lower()
                title = (data.get("title") or "").lower()
                combined = f"{app_id} {title}"
                return any(kw in combined for kw in CFG.TERMINAL_KEYWORDS)
        except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
            pass
        # Fallback: assume not a terminal (safe — uses Ctrl+V)
        return False
