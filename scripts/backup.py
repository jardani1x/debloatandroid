import subprocess
import json
import os
import sys
import time
from datetime import datetime

ADB_PATH = r"C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"

def get_device_id():
    # Make sure connected
    subprocess.run([ADB_PATH, "connect", "192.168.31.20:33305"], capture_output=True, text=True, check=False)
    res = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, check=False)
    for line in res.stdout.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    return None

def run_adb(device_id, args, text=True):
    cmd = [ADB_PATH, "-s", device_id] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=text, encoding="utf-8" if text else None, errors="replace" if text else None, check=False)
        return res.stdout if not text else res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def main():
    device_id = get_device_id()
    if not device_id:
        print("ERROR: Device not connected.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join("backups", f"backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)

    print(f"[*] Starting comprehensive backup for device {device_id}...")
    print(f"[*] Destination: {backup_dir}")

    # 1. Package inventory & paths
    print("[1/8] Capturing package inventory and paths...")
    packages_f_raw = run_adb(device_id, ["shell", "pm", "list", "packages", "-f", "-u"])
    packages_e_raw = run_adb(device_id, ["shell", "pm", "list", "packages", "-e"])
    packages_d_raw = run_adb(device_id, ["shell", "pm", "list", "packages", "-d"])

    enabled_set = set()
    for line in packages_e_raw.splitlines():
        if line.startswith("package:"):
            enabled_set.add(line.split("package:", 1)[1].strip())

    disabled_set = set()
    for line in packages_d_raw.splitlines():
        if line.startswith("package:"):
            disabled_set.add(line.split("package:", 1)[1].strip())

    package_states = {}
    for line in packages_f_raw.splitlines():
        if not line.startswith("package:"):
            continue
        rest = line[len("package:"):].strip()
        if "=" in rest:
            apk_path, pkg = rest.rsplit("=", 1)
        else:
            apk_path = "unknown"
            pkg = rest

        is_disabled = pkg in disabled_set
        is_enabled = pkg in enabled_set
        
        # State classification
        if is_disabled:
            state = "disabled"
        elif is_enabled:
            state = "enabled"
        else:
            state = "default"

        package_states[pkg] = {
            "package": pkg,
            "path": apk_path,
            "original_state": state,
            "is_system": apk_path.startswith("/system") or apk_path.startswith("/product") or apk_path.startswith("/system_ext") or apk_path.startswith("/vendor") or apk_path.startswith("/apex")
        }

    with open(os.path.join(backup_dir, "original-package-states.json"), "w", encoding="utf-8") as f:
        json.dump(package_states, f, indent=2)

    with open("backups/original-package-states.json", "w", encoding="utf-8") as f:
        json.dump(package_states, f, indent=2)

    with open(os.path.join(backup_dir, "packages-all.txt"), "w", encoding="utf-8") as f:
        f.write(packages_f_raw)

    with open(os.path.join(backup_dir, "packages-disabled.txt"), "w", encoding="utf-8") as f:
        f.write(packages_d_raw)

    # 2. Build properties
    print("[2/8] Capturing build properties...")
    getprop_raw = run_adb(device_id, ["shell", "getprop"])
    with open(os.path.join(backup_dir, "getprop.txt"), "w", encoding="utf-8") as f:
        f.write(getprop_raw)

    # 3. System settings
    print("[3/8] Capturing Android system settings (global, system, secure)...")
    settings_global = run_adb(device_id, ["shell", "settings", "list", "global"])
    settings_system = run_adb(device_id, ["shell", "settings", "list", "system"])
    settings_secure = run_adb(device_id, ["shell", "settings", "list", "secure"])

    with open(os.path.join(backup_dir, "settings_global.txt"), "w", encoding="utf-8") as f:
        f.write(settings_global)
    with open(os.path.join(backup_dir, "settings_system.txt"), "w", encoding="utf-8") as f:
        f.write(settings_system)
    with open(os.path.join(backup_dir, "settings_secure.txt"), "w", encoding="utf-8") as f:
        f.write(settings_secure)

    # 4. Default application assignments
    print("[4/8] Capturing default application assignments...")
    launcher = run_adb(device_id, ["shell", "cmd", "shortcut", "get-default-launcher"])
    keyboard = run_adb(device_id, ["shell", "settings", "get", "secure", "default_input_method"])
    dialer = run_adb(device_id, ["shell", "telecom", "get-default-dialer"])
    sms = run_adb(device_id, ["shell", "settings", "get", "secure", "sms_default_application"])
    webview = run_adb(device_id, ["shell", "dumpsys", "webviewupdate"])

    defaults = {
        "launcher": launcher,
        "keyboard": keyboard,
        "dialer": dialer,
        "sms": sms,
        "webview": webview
    }
    with open(os.path.join(backup_dir, "default-applications.json"), "w", encoding="utf-8") as f:
        json.dump(defaults, f, indent=2)

    # 5. Baseline performance measurements
    print("[5/8] Capturing baseline performance and process snapshot...")
    meminfo = run_adb(device_id, ["shell", "dumpsys", "meminfo"])
    cpuinfo = run_adb(device_id, ["shell", "dumpsys", "cpuinfo"])
    battery = run_adb(device_id, ["shell", "dumpsys", "battery"])
    processes = run_adb(device_id, ["shell", "ps", "-A"])
    df = run_adb(device_id, ["shell", "df", "-h"])

    with open(os.path.join(backup_dir, "baseline_meminfo.txt"), "w", encoding="utf-8") as f:
        f.write(meminfo)
    with open(os.path.join(backup_dir, "baseline_cpuinfo.txt"), "w", encoding="utf-8") as f:
        f.write(cpuinfo)
    with open(os.path.join(backup_dir, "baseline_battery.txt"), "w", encoding="utf-8") as f:
        f.write(battery)
    with open(os.path.join(backup_dir, "baseline_processes.txt"), "w", encoding="utf-8") as f:
        f.write(processes)
    with open(os.path.join(backup_dir, "baseline_df.txt"), "w", encoding="utf-8") as f:
        f.write(df)

    # 6. Baseline screenshot
    print("[6/8] Capturing baseline screen snapshot...")
    run_adb(device_id, ["shell", "screencap", "-p", "/sdcard/cyphone_baseline.png"])
    pull_cmd = [ADB_PATH, "-s", device_id, "pull", "/sdcard/cyphone_baseline.png", os.path.join(backup_dir, "baseline_screenshot.png")]
    subprocess.run(pull_cmd, capture_output=True, check=False)
    run_adb(device_id, ["shell", "rm", "/sdcard/cyphone_baseline.png"])

    # 7. Generate recovery scripts
    print("[7/8] Generating robust rollback and restoration scripts...")
    
    # restore-all.ps1
    ps1_content = f"""# CleanYourPhone Restore All Script (PowerShell)
# Target Device: {device_id}
$adb = "{ADB_PATH}"
$deviceId = "{device_id}"

Write-Host "Re-connecting to device $deviceId..."
& $adb connect $deviceId
Start-Sleep -Seconds 1

Write-Host "Restoring packages to original baseline states from original-package-states.json..."
$jsonPath = Join-Path $PSScriptRoot "original-package-states.json"
if (-not (Test-Path $jsonPath)) {{
    $jsonPath = Join-Path $PSScriptRoot "..\\backups\\original-package-states.json"
}}

if (-not (Test-Path $jsonPath)) {{
    Write-Error "Cannot find original-package-states.json!"
    exit 1
}}

$data = Get-Content $jsonPath -Raw | ConvertFrom-Json
$count = 0
foreach ($prop in $data.PSObject.Properties) {{
    $pkg = $prop.Name
    $info = $prop.Value
    $state = $info.original_state
    
    if ($state -eq "enabled" -or $state -eq "default") {{
        Write-Host "Enabling $pkg..."
        & $adb -s $deviceId shell pm enable --user 0 $pkg
        $count++
    }} elseif ($state -eq "disabled") {{
        Write-Host "Preserving originally disabled: $pkg"
        & $adb -s $deviceId shell pm disable-user --user 0 $pkg
    }}
}}

Write-Host "Restoration complete. Processed $count packages."
"""
    with open("scripts/restore-all.ps1", "w", encoding="utf-8") as f:
        f.write(ps1_content)
    with open(os.path.join(backup_dir, "restore-all.ps1"), "w", encoding="utf-8") as f:
        f.write(ps1_content)

    # restore-all.sh
    sh_content = f"""#!/bin/bash
# CleanYourPhone Restore All Script (Bash)
# Target Device: {device_id}
ADB="adb"
DEVICE_ID="{device_id}"

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
"""
    with open("scripts/restore-all.sh", "w", encoding="utf-8") as f:
        f.write(sh_content)
    with open(os.path.join(backup_dir, "restore-all.sh"), "w", encoding="utf-8") as f:
        f.write(sh_content)

    # restore-package.ps1
    restore_pkg_ps1 = f"""param (
    [Parameter(Mandatory=$true)]
    [string]$PackageName
)
$adb = "{ADB_PATH}"
$deviceId = "{device_id}"

Write-Host "Restoring package $PackageName on $deviceId..."
& $adb connect $deviceId
& $adb -s $deviceId shell pm enable --user 0 $PackageName
Write-Host "Verification:"
& $adb -s $deviceId shell pm list packages -d | Select-String $PackageName
"""
    with open("scripts/restore-package.ps1", "w", encoding="utf-8") as f:
        f.write(restore_pkg_ps1)

    # restore-package.sh
    restore_pkg_sh = f"""#!/bin/bash
PKG="$1"
if [ -z "$PKG" ]; then
    echo "Usage: ./restore-package.sh <package_name>"
    exit 1
fi
DEVICE_ID="{device_id}"
adb -s $DEVICE_ID shell pm enable --user 0 $PKG
adb -s $DEVICE_ID shell pm list packages -d | grep $PKG
"""
    with open("scripts/restore-package.sh", "w", encoding="utf-8") as f:
        f.write(restore_pkg_sh)

    # 8. Initialize transaction log
    print("[8/8] Initializing persistent transaction log...")
    tx_log_path = os.path.join("logs", "transactions.jsonl")
    if not os.path.exists(tx_log_path):
        with open(tx_log_path, "w", encoding="utf-8") as f:
            pass

    print("\n[SUCCESS] Backup and recovery setup completed successfully.")
    print(f"Total packages inventoried: {len(package_states)}")
    print(f"Backup location: {backup_dir}")

if __name__ == "__main__":
    main()
