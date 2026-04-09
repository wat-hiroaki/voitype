"""Text insertion into the active window via clipboard."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time

from voitype.platform import get_clipboard, get_input
from voitype.state import STATE

_lock = threading.Lock()
_xclip_proc: subprocess.Popen | None = None


def _x11_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    return env


def _set_clipboard_xclip(text: str) -> None:
    """Set clipboard using xclip, keeping the process alive to serve requests."""
    global _xclip_proc
    # Kill previous xclip if any
    if _xclip_proc is not None:
        try:
            _xclip_proc.kill()
        except OSError:
            pass
    _xclip_proc = subprocess.Popen(
        ["xclip", "-selection", "clipboard", "-loops", "0"],
        stdin=subprocess.PIPE, env=_x11_env(),
    )
    _xclip_proc.stdin.write(text.encode("utf-8"))
    _xclip_proc.stdin.close()


def _get_clipboard_xclip() -> str:
    try:
        r = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            capture_output=True, text=True, timeout=2, env=_x11_env(),
        )
        return r.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def type_text(text: str) -> None:
    """Set clipboard via xclip and simulate Ctrl+V into the target window."""
    with _lock:
        input_backend = get_input()
        print(f"[voitype debug] type_text: '{text[:50]}'", file=sys.stderr, flush=True)

        _set_clipboard_xclip(text)
        time.sleep(0.15)

        is_term = input_backend.is_terminal()
        win_id = STATE.target_window
        print(f"[voitype debug] pasting (terminal={is_term}, window={win_id})", file=sys.stderr, flush=True)
        input_backend.paste(terminal=is_term, window_id=win_id)

        # Don't restore clipboard — let the text stay available
        time.sleep(0.3)


def paste_text(text: str) -> None:
    """Set clipboard via xclip and simulate Ctrl+V."""
    with _lock:
        input_backend = get_input()
        _set_clipboard_xclip(text)
        time.sleep(0.15)

        is_term = input_backend.is_terminal()
        win_id = STATE.target_window
        input_backend.paste(terminal=is_term, window_id=win_id)

        time.sleep(0.3)


def copy_selection() -> str:
    """Copy currently selected text by simulating Ctrl+C, then read clipboard."""
    with _lock:
        input_backend = get_input()
        original = _get_clipboard_xclip()
        input_backend.copy()
        time.sleep(0.1)
        selected = _get_clipboard_xclip()
        return selected if selected != original else ""


def get_selected_text() -> str:
    """Get currently highlighted/selected text via primary selection."""
    return get_clipboard().get_selection()
