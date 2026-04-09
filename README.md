# VoiType

Voice-to-text dictation for Linux with AI-powered text formatting. Hold a key, speak, and get clean formatted text pasted at your cursor.

Powered by [Groq](https://groq.com/) for lightning-fast speech recognition (Whisper) and intelligent text formatting.

## Features

- **Voice Dictation** — Hold Right Alt, speak, release. Formatted text appears at your cursor.
- **Smart Rewrite** — Select text, hold Left Alt + Right Alt, give voice instructions. The selected text is rewritten accordingly.
- **AI Text Formatting** — Automatic grammar, punctuation, and paragraph formatting via LLM. Can be toggled off for raw transcription.
- **Multi-language** — Supports Japanese, English, and any language Whisper recognizes.
- **X11 + Wayland** — Works on both display servers. Auto-detects your session.
- **System Tray** — Status indicator with settings and hotkey reference.
- **Privacy** — No data stored. Audio is sent to Groq API for processing and discarded.

## Requirements

- Linux (Debian/Ubuntu, Arch, Fedora)
- Python 3.10+
- [Groq API key](https://console.groq.com/keys) (free tier available)
- User must be in the `input` group (for hotkey detection)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/voitype.git
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

Or export the key in your shell profile:

```bash
echo 'export GROQ_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
.venv/bin/voitype
```

### Hotkeys

| Key | Action |
|-----|--------|
| **Right Alt** (hold) | Voice dictation — speak and release to paste formatted text |
| **Left Alt + Right Alt** (hold) | Smart rewrite — select text first, then speak rewrite instructions |

### System Tray

Right-click the microphone icon in your system tray to:
- Toggle AI text formatting on/off
- View hotkey reference
- Quit the application

## How It Works

1. **Record** — Holding the hotkey captures audio from your microphone
2. **Transcribe** — Audio is sent to Groq's Whisper API for fast speech-to-text
3. **Format** — The transcription is cleaned up by an LLM (grammar, punctuation, structure)
4. **Paste** — The formatted text is pasted at your cursor position via clipboard

## Configuration

Settings are stored in `~/.config/voitype/settings.json`:

- `formatting_enabled` — Enable/disable AI text formatting (default: `true`)

## Troubleshooting

### "No keyboard devices found"

Your user needs to be in the `input` group:

```bash
sudo usermod -aG input $USER
# Log out and log back in
```

### "GROQ_API_KEY environment variable is not set"

Get a free API key at [console.groq.com/keys](https://console.groq.com/keys) and set it:

```bash
export GROQ_API_KEY=your_key_here
```

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
