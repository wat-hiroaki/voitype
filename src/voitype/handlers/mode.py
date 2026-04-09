"""Mode handlers for dictation and rewrite."""

from __future__ import annotations

import threading

from gi.repository import GLib

from voitype.config import CFG
from voitype.services import audio, clipboard, formatter, notify, sound
from voitype.state import STATE
from voitype.ui.overlay import OverlayState


def on_dictation_start() -> None:
    if not audio.start_recording():
        notify.mic_error()
        return
    sound.play_start()
    GLib.idle_add(_set_overlay, OverlayState.RECORDING)


def on_dictation_stop() -> None:
    duration = audio.recording_duration()
    raw_audio = audio.stop_recording()
    sound.play_stop()

    if raw_audio is None or duration < CFG.MIN_RECORDING_SECS:
        GLib.idle_add(_set_overlay, OverlayState.HIDDEN)
        if duration > 0.05:  # Only notify if they actually tried (not accidental)
            notify.too_short()
        return

    GLib.idle_add(_set_overlay, OverlayState.PROCESSING)
    threading.Thread(target=_process_dictation, args=(raw_audio,), daemon=True).start()


def on_rewrite_start() -> None:
    if not audio.start_recording():
        notify.mic_error()
        return
    sound.play_start()
    GLib.idle_add(_set_overlay, OverlayState.RECORDING_REWRITE)


def on_rewrite_stop() -> None:
    duration = audio.recording_duration()
    raw_audio = audio.stop_recording()
    sound.play_stop()

    if raw_audio is None or duration < CFG.MIN_RECORDING_SECS:
        GLib.idle_add(_set_overlay, OverlayState.HIDDEN)
        if duration > 0.05:
            notify.too_short()
        return

    GLib.idle_add(_set_overlay, OverlayState.PROCESSING)
    threading.Thread(target=_process_rewrite, args=(raw_audio,), daemon=True).start()


def on_cancel() -> None:
    audio.stop_recording()
    sound.play_stop()
    GLib.idle_add(_set_overlay, OverlayState.HIDDEN)
    notify.cancelled()


def _process_dictation(raw_audio) -> None:
    STATE.processing = True
    GLib.idle_add(_update_tray, True)
    try:
        text = audio.transcribe(raw_audio)
        if text is None:
            GLib.idle_add(_set_overlay, OverlayState.HIDDEN)
            notify.no_speech()
            return

        if STATE.formatting_enabled:
            text = formatter.format_dictation(text)

        clipboard.type_text(text)
        GLib.idle_add(_set_overlay, OverlayState.DONE)
    except Exception as e:
        GLib.idle_add(_set_overlay, OverlayState.ERROR, str(e)[:40])
        notify.api_error(str(e))
    finally:
        STATE.processing = False
        GLib.idle_add(_update_tray, False)


def _process_rewrite(raw_audio) -> None:
    STATE.processing = True
    GLib.idle_add(_update_tray, True)
    try:
        # Get selected text via Ctrl+C (more reliable than PRIMARY selection)
        selected = clipboard.copy_selection()
        if not selected.strip():
            # Fallback to primary selection
            selected = clipboard.get_selected_text()
        if not selected.strip():
            GLib.idle_add(_set_overlay, OverlayState.ERROR, "No text selected")
            return

        instruction = audio.transcribe(raw_audio)
        if instruction is None:
            GLib.idle_add(_set_overlay, OverlayState.HIDDEN)
            notify.no_speech()
            return

        result = formatter.format_rewrite(instruction, selected)
        clipboard.paste_text(result)
        GLib.idle_add(_set_overlay, OverlayState.DONE)
    except Exception as e:
        GLib.idle_add(_set_overlay, OverlayState.ERROR, str(e)[:40])
        notify.api_error(str(e))
    finally:
        STATE.processing = False
        GLib.idle_add(_update_tray, False)


def _set_overlay(state: OverlayState, error_msg: str = "") -> bool:
    if STATE.overlay is not None:
        STATE.overlay.set_state(state, error_msg)
    return False


def _update_tray(processing: bool) -> bool:
    if STATE.tray is not None:
        STATE.tray.set_processing(processing)
    return False
