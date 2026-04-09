"""Audio recording and Groq Whisper transcription."""

from __future__ import annotations

import io
import sys
import time

import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import resample

from voitype.config import CFG
from voitype.groq_client import get_client
from voitype.state import STATE


_stream: sd.InputStream | None = None
_actual_samplerate: int = CFG.SAMPLE_RATE


def _audio_callback(indata: np.ndarray, frames: int, time_info: object, status: object) -> None:
    if STATE.recording:
        STATE.audio_buffer.append(indata.copy())


def start_recording() -> bool:
    """Start recording. Returns True on success, False on failure."""
    global _stream, _actual_samplerate
    STATE.audio_buffer.clear()
    device = STATE.audio_device if STATE.audio_device >= 0 else None
    print(f"[voitype debug] Recording with device={device}", file=sys.stderr, flush=True)

    # Try target sample rate first, then fall back to device's native rate
    for rate in (CFG.SAMPLE_RATE, 48000, 44100, 32000):
        try:
            _stream = sd.InputStream(
                samplerate=rate,
                channels=CFG.CHANNELS,
                dtype=CFG.DTYPE,
                callback=_audio_callback,
                device=device,
            )
            _stream.start()
            _actual_samplerate = rate
            if rate != CFG.SAMPLE_RATE:
                print(f"[voitype debug] Using fallback sample rate: {rate}Hz", file=sys.stderr, flush=True)
            break
        except Exception:
            continue
    else:
        print(f"Recording error: no supported sample rate", file=sys.stderr, flush=True)
        _stream = None
        STATE.recording = False
        return False

    STATE.recording = True
    STATE.recording_start_time = time.monotonic()
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


def recording_duration() -> float:
    """Return how long the current/last recording lasted in seconds."""
    if STATE.recording_start_time <= 0:
        return 0.0
    return time.monotonic() - STATE.recording_start_time


def transcribe(audio: np.ndarray) -> str | None:
    """Transcribe audio via Groq Whisper. Returns None on failure or hallucination."""
    audio_mono = audio[:, 0] if audio.ndim > 1 else audio

    # Resample to 16000Hz if recorded at a different rate
    if _actual_samplerate != CFG.SAMPLE_RATE:
        num_samples = int(len(audio_mono) * CFG.SAMPLE_RATE / _actual_samplerate)
        audio_mono = resample(audio_mono, num_samples).astype(np.float32)
        print(f"[voitype debug] Resampled {_actual_samplerate}Hz -> {CFG.SAMPLE_RATE}Hz", file=sys.stderr, flush=True)

    audio_int16 = np.clip(audio_mono * 32767, -32768, 32767).astype(np.int16)

    wav_buffer = io.BytesIO()
    wavfile.write(wav_buffer, CFG.SAMPLE_RATE, audio_int16)
    wav_buffer.seek(0)
    wav_buffer.name = "audio.wav"

    client = get_client()

    try:
        transcript = client.audio.transcriptions.create(
            model=CFG.MODEL_WHISPER,
            file=wav_buffer,
            language="ja",
            prompt="音声入力、テスト、確認、送信、メール、レポート、コード、実装、設計",
        )
        text = transcript.text.strip()
        print(f"[voitype debug] Transcription OK: '{text[:50]}'", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[voitype debug] Transcription error: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        # On auth error, reset client and retry once (client may have stale key)
        if "401" in str(e) or "invalid_api_key" in str(e):
            from voitype.groq_client import reset_client
            reset_client()
            wav_buffer.seek(0)
            try:
                transcript = get_client().audio.transcriptions.create(
                    model=CFG.MODEL_WHISPER,
                    file=wav_buffer,
                    language="ja",
                )
                text = transcript.text.strip()
            except Exception as e2:
                raise RuntimeError(f"Transcription failed: {e2}") from e2
        else:
            raise RuntimeError(f"Transcription failed: {e}") from e

    if len(text) < CFG.MIN_TRANSCRIPTION_LENGTH:
        return None

    text_lower = text.lower().rstrip(".!?、。")
    if any(text_lower.startswith(h) for h in CFG.HALLUCINATION_PHRASES):
        return None

    return text
