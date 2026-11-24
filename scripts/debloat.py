import json
import os
import sys
import time
import argparse
import subprocess
from datetime import datetime, timezone

ADB_PATH = r"C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"
EXPECTED_DEVICE = "adb-UBS1241116012667-mmsCJ7._adb-tls-connect._tcp"
TX_LOG_PATH = os.path.join("logs", "transactions.jsonl")

PROTECTED_SYSTEM_PACKAGES = {
    "android",
    "com.android.systemui",
    "com.android.settings",
    "com.android.shell",
    "com.android.phone",
    "com.google.android.gms",
    "com.android.vending",
    "com.google.android.packageinstaller",
    "com.google.android.permissioncontroller",
    "com.google.android.webview",
    "com.google.android.inputmethod.latin",
    "com.android.launcher3",
    "com.google.android.dialer",
    "com.google.android.apps.messaging",
    "com.android.server.telecom",
    "com.android.providers.telephony",
    "com.spreadtrum.ims",
    "com.unisoc.phone",
    "com.android.providers.settings",
    "com.android.providers.media",
    "com.google.android.providers.media.module",
    "com.android.providers.contacts",
    "com.google.android.contacts",
    "com.android.providers.downloads",
    "com.google.android.documentsui",
    "com.android.externalstorage",
    "com.android.storagemanager",
    "com.android.keychain",
    "com.android.credentialmanager",
    "com.google.android.ext.services",
    "com.google.android.ext.shared",
    "com.google.android.gsf",
    "com.google.android.modulemetadata",
    "com.google.android.configupdater",
    "com.google.android.cellbroadcastreceiver",
    "com.android.location.fused",
    "com.spreadtrum.sgps",
    "com.google.android.networkstack",
    "com.android.bluetooth",
    "com.unisoc.wifi",
    "com.android.camera2",
    "com.android.cameraextensions",
    "org.ifaa.aidl.manager",
    "com.tencent.soter.soterserver",
    "com.android.nfc",
    "com.google.android.apps.walletnfcrel",
    "com.google.android.apps.googleassistant",
    "com.google.android.googlequicksearchbox",
    "com.nianticlabs.pokemongo",
    "com.whatsapp",
    "org.telegram.messenger",
    "com.tailscale.ipn",
    "com.azure.authenticator"
}

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

