"""X11 platform backends using xdotool."""

from __future__ import annotations

import os
import subprocess
import sys
import time

from voitype.config import CFG
from voitype.platform.base import ClipboardBackend, InputBackend


def _x11_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    return env


class X11Clipboard(ClipboardBackend):
    def get_text(self) -> str:
        try:
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, timeout=2, env=_x11_env(),
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def get_selection(self) -> str:
        try:
            result = subprocess.run(
                ["xclip", "-selection", "primary", "-o"],
                capture_output=True, text=True, timeout=2, env=_x11_env(),
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def set_text(self, text: str) -> None:
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text, text=True, timeout=2, env=_x11_env(),
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass


class X11Input(InputBackend):
    def paste(self, terminal: bool = False, window_id: str = "") -> None:
        env = _x11_env()
        try:
            # Refocus the original window
            if window_id:
                subprocess.run(
                    ["xdotool", "windowactivate", "--sync", window_id],
                    capture_output=True, timeout=2, env=env,
                )
                time.sleep(0.1)

            # Release ALL modifiers first (prevents stuck Alt_R from --clearmodifiers)
            subprocess.run(
                ["xdotool", "keyup", "Alt_R", "Alt_L",
                 "Control_L", "Control_R", "Shift_L", "Shift_R",
                 "Super_L", "Super_R"],
                capture_output=True, timeout=2, env=env,
            )
            time.sleep(0.05)

            # Send Ctrl+V WITHOUT --clearmodifiers (avoids re-pressing modifiers)
            keys = "ctrl+shift+v" if terminal else "ctrl+v"
            result = subprocess.run(
                ["xdotool", "key", keys],
                capture_output=True, text=True, timeout=2, env=env,
            )
            print(f"[voitype debug] xdotool key {keys}: rc={result.returncode}", file=sys.stderr, flush=True)
            if result.returncode != 0:
                print(f"[voitype debug] xdotool stderr: {result.stderr}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[voitype debug] paste error: {e}", file=sys.stderr, flush=True)

    def copy(self) -> None:
        env = _x11_env()
        try:
            subprocess.run(
                ["xdotool", "keyup", "Alt_R", "Alt_L",
                 "Control_L", "Control_R", "Shift_L", "Shift_R"],
                capture_output=True, timeout=2, env=env,
            )
            time.sleep(0.05)
            subprocess.run(
                ["xdotool", "key", "ctrl+c"],
                timeout=2, env=env,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def is_terminal(self) -> bool:
        try:
            result = subprocess.run(
                ["xdotool", "getactivewindow"],
                capture_output=True, text=True, timeout=2, env=_x11_env(),
            )
            window_id = result.stdout.strip()
            if not window_id:
                return False
            result = subprocess.run(
                ["xprop", "-id", window_id, "WM_CLASS"],
                capture_output=True, text=True, timeout=2, env=_x11_env(),
            )
            wm_class = result.stdout.lower()
            return any(kw in wm_class for kw in CFG.TERMINAL_KEYWORDS)
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
