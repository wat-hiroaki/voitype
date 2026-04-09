"""Recording indicator overlay using GTK3 + Cairo."""

from __future__ import annotations

import math

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, GLib, Gtk

from voitype.config import CFG


class RecordingOverlay(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)
        self.set_default_size(CFG.OVERLAY_WIDTH, CFG.OVERLAY_HEIGHT)

        # Transparent background
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None:
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.connect("draw", self._on_draw)

        self._pulse_alpha = 0.0
        self._pulse_direction = 1
        self._timer_id: int | None = None

    def show(self) -> None:
        # Position at bottom center of screen
        screen = Gdk.Screen.get_default()
        if screen is not None:
            monitor = screen.get_primary_monitor()
            if monitor < 0:
                monitor = 0
            geometry = screen.get_monitor_geometry(monitor)
            x = geometry.x + (geometry.width - CFG.OVERLAY_WIDTH) // 2
            y = geometry.y + geometry.height - CFG.OVERLAY_HEIGHT - CFG.OVERLAY_MARGIN_BOTTOM
            self.move(x, y)

        self._pulse_alpha = 0.0
        self._pulse_direction = 1
        self.show_all()
        self._timer_id = GLib.timeout_add(50, self._pulse_tick)

    def hide(self) -> None:
        if self._timer_id is not None:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        super().hide()

    def _pulse_tick(self) -> bool:
        self._pulse_alpha += 0.05 * self._pulse_direction
        if self._pulse_alpha >= 1.0:
            self._pulse_alpha = 1.0
            self._pulse_direction = -1
        elif self._pulse_alpha <= 0.3:
            self._pulse_alpha = 0.3
            self._pulse_direction = 1
        self.queue_draw()
        return True

    def _on_draw(self, widget: Gtk.Widget, cr: cairo.Context) -> bool:
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()

        # Clear
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

        # Rounded rectangle background (pill shape)
        radius = h / 2
        r, g, b, _ = CFG.OVERLAY_COLOR
        cr.set_source_rgba(r, g, b, self._pulse_alpha * 0.8)
        cr.arc(radius, radius, radius, math.pi / 2, math.pi * 3 / 2)
        cr.arc(w - radius, radius, radius, -math.pi / 2, math.pi / 2)
        cr.close_path()
        cr.fill()

        # Recording dot
        cr.set_source_rgba(1, 0.3, 0.3, self._pulse_alpha)
        cr.arc(24, h / 2, 6, 0, math.pi * 2)
        cr.fill()

        # Text
        cr.set_source_rgba(1, 1, 1, self._pulse_alpha)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        cr.move_to(38, h / 2 + 5)
        cr.show_text("Recording...")

        return True
