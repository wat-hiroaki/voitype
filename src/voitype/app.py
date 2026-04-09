"""Main application entry point."""

from __future__ import annotations

import grp
import os
import signal
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

# Suppress libEGL / Mesa warnings
os.environ.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")


def _check_input_group() -> bool:
    """Check if the current user is in the 'input' group."""
    try:
        input_gid = grp.getgrnam("input").gr_gid
        return input_gid in os.getgroups()
    except (KeyError, OSError):
        return True  # Group doesn't exist, skip check


def main() -> None:
    from voitype.groq_client import get_client
    get_client()

    from voitype.handlers.keyboard import KeyboardHandler
    from voitype.handlers.mode import (
        on_cancel,
        on_dictation_start,
        on_dictation_stop,
        on_rewrite_start,
        on_rewrite_stop,
    )
    from voitype.services import notify
    from voitype.state import STATE
    from voitype.ui.overlay import StatusOverlay
    from voitype.ui.settings_dialog import show_settings
    from voitype.ui.tray import TrayIcon

    GLib.set_prgname("voitype")
    GLib.set_application_name("VoiType")

    # Check input group
    if not _check_input_group():
        notify.no_keyboards()

    # Create UI
    overlay = StatusOverlay()
    STATE.overlay = overlay

    def quit_app() -> None:
        keyboard_handler.stop()
        Gtk.main_quit()

    tray = TrayIcon(on_quit=quit_app, on_settings=show_settings)
    STATE.tray = tray

    # Keyboard handler in daemon thread
    keyboard_handler = KeyboardHandler(
        on_dictation_start=on_dictation_start,
        on_dictation_stop=on_dictation_stop,
        on_rewrite_start=on_rewrite_start,
        on_rewrite_stop=on_rewrite_stop,
        on_cancel=on_cancel,
    )
    kb_thread = threading.Thread(target=keyboard_handler.run, daemon=True)
    kb_thread.start()

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, lambda *_: GLib.idle_add(quit_app))
    GLib.timeout_add(500, lambda: True)

    # Welcome notification on first run
    is_first = STATE.is_first_run
    STATE.save_settings()  # Create settings file
    if is_first:
        notify.welcome()

    print("VoiType is running. Use the system tray icon for settings.")
    Gtk.main()


if __name__ == "__main__":
    main()
