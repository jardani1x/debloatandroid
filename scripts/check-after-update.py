import json
import os
import sys
import subprocess

ADB_PATH = r"C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"

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
    return res.stdout.strip()

def main():
    print("==============================================================")
    print("CleanYourPhone — Post-Update Read-Only Audit")
    print("==============================================================")

    device_id = get_connected_device()
    if not device_id:
        print("[!] ERROR: No authorized device found via ADB.")
        sys.exit(1)

    # 1. Check firmware changes
    baseline_profile_path = os.path.join("reports", "device-profile.json")
    if os.path.exists(baseline_profile_path):
        with open(baseline_profile_path, "r", encoding="utf-8") as f:
            base_profile = json.load(f)
        current_build = run_adb(device_id, ["shell", "getprop", "ro.build.display.id"])
        current_patch = run_adb(device_id, ["shell", "getprop", "ro.build.version.security_patch"])
        
        base_build = base_profile.get("firmware_build", "Unknown")
        base_patch = base_profile.get("security_patch", "Unknown")

        print(f"[*] Firmware Baseline: {base_build} (Patch: {base_patch})")
        print(f"[*] Current Firmware:  {current_build} (Patch: {current_patch})")
        if current_build != base_build or current_patch != base_patch:
            print("  [!] FIRMWARE UPDATE DETECTED: Operating system has been updated!")
        else:
            print("  [OK] Firmware build matches baseline snapshot.")

    # 2. Check disabled packages
    baseline_states_path = os.path.join("backups", "original-package-states.json")
    balanced_profile_path = os.path.join("profiles", "balanced.json")

    if os.path.exists(balanced_profile_path):
        with open(balanced_profile_path, "r", encoding="utf-8") as f:
            intended_disabled = set(json.load(f).get("packages", []))
    else:
        intended_disabled = set()

    current_disabled_raw = run_adb(device_id, ["shell", "pm", "list", "packages", "-d"])
    current_disabled = set()
    for line in current_disabled_raw.splitlines():
        if line.startswith("package:"):
            current_disabled.add(line.split("package:", 1)[1].strip())

    re_enabled = intended_disabled - current_disabled
    if re_enabled:
        print(f"\n[!] Previously debloated packages that have been RE-ENABLED by OEM update ({len(re_enabled)}):")
        for pkg in sorted(re_enabled):
            print(f"  - {pkg}")
    else:
        print("\n[OK] All intended debloated packages remain in disabled state.")

    # 3. Check for newly installed packages
    if os.path.exists(baseline_states_path):
        with open(baseline_states_path, "r", encoding="utf-8") as f:
            old_packages = set(json.load(f).keys())
        
        current_packages_raw = run_adb(device_id, ["shell", "pm", "list", "packages"])
        current_all = set()
        for line in current_packages_raw.splitlines():
            if line.startswith("package:"):
                current_all.add(line.split("package:", 1)[1].strip())

        new_packages = current_all - old_packages
        if new_packages:
            print(f"\n[!] NEW packages installed since baseline ({len(new_packages)}):")
            for pkg in sorted(new_packages):
                print(f"  + {pkg}")
        else:
            print("\n[OK] No new unexpected manufacturer packages detected.")

    print("\n==============================================================")
    print("Post-update audit complete. Review changes before taking action.")
    print("Do NOT automatically apply old debloat lists to new firmware.")
    print("==============================================================")

if __name__ == "__main__":
    main()
