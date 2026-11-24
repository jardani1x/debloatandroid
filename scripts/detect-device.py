import subprocess
import json
import re
import os
import sys
import time

ADB_PATH = r"C:\Users\jun yi\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"

def get_connected_device():
    # Attempt connection or mDNS check
    subprocess.run([ADB_PATH, "connect", "192.168.31.20:33305"], capture_output=True, text=True, check=False)
    time.sleep(1)
    res = subprocess.run([ADB_PATH, "devices", "-l"], capture_output=True, text=True, check=False)
    lines = res.stdout.strip().splitlines()
    print("ADB Devices output:\n" + "\n".join(lines))
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    return None

def run_adb(device_id, args):
    cmd = [ADB_PATH, "-s", device_id] + args
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def parse_getprop(device_id):
    raw = run_adb(device_id, ["shell", "getprop"])
    props = {}
    for line in raw.splitlines():
        match = re.match(r"\[(.*?)\]:\s*\[(.*?)\]", line)
        if match:
            props[match.group(1)] = match.group(2)
    return props

def main():
    device_id = get_connected_device()
    if not device_id:
        print("ERROR: No authorized device found in 'adb devices'.")
        sys.exit(1)

    print(f"Using device ID: {device_id}")

    print("Querying build properties...")
    props = parse_getprop(device_id)

    print("Querying users...")
    users_raw = run_adb(device_id, ["shell", "pm", "list", "users"])

    print("Querying package lists...")
    packages_f = run_adb(device_id, ["shell", "pm", "list", "packages", "-f"]).splitlines()
    packages_s = run_adb(device_id, ["shell", "pm", "list", "packages", "-s"]).splitlines()
    packages_3 = run_adb(device_id, ["shell", "pm", "list", "packages", "-3"]).splitlines()
    packages_d = run_adb(device_id, ["shell", "pm", "list", "packages", "-d"]).splitlines()

    print("Querying memory, battery, cpu, storage, and webview...")
    meminfo_raw = run_adb(device_id, ["shell", "dumpsys", "meminfo"])
    battery_raw = run_adb(device_id, ["shell", "dumpsys", "battery"])
    cpuinfo_raw = run_adb(device_id, ["shell", "dumpsys", "cpuinfo"])
    df_raw = run_adb(device_id, ["shell", "df", "-h", "/data"])
    webview_raw = run_adb(device_id, ["shell", "dumpsys", "webviewupdate"])

    print("Querying default applications...")
    launcher_raw = run_adb(device_id, ["shell", "cmd", "shortcut", "get-default-launcher"])
    if not launcher_raw or "ERROR" in launcher_raw or "No default" in launcher_raw:
        launcher_raw = run_adb(device_id, ["shell", "pm", "resolve-activity", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME"])
    
    keyboard_raw = run_adb(device_id, ["shell", "settings", "get", "secure", "default_input_method"])
    dialer_raw = run_adb(device_id, ["shell", "telecom", "get-default-dialer"])
    sms_raw = run_adb(device_id, ["shell", "settings", "get", "secure", "sms_default_application"])

    # Parse RAM
    total_ram = "Unknown"
    free_ram = "Unknown"
    for line in meminfo_raw.splitlines():
        if "Total RAM:" in line:
            total_ram = line.split("Total RAM:")[1].strip()
        if "Free RAM:" in line:
            free_ram = line.split("Free RAM:")[1].strip()

    # Parse Storage
    storage_total = "Unknown"
    storage_avail = "Unknown"
    for line in df_raw.splitlines():
        if "/data" in line:
            parts = line.split()
            if len(parts) >= 5:
                storage_total = parts[1]
                storage_avail = parts[3]

    # Parse Battery
    battery_status = {}
    for line in battery_raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            battery_status[k.strip()] = v.strip()

    # Parse Users to verify User 0
    active_user = "Unknown"
    for line in users_raw.splitlines():
        if "UserInfo{" in line:
            active_user = line.strip()

    # OEM OS detection
    oem_os = "AOSP / Stock-like"
    if props.get("ro.mi.os.version.name") or props.get("ro.miui.ui.version.name"):
        oem_os = f"Xiaomi HyperOS / MIUI ({props.get('ro.mi.os.version.name') or props.get('ro.miui.ui.version.name')})"
    elif props.get("ro.build.version.oneui"):
        oem_os = f"Samsung One UI ({props.get('ro.build.version.oneui')})"
    elif props.get("ro.build.version.opporom") or props.get("ro.build.version.oplusrom"):
        oem_os = f"ColorOS / OxygenOS ({props.get('ro.build.version.opporom') or props.get('ro.build.version.oplusrom')})"
    elif props.get("ro.vivo.os.build.display.id"):
        oem_os = f"Vivo Funtouch / OriginOS ({props.get('ro.vivo.os.build.display.id')})"
    elif props.get("ro.build.version.emui"):
        oem_os = f"Huawei EMUI ({props.get('ro.build.version.emui')})"
    elif "pixel" in props.get("ro.product.brand", "").lower():
        oem_os = "Google Pixel Android"
    elif props.get("ro.product.manufacturer"):
        oem_os = f"OEM: {props.get('ro.product.manufacturer')}"

    profile = {
        "device_id": device_id,
        "manufacturer": props.get("ro.product.manufacturer", "Unknown"),
        "brand": props.get("ro.product.brand", "Unknown"),
        "model": props.get("ro.product.model", "Unknown"),
        "codename": props.get("ro.product.device", "Unknown"),
        "android_version": props.get("ro.build.version.release", "Unknown"),
        "sdk_level": props.get("ro.build.version.sdk", "Unknown"),
        "firmware_build": props.get("ro.build.display.id", props.get("ro.build.id", "Unknown")),
        "security_patch": props.get("ro.build.version.security_patch", "Unknown"),
        "oem_os": oem_os,
        "cpu_arch": props.get("ro.product.cpu.abi", "Unknown"),
        "total_ram": total_ram,
        "available_ram": free_ram,
        "internal_storage_total": storage_total,
        "internal_storage_available": storage_avail,
        "battery": {
            "level": battery_status.get("level", "Unknown"),
            "scale": battery_status.get("scale", "Unknown"),
            "status": battery_status.get("status", "Unknown"),
            "health": battery_status.get("health", "Unknown"),
            "temperature": battery_status.get("temperature", "Unknown"),
            "technology": battery_status.get("technology", "Unknown")
        },
        "active_user": active_user,
        "default_apps": {
            "launcher": launcher_raw,
            "keyboard": keyboard_raw,
            "dialer": dialer_raw,
            "sms": sms_raw,
            "webview": webview_raw.splitlines()[0] if webview_raw else "Unknown"
        },
        "package_counts": {
            "total": len(packages_f),
            "system": len(packages_s),
            "third_party": len(packages_3),
            "disabled": len(packages_d)
        }
    }

    os.makedirs("reports", exist_ok=True)
    with open("reports/device-profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    os.makedirs("backups/raw", exist_ok=True)
    with open("backups/raw/getprop.txt", "w", encoding="utf-8") as f:
        for k, v in sorted(props.items()):
            f.write(f"[{k}]: [{v}]\n")
    with open("backups/raw/packages_f.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(packages_f))
    with open("backups/raw/packages_s.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(packages_s))
    with open("backups/raw/packages_3.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(packages_3))
    with open("backups/raw/packages_d.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(packages_d))
    with open("backups/raw/meminfo.txt", "w", encoding="utf-8") as f:
        f.write(meminfo_raw)
    with open("backups/raw/battery.txt", "w", encoding="utf-8") as f:
        f.write(battery_raw)
    with open("backups/raw/cpuinfo.txt", "w", encoding="utf-8") as f:
        f.write(cpuinfo_raw)
    with open("backups/raw/webview.txt", "w", encoding="utf-8") as f:
        f.write(webview_raw)

    print("\n================ DEVICE RECONNAISSANCE SUMMARY ================")
    print(f"Device Identifier:   {profile['device_id']}")
    print(f"Manufacturer:        {profile['manufacturer']}")
    print(f"Brand:               {profile['brand']}")
    print(f"Model:               {profile['model']} (Codename: {profile['codename']})")
    print(f"Android Version:     {profile['android_version']} (SDK {profile['sdk_level']})")
    print(f"Firmware Build:      {profile['firmware_build']}")
    print(f"Security Patch:      {profile['security_patch']}")
    print(f"OEM OS / Flavor:     {profile['oem_os']}")
    print(f"CPU Architecture:    {profile['cpu_arch']}")
    print(f"Total RAM:           {profile['total_ram']}")
    print(f"Free / Avail RAM:    {profile['available_ram']}")
    print(f"Internal Storage:    {profile['internal_storage_total']} Total, {profile['internal_storage_available']} Available")
    print(f"Battery:             {profile['battery']['level']}% (Status: {profile['battery']['status']}, Health: {profile['battery']['health']})")
    print(f"Active User:         {profile['active_user']}")
    print(f"Default Launcher:    {profile['default_apps']['launcher']}")
    print(f"Default Keyboard:    {profile['default_apps']['keyboard']}")
    print(f"Default Phone:       {profile['default_apps']['dialer']}")
    print(f"Default Messaging:   {profile['default_apps']['sms']}")
    print(f"WebView Provider:    {profile['default_apps']['webview']}")
    print(f"Package Counts:      Total: {profile['package_counts']['total']} | System: {profile['package_counts']['system']} | Third-Party: {profile['package_counts']['third_party']} | Disabled: {profile['package_counts']['disabled']}")
    print("================================================================")

if __name__ == "__main__":
    main()
