"""Text insertion into the active window via clipboard."""

from __future__ import annotations

import threading
import time

from voitype.platform import get_clipboard, get_input

_lock = threading.Lock()


def type_text(text: str) -> None:
    """Copy text to clipboard and simulate paste, then restore original clipboard."""
    with _lock:
        clipboard = get_clipboard()
        input_backend = get_input()

        original = clipboard.get_text()
        clipboard.set_text(text)
        time.sleep(0.05)

        is_term = input_backend.is_terminal()
        input_backend.paste(terminal=is_term)

        time.sleep(0.3)
        clipboard.set_text(original)


def paste_text(text: str) -> None:
    """Copy text to clipboard and simulate paste, then restore original clipboard."""
    with _lock:
        clipboard = get_clipboard()
        input_backend = get_input()

        original = clipboard.get_text()
        clipboard.set_text(text)
        time.sleep(0.05)

        is_term = input_backend.is_terminal()
        input_backend.paste(terminal=is_term)

        time.sleep(0.3)
        clipboard.set_text(original)


def copy_selection() -> str:
    """Copy currently selected text by simulating Ctrl+C, then read clipboard."""
    with _lock:
        clipboard = get_clipboard()
        input_backend = get_input()

        original = clipboard.get_text()
        # Simulate Ctrl+C
        input_backend.copy()
        time.sleep(0.1)
        selected = clipboard.get_text()
        # Restore original clipboard
        clipboard.set_text(original)
        return selected if selected != original else ""


def get_selected_text() -> str:
    """Get currently highlighted/selected text via primary selection."""
    return get_clipboard().get_selection()
