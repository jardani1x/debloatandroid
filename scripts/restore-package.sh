#!/bin/bash
PKG="$1"
if [ -z "$PKG" ]; then
    echo "Usage: ./restore-package.sh <package_name>"
    exit 1
fi
DEVICE_ID="adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp"
adb -s $DEVICE_ID shell pm enable --user 0 $PKG
adb -s $DEVICE_ID shell pm list packages -d | grep $PKG
