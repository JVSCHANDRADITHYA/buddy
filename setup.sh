#!/usr/bin/env bash
# setup.sh — install deps and register the `buddy` command
set -e

echo "→ Installing Python dependencies..."
pip install numpy imageio imageio-ffmpeg

echo "→ Making buddy.sh executable..."
chmod +x "$(dirname "$0")/buddy.sh"

INSTALL_PATH="/usr/local/bin/buddy"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v sudo &>/dev/null; then
    echo "→ Linking buddy → $INSTALL_PATH"
    sudo ln -sf "$SCRIPT_DIR/buddy.sh" "$INSTALL_PATH"
    echo "✓ Done. Run: buddy video.mp4"
else
    echo ""
    echo "No sudo available. Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$PATH:$SCRIPT_DIR\""
    echo "  alias buddy='python3 $SCRIPT_DIR/ascii_play/cli.py'"
    echo ""
    echo "Then: source ~/.bashrc && buddy video.mp4"
fi
