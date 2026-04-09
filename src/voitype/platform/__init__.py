"""Platform detection and backend factory."""

from __future__ import annotations

import os

from voitype.platform.base import ClipboardBackend, InputBackend


def _detect_session() -> str:
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session in ("x11", "wayland"):
        return session
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "x11"


_session: str | None = None
_clipboard: ClipboardBackend | None = None
_input: InputBackend | None = None


def get_session() -> str:
    global _session
    if _session is None:
        _session = _detect_session()
    return _session


def get_clipboard() -> ClipboardBackend:
    global _clipboard
    if _clipboard is None:
        if get_session() == "wayland":
            from voitype.platform.wayland import WaylandClipboard
            _clipboard = WaylandClipboard()
        else:
            from voitype.platform.x11 import X11Clipboard
            _clipboard = X11Clipboard()
    return _clipboard


def get_input() -> InputBackend:
    global _input
    if _input is None:
        if get_session() == "wayland":
            from voitype.platform.wayland import WaylandInput
            _input = WaylandInput()
        else:
            from voitype.platform.x11 import X11Input
            _input = X11Input()
    return _input
