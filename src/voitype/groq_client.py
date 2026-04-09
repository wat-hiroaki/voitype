"""Groq API client initialization."""

from __future__ import annotations

import os
import sys

from groq import Groq

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            # Try loading from settings
            from voitype.state import STATE
            api_key = STATE.api_key or ""
        if not api_key:
            return _show_api_key_dialog()
        _client = Groq(api_key=api_key)
    return _client


def reset_client() -> None:
    """Reset client so next call to get_client() re-initializes."""
    global _client
    _client = None


def _show_api_key_dialog() -> Groq:
    """Show a GTK dialog to get the API key. Falls back to stderr on failure."""
    global _client
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import GLib, Gtk

        GLib.set_prgname("voitype")
        GLib.set_application_name("VoiType")

        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="VoiType: Groq API Key Required",
        )
        dialog.format_secondary_text(
            "Enter your Groq API key.\n"
            "Get a free key at console.groq.com/keys"
        )
        entry = Gtk.Entry()
        entry.set_placeholder_text("gsk_...")
        entry.set_width_chars(50)
        content = dialog.get_content_area()
        content.add(entry)
        dialog.show_all()

        response = dialog.run()
        api_key = entry.get_text().strip()
        dialog.destroy()

        if response == Gtk.ResponseType.OK and api_key:
            from voitype.state import STATE
            STATE.api_key = api_key
            STATE.save_settings()
            _client = Groq(api_key=api_key)
            return _client
    except Exception:
        pass

    print(
        "ERROR: GROQ_API_KEY not set.\n"
        "Get your free API key at https://console.groq.com/keys\n"
        "Then run: GROQ_API_KEY=your_key voitype",
        file=sys.stderr,
    )
    sys.exit(1)
