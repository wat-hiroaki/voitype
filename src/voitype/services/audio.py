"""Audio recording and Groq Whisper transcription."""

from __future__ import annotations

import io

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from voitype.config import CFG
from voitype.groq_client import get_client
from voitype.state import STATE


_stream: sd.InputStream | None = None


def _audio_callback(indata: np.ndarray, frames: int, time_info: object, status: object) -> None:
    if STATE.recording:
        STATE.audio_buffer.append(indata.copy())


def start_recording() -> bool:
    """Start recording. Returns True on success, False on failure."""
    global _stream
    STATE.audio_buffer.clear()
    try:
        _stream = sd.InputStream(
            samplerate=CFG.SAMPLE_RATE,
            channels=CFG.CHANNELS,
            dtype=CFG.DTYPE,
            callback=_audio_callback,
        )
        _stream.start()
    except Exception as e:
        print(f"Recording error (microphone unavailable?): {e}")
        _stream = None
        STATE.recording = False
        return False
    STATE.recording = True
    return True


def stop_recording() -> np.ndarray | None:
    global _stream
    STATE.recording = False
    if _stream is not None:
        _stream.stop()
        _stream.close()
        _stream = None
    if not STATE.audio_buffer:
        return None
    audio = np.concatenate(STATE.audio_buffer, axis=0)
    STATE.audio_buffer.clear()
    return audio


def transcribe(audio: np.ndarray) -> str | None:
    # Convert float32 audio to int16 WAV
    audio_mono = audio[:, 0] if audio.ndim > 1 else audio
    audio_int16 = np.clip(audio_mono * 32767, -32768, 32767).astype(np.int16)

    wav_buffer = io.BytesIO()
    wavfile.write(wav_buffer, CFG.SAMPLE_RATE, audio_int16)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"

    try:
        transcript = get_client().audio.transcriptions.create(
            model=CFG.MODEL_WHISPER,
            file=wav_buffer,
        )
        text = transcript.text.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

    # Filter hallucinations
    if len(text) < CFG.MIN_TRANSCRIPTION_LENGTH:
        return None
    text_lower = text.lower().rstrip(".!?、。")
    if any(text_lower.startswith(h) for h in CFG.HALLUCINATION_PHRASES):
        return None

    return text
