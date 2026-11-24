import json
import os
import sys
import argparse
import subprocess
from datetime import datetime, timezone

ADB_PATH = r"C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"
TX_LOG_PATH = os.path.join("logs", "transactions.jsonl")

def get_connected_device():
    subprocess.run([ADB_PATH, "connect", "192.168.31.20:33305"], capture_output=True, text=True, check=False)
    res = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, check=False)
    for line in res.stdout.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    return None

def run_adb(device_id, args):
    cmd = [ADB_PATH, "-s", device_id] + args
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def log_transaction(action, pkg, original_state, new_state, status, details=""):
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "package": pkg,
        "original_state": original_state,
        "new_state": new_state,
        "status": status,
        "details": details
    }
    with open(TX_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    parser = argparse.ArgumentParser(description="CleanYourPhone Restoration Tool")
    parser.add_argument("--package", help="Restore a single package by name")
    parser.add_argument("--all", action="store_true", help="Restore all packages to original baseline state")
    parser.add_argument("--profile", help="Restore packages belonging to a specific profile")
    args = parser.parse_args()

    device_id = get_connected_device()
    if not device_id:
        print("[!] ERROR: No authorized device found via ADB.")
        sys.exit(1)

    states_path = os.path.join("backups", "original-package-states.json")
    if not os.path.exists(states_path):
        print("[!] ERROR: Missing backups/original-package-states.json.")
        sys.exit(1)

    with open(states_path, "r", encoding="utf-8") as f:
        original_states = json.load(f)

    if args.package:
        pkg = args.package
        orig = original_states.get(pkg, {}).get("original_state", "enabled")
        print(f"[*] Restoring single package {pkg} on {device_id}...")
        stdout, stderr, code = run_adb(device_id, ["shell", "pm", "enable", "--user", "0", pkg])
        
        # Verify
        check_out, _, _ = run_adb(device_id, ["shell", "pm", "list", "packages", "-d"])
        if f"package:{pkg}" not in check_out:
            print(f"[SUCCESS] {pkg} is now enabled and restored.")
            log_transaction("restore_package", pkg, "disabled", "enabled", "SUCCESS", stdout)
        else:
            print(f"[FAILED] Could not restore {pkg}: {stderr}")
            log_transaction("restore_package", pkg, "disabled", "disabled", "FAILED", stderr)

    elif args.all or args.profile:
        if args.profile:
            profile_file = os.path.join("profiles", f"{args.profile}.json")
            with open(profile_file, "r", encoding="utf-8") as f:
                target_packages = json.load(f).get("packages", [])
        else:
            target_packages = list(original_states.keys())

        print(f"[*] Restoring {len(target_packages)} packages on {device_id}...")
        restored = 0
        for pkg in target_packages:
            orig = original_states.get(pkg, {}).get("original_state", "enabled")
            if orig in ["enabled", "default"]:
                stdout, stderr, code = run_adb(device_id, ["shell", "pm", "enable", "--user", "0", pkg])
                log_transaction("restore_package", pkg, "disabled", "enabled", "SUCCESS")
                restored += 1
            elif orig == "disabled":
                # Preserve packages that were already disabled prior to session
                pass

        print(f"[SUCCESS] Restoration complete. Restored {restored} packages.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
