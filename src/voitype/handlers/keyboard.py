"""Hotkey listener using evdev for raw keyboard input."""

from __future__ import annotations

import selectors
import sys
from collections.abc import Callable
from pathlib import Path

import evdev
from evdev import InputDevice, ecodes

from voitype.state import STATE


def _resolve_keycode(name: str) -> int:
    """Convert a key name like 'KEY_RIGHTALT' to its evdev keycode."""
    return getattr(ecodes, name)


class KeyboardHandler:
    def __init__(
        self,
        on_dictation_start: Callable[[], None],
        on_dictation_stop: Callable[[], None],
        on_rewrite_start: Callable[[], None],
        on_rewrite_stop: Callable[[], None],
        on_cancel: Callable[[], None],
    ) -> None:
        self._on_dictation_start = on_dictation_start
        self._on_dictation_stop = on_dictation_stop
        self._on_rewrite_start = on_rewrite_start
        self._on_rewrite_stop = on_rewrite_stop
        self._on_cancel = on_cancel
        self._modifier_held = False
        self._hotkey_held = False
        self._active_mode: str | None = None  # "dictation" or "rewrite"
        self._running = False
        self._hotkey_code = _resolve_keycode(STATE.hotkey_dictation)
        self._modifier_code = _resolve_keycode(STATE.hotkey_modifier)

    def _find_keyboards(self) -> list[InputDevice]:
        keyboards = []
        for path in sorted(Path("/dev/input/").glob("event*")):
            try:
                dev = InputDevice(str(path))
                caps = dev.capabilities(verbose=False)
                if ecodes.EV_KEY in caps:
                    key_caps = caps[ecodes.EV_KEY]
                    if ecodes.KEY_A in key_caps or ecodes.KEY_F1 in key_caps:
                        keyboards.append(dev)
                    else:
                        dev.close()
                else:
                    dev.close()
            except (PermissionError, OSError):
                continue
        return keyboards

    def run(self) -> None:
        """Main loop — call from a daemon thread."""
        self._running = True
        keyboards = self._find_keyboards()
        if not keyboards:
            from voitype.services import notify
            notify.no_keyboards()
            return

        sel = selectors.DefaultSelector()
        for kb in keyboards:
            sel.register(kb, selectors.EVENT_READ)

        try:
            while self._running:
                events = sel.select(timeout=0.5)
                for key, _ in events:
                    device: InputDevice = key.fileobj  # type: ignore[assignment]
                    try:
                        for event in device.read():
                            if event.type == ecodes.EV_KEY:
                                try:
                                    self._handle_key(event)
                                except Exception as e:
                                    print(f"Key handler error: {e}", file=sys.stderr, flush=True)
                    except OSError:
                        sel.unregister(device)
                        device.close()
        finally:
            sel.close()
            for kb in keyboards:
                try:
                    kb.close()
                except OSError:
                    pass

    def stop(self) -> None:
        self._running = False

    def _handle_key(self, event: evdev.InputEvent) -> None:
        key_code = event.code
        is_down = event.value in (1, 2)  # press or hold/repeat
        is_up = event.value == 0

        # Escape to cancel recording
        if key_code == ecodes.KEY_ESC and event.value == 1 and self._active_mode is not None:
            self._cancel_recording()
            return

        if key_code == self._modifier_code:
            self._modifier_held = is_down
        elif key_code == self._hotkey_code:
            if is_down and not self._hotkey_held:
                self._hotkey_held = True
                self._start_recording()
            elif is_up and self._hotkey_held:
                self._hotkey_held = False
                self._stop_recording()

    def _start_recording(self) -> None:
        if self._active_mode is not None:
            return
        if STATE.processing:
            from voitype.services import notify
            notify.busy()
            return
        if self._modifier_held:
            self._active_mode = "rewrite"
            self._on_rewrite_start()
        else:
            self._active_mode = "dictation"
            self._on_dictation_start()

    def _stop_recording(self) -> None:
        if self._active_mode == "dictation":
            self._on_dictation_stop()
        elif self._active_mode == "rewrite":
            self._on_rewrite_stop()
        self._active_mode = None

    def _cancel_recording(self) -> None:
        self._on_cancel()
        self._active_mode = None
        self._hotkey_held = False
