"""Immutable application configuration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Audio
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    DTYPE: str = "float32"

    # Groq models
    MODEL_WHISPER: str = "whisper-large-v3"
    MODEL_LLM: str = "llama-3.3-70b-versatile"

    # LLM prompts
    PROMPT_DICTATION: str = (
        "You are a text formatter. Convert the following speech transcription "
        "into clean, well-formatted text. Fix grammar, add proper punctuation, "
        "and organize into paragraphs if needed. Preserve the original language "
        "(Japanese, English, etc). Do NOT add any explanation — output ONLY the "
        "formatted text.\n\nTranscription: {text}"
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
    OVERLAY_WIDTH: int = 200
    OVERLAY_HEIGHT: int = 40
    OVERLAY_MARGIN_BOTTOM: int = 80
    OVERLAY_COLOR: tuple[float, float, float, float] = (0.2, 0.6, 1.0, 0.9)

    # Settings path
    CONFIG_DIR: str = "~/.config/voitype"
    SETTINGS_FILE: str = "settings.json"

    # Terminal detection keywords
    TERMINAL_KEYWORDS: tuple[str, ...] = (
        "terminal", "konsole", "alacritty", "kitty", "wezterm", "foot",
        "xterm", "urxvt", "st-256color", "terminator", "tilix", "guake",
        "yakuake", "sakura", "terminology", "gnome-terminal", "xfce4-terminal",
        "mate-terminal", "lxterminal", "cool-retro-term",
    )


CFG = Config()
