"""Hotkey listener using evdev for raw keyboard input."""

from __future__ import annotations

import selectors
from pathlib import Path
from typing import Callable

import evdev
from evdev import InputDevice, categorize, ecodes


# Right Alt = KEY_RIGHTALT (100), Left Alt = KEY_LEFTALT (56)
KEY_RIGHT_ALT = ecodes.KEY_RIGHTALT
KEY_LEFT_ALT = ecodes.KEY_LEFTALT


class KeyboardHandler:
    def __init__(
        self,
        on_dictation_start: Callable[[], None],
        on_dictation_stop: Callable[[], None],
        on_rewrite_start: Callable[[], None],
        on_rewrite_stop: Callable[[], None],
    ) -> None:
        self._on_dictation_start = on_dictation_start
        self._on_dictation_stop = on_dictation_stop
        self._on_rewrite_start = on_rewrite_start
        self._on_rewrite_stop = on_rewrite_stop
        self._left_alt_held = False
        self._right_alt_held = False
        self._active_mode: str | None = None  # "dictation" or "rewrite"
        self._running = False

    def _find_keyboards(self) -> list[InputDevice]:
        keyboards = []
        for path in sorted(Path("/dev/input/").glob("event*")):
            try:
                dev = InputDevice(str(path))
                caps = dev.capabilities(verbose=False)
                if ecodes.EV_KEY in caps:
                    key_caps = caps[ecodes.EV_KEY]
                    # Must have common keys to be a keyboard
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
            print(
                "WARNING: No keyboard devices found. "
                "Make sure your user is in the 'input' group:\n"
                "  sudo usermod -aG input $USER\n"
                "Then log out and log back in."
            )
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
                                    print(f"Key handler error: {e}")
                    except OSError:
                        # Device disconnected
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
        # value: 0=up, 1=down, 2=hold/repeat
        is_down = event.value in (1, 2)
        is_up = event.value == 0

        if key_code == KEY_LEFT_ALT:
            self._left_alt_held = is_down
        elif key_code == KEY_RIGHT_ALT:
            if is_down and not self._right_alt_held:
                # Key just pressed
                self._right_alt_held = True
                self._start_recording()
            elif is_up and self._right_alt_held:
                # Key released
                self._right_alt_held = False
                self._stop_recording()

    def _start_recording(self) -> None:
        if self._active_mode is not None:
            return
        if self._left_alt_held:
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
