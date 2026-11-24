#!/bin/bash
# CleanYourPhone Restore All Script (Bash)
# Target Device: adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp
ADB="adb"
DEVICE_ID="adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp"

echo "Re-connecting to device $DEVICE_ID..."
$ADB connect $DEVICE_ID
sleep 1

JSON_PATH="$(dirname "$0")/original-package-states.json"
if [ ! -f "$JSON_PATH" ]; then
    JSON_PATH="$(dirname "$0")/../backups/original-package-states.json"
fi

if [ ! -f "$JSON_PATH" ]; then
    echo "ERROR: original-package-states.json not found!"
    exit 1
fi

echo "Restoring packages to baseline states..."
# Reads package states and enables default/enabled packages
python3 -c '
import json, sys, subprocess
data = json.load(open("'"$JSON_PATH"'"))
for pkg, info in data.items():
    if info.get("original_state") in ["enabled", "default"]:
        subprocess.run(["adb", "-s", "'"$DEVICE_ID"'", "shell", "pm", "enable", "--user", "0", pkg])
'
echo "Restoration complete."
