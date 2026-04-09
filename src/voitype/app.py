"""Main application entry point."""

from __future__ import annotations

import os
import signal
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

# Suppress libEGL / Mesa warnings
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")


def main() -> None:
    # Validate API key early
    from voitype.groq_client import get_client
    get_client()

    from voitype.handlers.keyboard import KeyboardHandler
    from voitype.handlers.mode import (
        on_dictation_start,
        on_dictation_stop,
        on_rewrite_start,
        on_rewrite_stop,
    )
    from voitype.state import STATE
    from voitype.ui.overlay import RecordingOverlay
    from voitype.ui.tray import TrayIcon

    # Initialize GTK on main thread
    GLib.set_prgname("voitype")
    GLib.set_application_name("VoiType")

    # Create UI
    overlay = RecordingOverlay()
    STATE.overlay = overlay

    def quit_app() -> None:
        keyboard_handler.stop()
        Gtk.main_quit()

    tray = TrayIcon(on_quit=quit_app)
    STATE.tray = tray

    # Keyboard handler in daemon thread
    keyboard_handler = KeyboardHandler(
        on_dictation_start=on_dictation_start,
        on_dictation_stop=on_dictation_stop,
        on_rewrite_start=on_rewrite_start,
        on_rewrite_stop=on_rewrite_stop,
    )
    kb_thread = threading.Thread(target=keyboard_handler.run, daemon=True)
    kb_thread.start()

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda *_: GLib.idle_add(quit_app))
    # GLib needs periodic wakeup to handle signals
    GLib.timeout_add(500, lambda: True)

    print("VoiType is running. Right Alt to dictate, Left Alt + Right Alt to rewrite.")
    Gtk.main()


if __name__ == "__main__":
    main()
