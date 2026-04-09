#!/usr/bin/env bash
set -euo pipefail

echo "=== VoiType Setup ==="
echo ""

# Detect distro family
if command -v apt &>/dev/null; then
    PKG_MGR="apt"
elif command -v pacman &>/dev/null; then
    PKG_MGR="pacman"
elif command -v dnf &>/dev/null; then
    PKG_MGR="dnf"
else
    echo "ERROR: Unsupported package manager. Install dependencies manually."
    exit 1
fi

echo "Package manager: $PKG_MGR"

# Detect session type
SESSION_TYPE="${XDG_SESSION_TYPE:-x11}"
echo "Session type: $SESSION_TYPE"
echo ""

# Install system dependencies
echo "Installing system dependencies..."
case "$PKG_MGR" in
    apt)
        sudo apt update
        sudo apt install -y \
            python3-venv python3-dev \
            libgirepository1.0-dev gcc libcairo2-dev pkg-config \
            gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 \
            libspeexdsp-dev portaudio19-dev
        if [ "$SESSION_TYPE" = "x11" ]; then
            sudo apt install -y xdotool xclip
        else
            sudo apt install -y wtype wl-clipboard
        fi
        ;;
    pacman)
        sudo pacman -Syu --noconfirm \
            python gobject-introspection cairo gtk3 \
            libayatana-appindicator speexdsp portaudio
        if [ "$SESSION_TYPE" = "x11" ]; then
            sudo pacman -S --noconfirm xdotool xclip
        else
            sudo pacman -S --noconfirm wtype wl-clipboard
        fi
        ;;
    dnf)
        sudo dnf install -y \
            python3-devel gobject-introspection-devel cairo-devel \
            gtk3-devel libayatana-appindicator-gtk3 \
            speexdsp-devel portaudio-devel
        if [ "$SESSION_TYPE" = "x11" ]; then
            sudo dnf install -y xdotool xclip
        else
            sudo dnf install -y wtype wl-clipboard
        fi
        ;;
esac

echo ""

# Add user to input group for evdev access
if ! groups "$USER" | grep -q '\binput\b'; then
    echo "Adding $USER to 'input' group for keyboard access..."
    sudo usermod -aG input "$USER"
    echo "NOTE: Log out and log back in for group changes to take effect."
fi

echo ""

# Create venv and install
echo "Setting up Python virtual environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Usage:"
echo "  1. Get your free Groq API key at https://console.groq.com/keys"
echo "  2. Run: GROQ_API_KEY=your_key .venv/bin/voitype"
echo ""
echo "Hotkeys:"
echo "  Right Alt (hold)              → Voice dictation"
echo "  Left Alt + Right Alt (hold)   → Smart rewrite (select text first)"
