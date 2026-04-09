"""Recording/processing/status overlay using GTK3 + Cairo."""

from __future__ import annotations

import math
from enum import Enum, auto

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk

from voitype.config import CFG


class OverlayState(Enum):
    HIDDEN = auto()
    RECORDING = auto()
    RECORDING_REWRITE = auto()
    PROCESSING = auto()
    DONE = auto()
    ERROR = auto()


# Colors (r, g, b)
_COLORS = {
    OverlayState.RECORDING: (0.9, 0.25, 0.25),        # Red
    OverlayState.RECORDING_REWRITE: (0.9, 0.55, 0.1),  # Orange
    OverlayState.PROCESSING: (0.2, 0.6, 1.0),          # Blue
    OverlayState.DONE: (0.2, 0.8, 0.3),                # Green
    OverlayState.ERROR: (0.9, 0.2, 0.2),               # Red
}

_LABELS = {
    OverlayState.RECORDING: "Recording...",
    OverlayState.RECORDING_REWRITE: "Recording (Rewrite)...",
    OverlayState.PROCESSING: "Processing...",
    OverlayState.DONE: "Done",
    OverlayState.ERROR: "Error",
}


class StatusOverlay(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_default_size(CFG.OVERLAY_WIDTH, CFG.OVERLAY_HEIGHT)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.connect("draw", self._on_draw)

        self._state = OverlayState.HIDDEN
        self._error_msg = ""
        self._pulse_alpha = 0.7
        self._pulse_direction = 1
        self._spinner_angle = 0.0
        self._timer_id: int | None = None
        self._auto_hide_id: int | None = None

    def set_state(self, state: OverlayState, error_msg: str = "") -> None:
        """Change overlay state. Call from main thread (via GLib.idle_add)."""
        self._cancel_auto_hide()

        if state == OverlayState.HIDDEN:
            self._stop_timer()
            super().hide()
            self._state = state
            return

        self._state = state
        self._error_msg = error_msg
        self._pulse_alpha = 0.7
        self._pulse_direction = 1
        self._spinner_angle = 0.0

        self._position_on_screen()
        self.show_all()
        self._start_timer()

        if state == OverlayState.DONE:
            self._auto_hide_id = GLib.timeout_add(800, self._auto_hide)
        elif state == OverlayState.ERROR:
            self._auto_hide_id = GLib.timeout_add(2500, self._auto_hide)

    def _auto_hide(self) -> bool:
        self._auto_hide_id = None
        self.set_state(OverlayState.HIDDEN)
        return False

    def _cancel_auto_hide(self) -> None:
        if self._auto_hide_id is not None:
            GLib.source_remove(self._auto_hide_id)
            self._auto_hide_id = None

    def _position_on_screen(self) -> None:
        screen = Gdk.Screen.get_default()
        if screen is not None:
            monitor = screen.get_primary_monitor()
            if monitor < 0:
                monitor = 0
            geometry = screen.get_monitor_geometry(monitor)
            x = geometry.x + (geometry.width - CFG.OVERLAY_WIDTH) // 2
            y = geometry.y + geometry.height - CFG.OVERLAY_HEIGHT - CFG.OVERLAY_MARGIN_BOTTOM
            self.move(x, y)

    def _start_timer(self) -> None:
        if self._timer_id is None:
            self._timer_id = GLib.timeout_add(40, self._tick)

    def _stop_timer(self) -> None:
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None

    def _tick(self) -> bool:
        if self._state in (OverlayState.RECORDING, OverlayState.RECORDING_REWRITE):
            self._pulse_alpha += 0.04 * self._pulse_direction
            if self._pulse_alpha >= 1.0:
                self._pulse_alpha = 1.0
                self._pulse_direction = -1
            elif self._pulse_alpha <= 0.4:
                self._pulse_alpha = 0.4
                self._pulse_direction = 1
        elif self._state == OverlayState.PROCESSING:
            self._spinner_angle = (self._spinner_angle + 8) % 360
        self.queue_draw()
        return True

    def _on_draw(self, widget: Gtk.Widget, cr: cairo.Context) -> bool:
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()

        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        if self._state == OverlayState.HIDDEN:
            return True

        color = _COLORS.get(self._state, (0.5, 0.5, 0.5))
        label = _LABELS.get(self._state, "")
        if self._state == OverlayState.ERROR and self._error_msg:
            label = self._error_msg

        # Alpha
        if self._state in (OverlayState.RECORDING, OverlayState.RECORDING_REWRITE):
            alpha = self._pulse_alpha
        else:
            alpha = 0.9

        # Pill background
        radius = h / 2
        r, g, b = color
        cr.set_source_rgba(r * 0.15, g * 0.15, b * 0.15, alpha * 0.85)
        self._draw_pill(cr, w, h, radius)
        cr.fill()

        # Border
        cr.set_source_rgba(r, g, b, alpha * 0.6)
        cr.set_line_width(1.5)
        self._draw_pill(cr, w, h, radius)
        cr.stroke()

        # Icon area (left side)
        cx, cy = 22, h / 2
        if self._state in (OverlayState.RECORDING, OverlayState.RECORDING_REWRITE):
            # Pulsing red dot
            cr.set_source_rgba(r, g, b, alpha)
            cr.arc(cx, cy, 6, 0, math.pi * 2)
            cr.fill()
        elif self._state == OverlayState.PROCESSING:
            # Spinning arc
            cr.set_source_rgba(r, g, b, 0.9)
            cr.set_line_width(2.5)
            start = math.radians(self._spinner_angle)
            cr.arc(cx, cy, 7, start, start + math.pi * 1.5)
            cr.stroke()
        elif self._state == OverlayState.DONE:
            # Checkmark
            cr.set_source_rgba(r, g, b, 0.9)
            cr.set_line_width(2.5)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(cx - 5, cy)
            cr.line_to(cx - 1, cy + 4)
            cr.line_to(cx + 6, cy - 4)
            cr.stroke()
        elif self._state == OverlayState.ERROR:
            # X mark
            cr.set_source_rgba(r, g, b, 0.9)
            cr.set_line_width(2.5)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.move_to(cx - 4, cy - 4)
            cr.line_to(cx + 4, cy + 4)
            cr.move_to(cx + 4, cy - 4)
            cr.line_to(cx - 4, cy + 4)
            cr.stroke()

        # Label text
        cr.set_source_rgba(1, 1, 1, alpha * 0.95)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(13)
        cr.move_to(38, h / 2 + 4.5)
        cr.show_text(label)

        return True

    @staticmethod
    def _draw_pill(cr: cairo.Context, w: float, h: float, radius: float) -> None:
        cr.arc(radius, radius, radius, math.pi / 2, math.pi * 3 / 2)
        cr.arc(w - radius, radius, radius, -math.pi / 2, math.pi / 2)
        cr.close_path()
