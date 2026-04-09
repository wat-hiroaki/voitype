"""X11 platform backends using xclip and xdotool."""

from __future__ import annotations

import subprocess

from voitype.config import CFG
from voitype.platform.base import ClipboardBackend, InputBackend


class X11Clipboard(ClipboardBackend):
    def get_text(self) -> str:
        try:
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def get_selection(self) -> str:
        try:
            result = subprocess.run(
                ["xclip", "-selection", "primary", "-o"],
                capture_output=True, text=True, timeout=2,
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def set_text(self, text: str) -> None:
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text, text=True, timeout=2,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass


class X11Input(InputBackend):
    def paste(self, terminal: bool = False) -> None:
        try:
            if terminal:
                subprocess.run(
                    ["xdotool", "key", "--clearmodifiers",
                     "ctrl+shift+v"],
                    timeout=2,
                )
            else:
                subprocess.run(
                    ["xdotool", "key", "--clearmodifiers", "ctrl+v"],
                    timeout=2,
                )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def is_terminal(self) -> bool:
        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow"],
                capture_output=True, text=True, timeout=2,
            )
            window_id = result.stdout.strip()
            if not window_id:
                return False
            result = subprocess.run(
                ["xprop", "-id", window_id, "WM_CLASS"],
                capture_output=True, text=True, timeout=2,
            )
            wm_class = result.stdout.lower()
            return any(kw in wm_class for kw in CFG.TERMINAL_KEYWORDS)
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
