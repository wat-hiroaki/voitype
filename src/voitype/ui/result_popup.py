"""Result popup — shows transcribed text, click to copy to clipboard."""

from __future__ import annotations

import os
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk, Pango


def _x11_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    return env


class ResultPopup(Gtk.Window):
    """Floating popup showing transcription result. Click to copy."""

    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_resizable(False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)
        self.set_app_paintable(True)

        # Main container
        self._box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self._box.set_margin_start(12)
        self._box.set_margin_end(12)
        self._box.set_margin_top(8)
        self._box.set_margin_bottom(8)

        # Text label
        self._label = Gtk.Label()
        self._label.set_max_width_chars(60)
        self._label.set_line_wrap(True)
        self._label.set_line_wrap_mode(Pango.WrapMode.CHAR)
        self._label.set_xalign(0)
        self._box.pack_start(self._label, True, True, 0)

        # Copy icon label
        self._copy_icon = Gtk.Label(label="  Copy")
        self._box.pack_end(self._copy_icon, False, False, 0)

        # Event box for click handling
        event_box = Gtk.EventBox()
        event_box.add(self._box)
        event_box.connect("button-press-event", self._on_click)
        event_box.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add(event_box)

        self.connect("draw", self._on_draw)

        self._text = ""
        self._auto_hide_id: int | None = None

    def show_result(self, text: str) -> None:
        """Show the popup with transcribed text."""
        self._cancel_auto_hide()
        self._text = text

        # Style the label
        display_text = text if len(text) <= 120 else text[:117] + "..."
        self._label.set_markup(
            f'<span foreground="white" font_desc="Sans 11">{GLib.markup_escape_text(display_text)}</span>'
        )
        self._copy_icon.set_markup(
            '<span foreground="#88bbff" font_desc="Sans 10"> [Copy]</span>'
        )

        self._position_on_screen()
        self.show_all()
        self._auto_hide_id = GLib.timeout_add(8000, self._auto_hide)

    def _on_click(self, widget: Gtk.Widget, event: Gdk.EventButton) -> bool:
        """Copy text to clipboard on click."""
        try:
            proc = subprocess.Popen(
                ["xclip", "-selection", "clipboard", "-loops", "0"],
                stdin=subprocess.PIPE, env=_x11_env(),
            )
            proc.stdin.write(self._text.encode("utf-8"))
            proc.stdin.close()
        except Exception:
            pass

        # Flash feedback
        self._copy_icon.set_markup(
            '<span foreground="#66ff88" font_desc="Sans 10"> Copied!</span>'
        )
        GLib.timeout_add(1000, self._auto_hide)
        return True

    def _auto_hide(self) -> bool:
        self._auto_hide_id = None
        self.hide()
        return False

    def _cancel_auto_hide(self) -> None:
        if self._auto_hide_id is not None:
            GLib.source_remove(self._auto_hide_id)
            self._auto_hide_id = None

    def _position_on_screen(self) -> None:
        screen = Gdk.Screen.get_default()
        if screen is None:
            return
        monitor = screen.get_primary_monitor()
        if monitor < 0:
            monitor = 0
        geometry = screen.get_monitor_geometry(monitor)

        # Show above the status overlay position
        self.show_all()
        req = self.get_preferred_size()[1]
        w = min(req.width, geometry.width - 40)
        h = req.height

        x = geometry.x + (geometry.width - w) // 2
        y = geometry.y + geometry.height - h - 140
        self.move(x, y)
        self.resize(w, h)

    def _on_draw(self, widget: Gtk.Widget, cr) -> bool:
        import cairo as _cairo

        w = widget.get_allocated_width()
        h = widget.get_allocated_height()

        cr.set_operator(_cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(_cairo.OPERATOR_OVER)

        # Rounded rectangle background
        radius = 10
        cr.set_source_rgba(0.1, 0.1, 0.15, 0.92)
        cr.arc(radius, radius, radius, 3.14159, 3.14159 * 1.5)
        cr.arc(w - radius, radius, radius, -3.14159 * 0.5, 0)
        cr.arc(w - radius, h - radius, radius, 0, 3.14159 * 0.5)
        cr.arc(radius, h - radius, radius, 3.14159 * 0.5, 3.14159)
        cr.close_path()
        cr.fill()

        # Border
        cr.set_source_rgba(0.3, 0.5, 0.8, 0.5)
        cr.set_line_width(1)
        cr.arc(radius, radius, radius, 3.14159, 3.14159 * 1.5)
        cr.arc(w - radius, radius, radius, -3.14159 * 0.5, 0)
        cr.arc(w - radius, h - radius, radius, 0, 3.14159 * 0.5)
        cr.arc(radius, h - radius, radius, 3.14159 * 0.5, 3.14159)
        cr.close_path()
        cr.stroke()

        return False
