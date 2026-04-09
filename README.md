<p align="center">
  <h1 align="center">VoiType</h1>
  <p align="center">
    <strong>Voice typing for Linux</strong> — press a key, speak, and text appears at your cursor.
    <br />
    Powered by <a href="https://groq.com/">Groq</a> Whisper for lightning-fast speech recognition.
  </p>
  <p align="center">
    <a href="https://github.com/wat-hiroaki/voitype/stargazers"><img src="https://img.shields.io/github/stars/wat-hiroaki/voitype?style=social" alt="Stars"></a>
    <a href="https://github.com/wat-hiroaki/voitype/blob/main/LICENSE"><img src="https://img.shields.io/github/license/wat-hiroaki/voitype" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python"></a>
    <a href="https://console.groq.com/keys"><img src="https://img.shields.io/badge/API-Groq%20(free)-orange" alt="Groq"></a>
  </p>
</p>

<p align="center">
  <img src="assets/demo.gif" alt="VoiType Demo" width="720" />
</p>

---

## Why VoiType?

Linux has lacked a proper voice typing tool like [Typeless](https://typeless.so/) on macOS. VoiType fills that gap — it's free, open-source, and works with any app on X11 and Wayland.

**Hold a key. Speak. Release. Done.**

Your speech is transcribed by Groq's Whisper API (blazing fast, free tier available), cleaned up by an LLM (filler removal, punctuation, grammar), and pasted at your cursor.

## Features

- **Voice Dictation** — Hold Right Alt, speak, release. Formatted text appears at your cursor.
- **Smart Rewrite** — Select text, hold Left Alt + Right Alt, speak rewrite instructions.
- **AI Formatting** — Automatic filler removal ("um", "uh"), grammar, punctuation via LLM. Toggle off for raw transcription.
- **Result Popup** — Transcribed text shown in a floating popup. Click to copy if auto-paste doesn't work in certain apps.
- **Microphone Selection** — Choose your input device from Settings. Auto sample rate fallback.
- **Visual Overlay** — Recording (red pulse), Processing (blue spinner), Done (green check).
- **Multi-language** — Japanese, English, and any Whisper-supported language.
- **X11 + Wayland** — Auto-detects your session. Works with Sway, Hyprland, niri, GNOME, KDE, etc.
- **System Tray** — Quick access to settings, toggles, and hotkey reference.
- **Privacy** — No data stored. Audio is processed by Groq and discarded.

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/wat-hiroaki/voitype.git
cd voitype
chmod +x setup.sh
./setup.sh

# 2. Log out and back in (required for input group)

# 3. Run
GROQ_API_KEY=your_key_here .venv/bin/voitype
```

Get your free API key at [console.groq.com/keys](https://console.groq.com/keys).

## Hotkeys

| Key | Action |
|-----|--------|
| **Right Alt** (hold) | Voice dictation |
| **Left Alt + Right Alt** (hold) | Smart rewrite (select text first) |
| **Esc** | Cancel recording |

Configurable via Settings (system tray > Settings).

## How It Works

```
Hold key → Record → Groq Whisper API → LLM Format → Paste at cursor
              |                                          |
          microphone                              result popup
```

1. **Record** — Holding the hotkey captures audio from your microphone
2. **Transcribe** — Audio is sent to Groq's Whisper API (~0.5s latency)
3. **Format** — LLM cleans up filler words, self-corrections, adds punctuation
4. **Paste** — Formatted text is pasted at your cursor + shown in result popup

## Configuration

Settings are stored in `~/.config/voitype/settings.json`:

| Setting | Description | Default |
|---------|-------------|---------|
| `formatting_enabled` | AI text formatting | `true` |
| `sound_enabled` | Sound feedback | `true` |
| `hotkey_dictation` | Dictation key | `KEY_RIGHTALT` |
| `hotkey_modifier` | Rewrite modifier | `KEY_LEFTALT` |
| `audio_device` | Microphone index (-1 = default) | `-1` |
| `api_key` | Groq API key | `""` |

## Requirements

- Linux (Debian/Ubuntu, Arch, Fedora)
- Python 3.10+
- [Groq API key](https://console.groq.com/keys) (free tier available)
- `input` group membership (setup.sh handles this)

## Troubleshooting

<details>
<summary><strong>Hotkeys not working</strong></summary>

```bash
sudo usermod -aG input $USER
# Log out and log back in
```
</details>

<details>
<summary><strong>API key dialog on every launch</strong></summary>

```bash
echo 'export GROQ_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

Or set it via the Settings dialog (saved permanently).
</details>

<details>
<summary><strong>Right Alt conflicts with AltGr</strong></summary>

Open Settings from the tray icon and change the dictation key to `KEY_F13`, `KEY_SCROLLLOCK`, or `KEY_PAUSE`.
</details>

<details>
<summary><strong>No system tray icon</strong></summary>

```bash
# Debian/Ubuntu
sudo apt install gir1.2-ayatanaappindicator3-0.1

# Arch
sudo pacman -S libayatana-appindicator
```
</details>

<details>
<summary><strong>Audio not recording</strong></summary>

```bash
arecord -d 3 test.wav && aplay test.wav
```

If that works, try selecting a different microphone in Settings.
</details>

## Contributing

Contributions are welcome! Feel free to open issues or submit PRs.

## License

MIT
