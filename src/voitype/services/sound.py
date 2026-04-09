"""Audio feedback sounds (start/stop beeps)."""

from __future__ import annotations

import threading

import numpy as np
import sounddevice as sd

from voitype.config import CFG
from voitype.state import STATE


def _play_tone(freq: int, duration: float) -> None:
    """Play a short sine wave tone."""
    try:
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        # Apply fade in/out to avoid click
        fade_len = int(sample_rate * 0.01)
        tone = np.sin(2 * np.pi * freq * t).astype(np.float32)
        tone[:fade_len] *= np.linspace(0, 1, fade_len)
        tone[-fade_len:] *= np.linspace(1, 0, fade_len)
        tone *= 0.3  # Volume
        sd.play(tone, samplerate=sample_rate, blocking=True)
    except Exception:
        pass


def play_start() -> None:
    """Play recording start sound (async)."""
    if STATE.sound_enabled:
        threading.Thread(
            target=_play_tone,
            args=(CFG.SOUND_FREQ_START, CFG.SOUND_DURATION),
            daemon=True,
        ).start()


def play_stop() -> None:
    """Play recording stop sound (async)."""
    if STATE.sound_enabled:
        threading.Thread(
            target=_play_tone,
            args=(CFG.SOUND_FREQ_STOP, CFG.SOUND_DURATION),
            daemon=True,
        ).start()
