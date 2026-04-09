"""System tray icon using AyatanaAppIndicator3."""

from __future__ import annotations

from collections.abc import Callable

import gi

gi.require_version("Gtk", "3.0")

try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
    HAS_INDICATOR = True
except (ValueError, ImportError):
    HAS_INDICATOR = False

from gi.repository import Gtk

from voitype.config import CFG
from voitype.state import STATE


class TrayIcon:
    def __init__(self, on_quit: Callable[[], None], on_settings: Callable[[], None]) -> None:
        self._on_quit = on_quit
        self._on_settings = on_settings
        self._indicator = None
        self._status_item: Gtk.MenuItem | None = None

        if not HAS_INDICATOR:
            print("WARNING: AyatanaAppIndicator3 not available. No tray icon.")
            return

        self._indicator = AppIndicator.Indicator.new(
            "voitype",
            "audio-input-microphone",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )
        self._indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self._indicator.set_title(CFG.APP_NAME)

        menu = self._build_menu()
        self._indicator.set_menu(menu)

    def _build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        # Status
        self._status_item = Gtk.MenuItem(label="Ready")
        self._status_item.set_sensitive(False)
        menu.append(self._status_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Formatting toggle
        fmt_item = Gtk.CheckMenuItem(label="AI Text Formatting")
        fmt_item.set_active(STATE.formatting_enabled)
        fmt_item.connect("toggled", self._on_formatting_toggled)
        menu.append(fmt_item)

        # Sound toggle
        snd_item = Gtk.CheckMenuItem(label="Sound Feedback")
        snd_item.set_active(STATE.sound_enabled)
        snd_item.connect("toggled", self._on_sound_toggled)
        menu.append(snd_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Hotkey info
        help_item = Gtk.MenuItem(label="Hotkeys")
        help_submenu = Gtk.Menu()

        for label in (
            f"{STATE.hotkey_dictation} (hold): Dictation",
            f"{STATE.hotkey_modifier} + {STATE.hotkey_dictation} (hold): Rewrite",
            "Esc: Cancel recording",
        ):
            item = Gtk.MenuItem(label=label)
            item.set_sensitive(False)
            help_submenu.append(item)

        help_item.set_submenu(help_submenu)
        menu.append(help_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Settings
        settings_item = Gtk.MenuItem(label="Settings...")
        settings_item.connect("activate", lambda _: self._on_settings())
        menu.append(settings_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _: self._on_quit())
        menu.append(quit_item)

        menu.show_all()
        return menu

    def _on_formatting_toggled(self, item: Gtk.CheckMenuItem) -> None:
        STATE.formatting_enabled = item.get_active()
        STATE.save_settings()

    def _on_sound_toggled(self, item: Gtk.CheckMenuItem) -> None:
        STATE.sound_enabled = item.get_active()
        STATE.save_settings()

    def set_processing(self, processing: bool) -> None:
        if self._status_item is not None:
            self._status_item.set_label("Processing..." if processing else "Ready")
        if self._indicator is not None:
            icon = "audio-input-microphone-high" if processing else "audio-input-microphone"
            self._indicator.set_icon_full(icon, CFG.APP_NAME)
