"""Mode handlers for dictation and rewrite."""

from __future__ import annotations

import threading

from gi.repository import GLib

from voitype.services import audio, clipboard, formatter
from voitype.state import STATE


def on_dictation_start() -> None:
    if not audio.start_recording():
        return
    GLib.idle_add(_show_overlay)


def on_dictation_stop() -> None:
    raw_audio = audio.stop_recording()
    GLib.idle_add(_hide_overlay)
    if raw_audio is None:
        return
    # Process in background thread to avoid blocking evdev
    threading.Thread(target=_process_dictation, args=(raw_audio,), daemon=True).start()


def on_rewrite_start() -> None:
    if not audio.start_recording():
        return
    GLib.idle_add(_show_overlay)


def on_rewrite_stop() -> None:
    raw_audio = audio.stop_recording()
    GLib.idle_add(_hide_overlay)
    if raw_audio is None:
        return
    threading.Thread(target=_process_rewrite, args=(raw_audio,), daemon=True).start()


def _process_dictation(raw_audio) -> None:
    STATE.processing = True
    GLib.idle_add(_update_tray_processing, True)

    text = audio.transcribe(raw_audio)
    if text is None:
        STATE.processing = False
        GLib.idle_add(_update_tray_processing, False)
        return

    if STATE.formatting_enabled:
        text = formatter.format_dictation(text)

    clipboard.type_text(text)
    STATE.processing = False
    GLib.idle_add(_update_tray_processing, False)


def _process_rewrite(raw_audio) -> None:
    STATE.processing = True
    GLib.idle_add(_update_tray_processing, True)

    # Get selected text first
    selected = clipboard.get_selected_text()
    if not selected.strip():
        STATE.processing = False
        GLib.idle_add(_update_tray_processing, False)
        return

    instruction = audio.transcribe(raw_audio)
    if instruction is None:
        STATE.processing = False
        GLib.idle_add(_update_tray_processing, False)
        return

    result = formatter.format_rewrite(instruction, selected)
    clipboard.paste_text(result)
    STATE.processing = False
    GLib.idle_add(_update_tray_processing, False)


def _show_overlay() -> bool:
    if STATE.overlay is not None:
        STATE.overlay.show()
    return False


def _hide_overlay() -> bool:
    if STATE.overlay is not None:
        STATE.overlay.hide()
    return False


def _update_tray_processing(processing: bool) -> bool:
    if STATE.tray is not None:
        STATE.tray.set_processing(processing)
    return False