def check_system_stability(device_id):
    # Check if systemui and settings respond
    out, _, code = run_adb(device_id, ["shell", "pidof", "com.android.systemui"])
    if code != 0 or not out:
        return False, "SystemUI process is not running or crashed"
    out_pm, _, code_pm = run_adb(device_id, ["shell", "pm", "path", "android"])
    if code_pm != 0 or not out_pm:
        return False, "Package manager service unresponsive"
    return True, "Stable"

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
    parser = argparse.ArgumentParser(description="CleanYourPhone Controlled Debloat Executor")
    parser.add_argument("--profile", choices=["conservative", "balanced", "aggressive"], default="balanced", help="Profile to execute")
    parser.add_argument("--packages", nargs="+", help="Explicit list of packages to disable")
    parser.add_argument("--batch-size", type=int, default=5, help="Batch size (max 5)")
    parser.add_argument("--apply", action="store_true", help="Explicitly apply changes (defaults to dry-run)")
    args = parser.parse_args()

    is_dry_run = not args.apply

    print("==============================================================")
    print("CleanYourPhone — Controlled Batch Debloat Execution")
    print(f"Mode: {'[DRY RUN - No changes will be made]' if is_dry_run else '[APPLY - Live Modifications Enabled]'}")
    print("==============================================================")

    # 1. Device identity check
    device_id = get_connected_device()
    if not device_id:
        print("[!] ERROR: No authorized device found via ADB.")
        sys.exit(1)
    
    print(f"[*] Connected device: {device_id}")

    # 2. Verify target user
    user_out, _, _ = run_adb(device_id, ["shell", "am", "get-current-user"])
    if user_out != "0":
        print(f"[!] ERROR: Target user is '{user_out}', expected User 0. Aborting for safety.")
        sys.exit(1)
    print("[*] Target Android User verified: 0 (Owner)")

    # 3. Load baseline package states
    states_path = os.path.join("backups", "original-package-states.json")
    if not os.path.exists(states_path):
        print("[!] ERROR: Missing backups/original-package-states.json! Run backup first.")
        sys.exit(1)
    with open(states_path, "r", encoding="utf-8") as f:
        original_states = json.load(f)

    # 4. Resolve package list
    if args.packages:
        target_packages = args.packages
    else:
        profile_file = os.path.join("profiles", f"{args.profile}.json")
        with open(profile_file, "r", encoding="utf-8") as f:
            target_packages = json.load(f).get("packages", [])

    print(f"[*] Target Profile: {args.profile} ({len(target_packages)} packages queued)")

    # 5. Filter through protection list
    safe_to_disable = []
    for pkg in target_packages:
        if pkg in PROTECTED_SYSTEM_PACKAGES or pkg.endswith(".overlay") or any(pkg.startswith(p) for p in ["android.unisoc.", "android.overlay."]):
            print(f"  [REJECTED - PROTECTED] {pkg} cannot be disabled!")
        else:
            safe_to_disable.append(pkg)

    print(f"[*] Approved safe candidates: {len(safe_to_disable)}")

    # 6. Process in batches
    batch_size = min(args.batch_size, 5)
    batches = [safe_to_disable[i:i + batch_size] for i in range(0, len(safe_to_disable), batch_size)]

    total_disabled = 0
    for idx, batch in enumerate(batches, 1):
        print(f"\n--- Processing Batch {idx}/{len(batches)} ({len(batch)} packages) ---")
        for pkg in batch:
            orig = original_states.get(pkg, {}).get("original_state", "unknown")
            cmd_str = f"pm disable-user --user 0 {pkg}"

            if is_dry_run:
                print(f"  [DRY-RUN] Would execute: adb shell {cmd_str} (Original: {orig})")
                log_transaction("dry_run_disable", pkg, orig, "would_be_disabled", "SIMULATED", cmd_str)
                total_disabled += 1
            else:
                print(f"  [EXECUTING] adb shell {cmd_str} ...", end=" ", flush=True)
                stdout, stderr, code = run_adb(device_id, ["shell", "pm", "disable-user", "--user", "0", pkg])
                
                # Verify resulting state
                check_out, _, _ = run_adb(device_id, ["shell", "pm", "list", "packages", "-d"])
                is_disabled_now = f"package:{pkg}" in check_out

                if is_disabled_now:
                    print("SUCCESS (Disabled)")
                    log_transaction("disable_user", pkg, orig, "disabled", "SUCCESS", stdout)
                    total_disabled += 1
                else:
                    print(f"FAILED / REFUSED (Exit: {code}, Out: {stdout}, Err: {stderr})")
                    log_transaction("disable_user", pkg, orig, orig, "FAILED", f"code={code}, out={stdout}, err={stderr}")

        # Post-batch stability check
        if not is_dry_run:
            print("  [*] Verifying system stability after batch...")
            stable, reason = check_system_stability(device_id)
            if not stable:
                print(f"\n[CRITICAL ERROR] System instability detected: {reason}!")
                print("  [ROLLBACK] Rolling back recent batch immediately...")
                for pkg in batch:
                    orig = original_states.get(pkg, {}).get("original_state", "enabled")
                    if orig in ["enabled", "default"]:
                        run_adb(device_id, ["shell", "pm", "enable", "--user", "0", pkg])
                        log_transaction("emergency_rollback", pkg, "disabled", "restored", "RECOVERED")
                sys.exit(1)
            else:
                print("  [OK] System is healthy and responsive.")

    print("\n==============================================================")
    print(f"Debloat run completed. Total packages processed: {total_disabled}")
    if is_dry_run:
        print("Note: This was a DRY RUN. Pass --apply to execute changes live.")
    print("==============================================================")

if __name__ == "__main__":
    main()
