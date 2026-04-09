# VoiType

Voice-to-text dictation for Linux with AI-powered text formatting. Hold a key, speak, and get clean formatted text pasted at your cursor.

Powered by [Groq](https://groq.com/) for lightning-fast speech recognition (Whisper) and intelligent text formatting.

## Features

- **Voice Dictation** — Hold a hotkey, speak, release. Formatted text appears at your cursor.
- **Smart Rewrite** — Select text, hold modifier + hotkey, give voice instructions. The selected text is rewritten accordingly.
- **AI Text Formatting** — Automatic filler removal, self-correction resolution, grammar, punctuation, and paragraph formatting via LLM. Can be toggled off for raw transcription.
- **Real-time Feedback** — Visual overlay shows recording, processing, done, and error states. Sound feedback on start/stop. Desktop notifications for errors.
- **Cancel with Escape** — Press Esc during recording to cancel.
- **Configurable Hotkeys** — Change the dictation key and modifier via Settings dialog. Defaults to Right Alt (dictation) and Left Alt (rewrite modifier).
- **Result Popup** — Transcribed text appears in a floating popup. Click to copy to clipboard if auto-paste doesn't work in certain apps.
- **Microphone Selection** — Choose your input device from the Settings dialog. Automatic sample rate fallback for device compatibility.
- **Multi-language** — Supports Japanese, English, and any language Whisper recognizes.
- **X11 + Wayland** — Works on both display servers. Auto-detects your session. Terminal detection for Sway, Hyprland, and niri.
- **System Tray** — Status indicator with settings, formatting/sound toggles, and hotkey reference.
- **Settings Dialog** — Configure API key, hotkeys, microphone, and more from the GUI.
- **Privacy** — No data stored. Audio is sent to Groq API for processing and discarded.

## Requirements

- Linux (Debian/Ubuntu, Arch, Fedora)
- Python 3.10+
- [Groq API key](https://console.groq.com/keys) (free tier available)
- User must be in the `input` group (for hotkey detection)

## Installation

```bash
git clone https://github.com/wat-hiroaki/voitype.git
cd voitype
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Install system dependencies (GTK3, audio libraries, clipboard tools)
2. Add your user to the `input` group if needed
3. Create a Python virtual environment and install VoiType

## Usage

```bash
GROQ_API_KEY=your_api_key_here .venv/bin/voitype
```

Or configure the API key via the Settings dialog (saved to `~/.config/voitype/settings.json`).

### Hotkeys (defaults)

| Key | Action |
|-----|--------|
| **Right Alt** (hold) | Voice dictation — speak and release to paste formatted text |
| **Left Alt + Right Alt** (hold) | Smart rewrite — select text first, then speak rewrite instructions |
| **Esc** | Cancel current recording |

Hotkeys can be changed in Settings (accessible from the system tray icon).

### Visual Feedback

| State | Overlay |
|-------|---------|
| Recording | Red pulsing dot — "Recording..." |
| Recording (Rewrite) | Orange pulsing dot — "Recording (Rewrite)..." |
| Processing | Blue spinner — "Processing..." |
| Done | Green checkmark — auto-hides after 0.8s |
| Error | Red X — shows error message, auto-hides after 2.5s |

### System Tray

Click the microphone icon in your system tray to:
- Toggle AI text formatting on/off
- Toggle sound feedback on/off
- View hotkey reference
- Open Settings dialog
- Quit the application

## How It Works

1. **Record** — Holding the hotkey captures audio from your microphone
2. **Transcribe** — Audio is sent to Groq's Whisper API for fast speech-to-text
3. **Format** — The transcription is cleaned up by an LLM (filler removal, self-corrections, grammar, punctuation, paragraphs)
4. **Paste** — The formatted text is pasted at your cursor position via clipboard

## Configuration

Settings are stored in `~/.config/voitype/settings.json`:

| Setting | Description | Default |
|---------|-------------|---------|
| `formatting_enabled` | AI text formatting | `true` |
| `sound_enabled` | Sound feedback on record start/stop | `true` |
| `hotkey_dictation` | Dictation hotkey (evdev key name) | `KEY_RIGHTALT` |
| `hotkey_modifier` | Rewrite modifier key | `KEY_LEFTALT` |
| `api_key` | Groq API key (alternative to env var) | `""` |
| `audio_device` | Microphone device index (-1 = system default) | `-1` |

## Troubleshooting

### "No keyboard devices found" / Hotkeys not working

Your user needs to be in the `input` group:

```bash
sudo usermod -aG input $USER
# Log out and log back in
```

### API key dialog on every launch

Set the key permanently via environment variable or the Settings dialog:

```bash
echo 'export GROQ_API_KEY=your_key_here' >> ~/.bashrc
source ~/.bashrc
```

### Right Alt conflicts with AltGr (international keyboards)

Open Settings from the tray icon and change the dictation key to another key (e.g., `KEY_F13`, `KEY_SCROLLLOCK`, or `KEY_PAUSE`). Restart VoiType after changing hotkeys.

### No system tray icon

Install the AyatanaAppIndicator3 package:

```bash
# Debian/Ubuntu
sudo apt install gir1.2-ayatanaappindicator3-0.1

# Arch
sudo pacman -S libayatana-appindicator
```

### Audio not recording

Make sure your microphone is working:

```bash
arecord -d 3 test.wav && aplay test.wav
```

## License

MIT
