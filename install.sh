#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "   CleanYourPhone — Installation & Setup"
echo "=========================================================="

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required."
    exit 1
fi

if ! command -v adb &>/dev/null; then
    echo "WARNING: adb was not found in PATH. Please install Android Platform Tools (e.g. sudo apt install adb / brew install android-platform-tools)"
fi

echo "[*] Installing CleanYourPhone CLI..."
python3 -m pip install -e .

echo ""
echo "[SUCCESS] CleanYourPhone is installed!"
echo "Run 'cleanyourphone --help' or 'cleanyourphone detect' to begin."
