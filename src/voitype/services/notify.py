"""Desktop notifications via notify-send."""

from __future__ import annotations

import subprocess

from voitype.config import CFG


def send(summary: str, body: str = "", urgency: str = "normal", icon: str = "audio-input-microphone") -> None:
    """Send a desktop notification. urgency: low, normal, critical."""
    try:
        cmd = [
            "notify-send",
            "--app-name", CFG.APP_NAME,
            "--urgency", urgency,
            "--icon", icon,
            summary,
        ]
        if body:
            cmd.append(body)
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print(f"[{CFG.APP_NAME}] {summary}: {body}")


def welcome() -> None:
    send(
        "VoiType is running",
        "Hold Right Alt to dictate.\nLeft Alt + Right Alt to rewrite.\nEsc to cancel.",
    )


def no_api_key() -> None:
    send(
        "VoiType: API key required",
        "Set GROQ_API_KEY or configure in Settings.\nGet a key at console.groq.com/keys",
        urgency="critical",
        icon="dialog-error",
    )


def no_keyboards() -> None:
    send(
        "VoiType: Keyboard access denied",
        "Add your user to the 'input' group:\nsudo usermod -aG input $USER\nThen log out and log back in.",
        urgency="critical",
        icon="dialog-warning",
    )


def mic_error() -> None:
    send(
        "VoiType: Microphone error",
        "Could not access the microphone. Check your audio settings.",
        urgency="critical",
        icon="dialog-error",
    )


def api_error(detail: str = "") -> None:
    send(
        "VoiType: API error",
        detail or "Could not reach the Groq API. Check your internet connection.",
        urgency="critical",
        icon="dialog-error",
    )


def no_speech() -> None:
    send("VoiType", "No speech detected.", urgency="low")


def too_short() -> None:
    send("VoiType", "Recording too short.", urgency="low")


def cancelled() -> None:
    send("VoiType", "Recording cancelled.", urgency="low")


def busy() -> None:
    send("VoiType", "Still processing the previous recording. Please wait.", urgency="low")
