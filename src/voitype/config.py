"""Immutable application configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Audio
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    DTYPE: str = "float32"
    MIN_RECORDING_SECS: float = 0.3

    # Groq models
    MODEL_WHISPER: str = "whisper-large-v3"
    MODEL_LLM: str = "llama-3.3-70b-versatile"

    # LLM prompts
    PROMPT_DICTATION: str = (
        "You are a text formatter. Convert the following speech transcription "
        "into clean, well-formatted text. Remove filler words (um, uh, like, えーと, あの), "
        "resolve self-corrections (keep only the final version), fix grammar, "
        "add proper punctuation, and organize into paragraphs if needed. "
        "Preserve the original language (Japanese, English, etc). "
        "Do NOT add any explanation — output ONLY the formatted text.\n\n"
        "Transcription: {text}"
    )
    PROMPT_REWRITE: str = (
        "Rewrite the following text according to the voice instruction. "
        "Output ONLY the rewritten text, no explanation.\n\n"
        "Instruction: {instruction}\n\nOriginal text: {original}"
    )

    # Hallucination filter — common Whisper outputs on silence
    HALLUCINATION_PHRASES: tuple[str, ...] = (
        "thank you",
        "thanks for watching",
        "you're welcome",
        "subtitle",
        "untertitel",
        "sottotitoli",
        "sous-titres",
        "ご視聴ありがとうございました",
        "おやすみなさい",
    )
    MIN_TRANSCRIPTION_LENGTH: int = 2

    # UI
    APP_NAME: str = "VoiType"
    OVERLAY_WIDTH: int = 220
    OVERLAY_HEIGHT: int = 44
    OVERLAY_MARGIN_BOTTOM: int = 80

    # Settings path
    CONFIG_DIR: str = "~/.config/voitype"
    SETTINGS_FILE: str = "settings.json"

    # Default hotkeys (evdev key names)
    DEFAULT_HOTKEY_DICTATION: str = "KEY_RIGHTALT"
    DEFAULT_HOTKEY_MODIFIER: str = "KEY_LEFTALT"

    # Sound
    SOUND_FREQ_START: int = 880
    SOUND_FREQ_STOP: int = 660
    SOUND_DURATION: float = 0.08

    # Terminal detection keywords
    TERMINAL_KEYWORDS: tuple[str, ...] = (
        "terminal", "konsole", "alacritty", "kitty", "wezterm", "foot",
        "xterm", "urxvt", "st-256color", "terminator", "tilix", "guake",
        "yakuake", "sakura", "terminology", "gnome-terminal", "xfce4-terminal",
        "mate-terminal", "lxterminal", "cool-retro-term",
    )


CFG = Config()
