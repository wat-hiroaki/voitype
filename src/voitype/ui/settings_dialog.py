"""Settings dialog for VoiType."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import sounddevice as sd

from voitype.state import STATE


# Common evdev key names for hotkey selection
_KEY_OPTIONS = [
    "KEY_RIGHTALT",
    "KEY_LEFTALT",
    "KEY_RIGHTCTRL",
    "KEY_LEFTCTRL",
    "KEY_RIGHTMETA",
    "KEY_LEFTMETA",
    "KEY_CAPSLOCK",
    "KEY_SCROLLLOCK",
    "KEY_PAUSE",
    "KEY_F1", "KEY_F2", "KEY_F3", "KEY_F4",
    "KEY_F5", "KEY_F6", "KEY_F7", "KEY_F8",
    "KEY_F9", "KEY_F10", "KEY_F11", "KEY_F12",
    "KEY_F13", "KEY_F14", "KEY_F15",
]


class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window | None = None) -> None:
        super().__init__(
            title="VoiType Settings",
            transient_for=parent,
            modal=True,
        )
        self.set_default_size(420, 300)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )

        content = self.get_content_area()
        content.set_spacing(12)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(12)
        content.set_margin_bottom(8)

        # API Key
        api_frame = Gtk.Frame(label="Groq API Key")
        api_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        api_box.set_margin_start(8)
        api_box.set_margin_end(8)
        api_box.set_margin_top(8)
        api_box.set_margin_bottom(8)
        self._api_entry = Gtk.Entry()
        self._api_entry.set_placeholder_text("gsk_...")
        self._api_entry.set_visibility(False)  # Password-style
        if STATE.api_key:
            self._api_entry.set_text(STATE.api_key)
        api_box.pack_start(self._api_entry, True, True, 0)
        # Toggle visibility button
        show_btn = Gtk.ToggleButton(label="Show")
        show_btn.connect("toggled", lambda b: self._api_entry.set_visibility(b.get_active()))
        api_box.pack_start(show_btn, False, False, 0)
        api_frame.add(api_box)
        content.pack_start(api_frame, False, False, 0)

        # Microphone
        mic_frame = Gtk.Frame(label="Microphone")
        mic_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mic_box.set_margin_start(8)
        mic_box.set_margin_end(8)
        mic_box.set_margin_top(8)
        mic_box.set_margin_bottom(8)
        self._mic_combo = Gtk.ComboBoxText()
        self._mic_combo.append("-1", "System Default")
        active_id = "-1"
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0 and "hw:" in d["name"]:
                name = d["name"].split(":")[0].strip()
                label = f"{name} ({d['max_input_channels']}ch)"
                self._mic_combo.append(str(i), label)
                if i == STATE.audio_device:
                    active_id = str(i)
        self._mic_combo.set_active_id(active_id)
        mic_box.pack_start(self._mic_combo, True, True, 0)
        mic_frame.add(mic_box)
        content.pack_start(mic_frame, False, False, 0)

        # Hotkeys
        hotkey_frame = Gtk.Frame(label="Hotkeys")
        hotkey_grid = Gtk.Grid()
        hotkey_grid.set_row_spacing(8)
        hotkey_grid.set_column_spacing(12)
        hotkey_grid.set_margin_start(8)
        hotkey_grid.set_margin_end(8)
        hotkey_grid.set_margin_top(8)
        hotkey_grid.set_margin_bottom(8)

        hotkey_grid.attach(Gtk.Label(label="Dictation key:", xalign=0), 0, 0, 1, 1)
        self._dictation_combo = self._make_key_combo(STATE.hotkey_dictation)
        hotkey_grid.attach(self._dictation_combo, 1, 0, 1, 1)

        hotkey_grid.attach(Gtk.Label(label="Rewrite modifier:", xalign=0), 0, 1, 1, 1)
        self._modifier_combo = self._make_key_combo(STATE.hotkey_modifier)
        hotkey_grid.attach(self._modifier_combo, 1, 1, 1, 1)

        hotkey_grid.attach(
            Gtk.Label(label="Hold dictation key to record.\nHold modifier + dictation key for rewrite.\nEsc to cancel.", xalign=0),
            0, 2, 2, 1,
        )

        hotkey_frame.add(hotkey_grid)
        content.pack_start(hotkey_frame, False, False, 0)

        # Note about restart
        note = Gtk.Label(label="Hotkey changes require restart to take effect.")
        note.set_xalign(0)
        note.get_style_context().add_class("dim-label")
        content.pack_start(note, False, False, 0)

        self.show_all()

    @staticmethod
    def _make_key_combo(current: str) -> Gtk.ComboBoxText:
        combo = Gtk.ComboBoxText()
        for i, key in enumerate(_KEY_OPTIONS):
            combo.append_text(key)
            if key == current:
                combo.set_active(i)
        if combo.get_active() == -1:
            combo.prepend_text(current)
            combo.set_active(0)
        return combo

    def get_values(self) -> dict:
        mic_id = self._mic_combo.get_active_id()
        return {
            "api_key": self._api_entry.get_text().strip(),
            "hotkey_dictation": self._dictation_combo.get_active_text() or STATE.hotkey_dictation,
            "hotkey_modifier": self._modifier_combo.get_active_text() or STATE.hotkey_modifier,
            "audio_device": int(mic_id) if mic_id is not None else -1,
        }


def show_settings() -> None:
    """Show the settings dialog and apply changes."""
    dialog = SettingsDialog()
    response = dialog.run()

    if response == Gtk.ResponseType.OK:
        values = dialog.get_values()
        changed = False
        if values["api_key"] and values["api_key"] != STATE.api_key:
            STATE.api_key = values["api_key"]
            from voitype.groq_client import reset_client
            reset_client()
            changed = True
        if values["hotkey_dictation"] != STATE.hotkey_dictation:
            STATE.hotkey_dictation = values["hotkey_dictation"]
            changed = True
        if values["hotkey_modifier"] != STATE.hotkey_modifier:
            STATE.hotkey_modifier = values["hotkey_modifier"]
            changed = True
        if values["audio_device"] != STATE.audio_device:
            STATE.audio_device = values["audio_device"]
            changed = True
        if changed:
            STATE.save_settings()

    dialog.destroy()
