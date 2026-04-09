"""Text insertion into the active window via clipboard."""

from __future__ import annotations

import time

from voitype.platform import get_clipboard, get_input


def type_text(text: str) -> None:
    """Copy text to clipboard and simulate paste, then restore original clipboard."""
    clipboard = get_clipboard()
    input_backend = get_input()

    # Save original clipboard
    original = clipboard.get_text()

    # Set new text and paste
    clipboard.set_text(text)
    time.sleep(0.05)

    is_term = input_backend.is_terminal()
    input_backend.paste(terminal=is_term)

    # Restore original clipboard after a short delay
    time.sleep(0.1)
    clipboard.set_text(original)


def paste_text(text: str) -> None:
    """Copy text to clipboard and simulate paste (no restore)."""
    clipboard = get_clipboard()
    input_backend = get_input()

    clipboard.set_text(text)
    time.sleep(0.05)

    is_term = input_backend.is_terminal()
    input_backend.paste(terminal=is_term)


def get_selected_text() -> str:
    """Get currently highlighted/selected text via primary selection."""
    return get_clipboard().get_selection()
