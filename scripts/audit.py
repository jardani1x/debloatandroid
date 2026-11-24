import json
import csv
import os
import sys

def main():
    print("[*] Loading package inventory and UAD-NG database...")
    with open("backups/original-package-states.json", "r", encoding="utf-8") as f:
        states = json.load(f)

    with open("configs/uad_lists.json", "r", encoding="utf-8") as f:
        uad = json.load(f)

    # Core system & user apps that must NEVER be disabled
    EXPLICITLY_PROTECTED = {
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
        "com.google.android.inputmethod.latin",  # Default keyboard (Gboard)
        "com.android.launcher3",                # Default launcher
        "com.google.android.dialer",            # Default dialer
        "com.google.android.apps.messaging",    # Messaging
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
        # User apps retained by explicit preference
        "com.nianticlabs.pokemongo",
        "com.whatsapp",
        "org.telegram.messenger",
        "com.tailscale.ipn",
        "com.azure.authenticator",
        "proton.android.pass",
        "ch.protonvpn.android",
        "io.metamask",
        "com.ton_keeper",
        "com.bitkeep.wallet",
        "money.moonshot.app",
        "com.dexscreener",
        "com.tradingview.tradingviewapp",
        "com.spotify.music",
        "com.termux",
        "com.termux.x11",
        "com.openai.chatgpt",
        "ai.x.grok",
        "com.grabtaxi.passenger",
        "com.global.foodpanda.android",
        "com.shopee.sg",
        "com.lazada.android",
        "com.shopback.app",
        "com.sia.krispay.customer",
        "sg.gov.imda.wsgapp2_android",
        "sg.gov.mnd.OneService",
        "sg.mediacorp.android",
        "com.axs",
        "com.google.android.apps.maps",
        "com.google.android.apps.photos",
        "com.google.android.calendar",
        "com.google.android.gm",
        "com.android.chrome"
    }

    # 1. Conservative candidates (promotional, test, and unused ODM apps)
    CONSERVATIVE_CANDIDATES = {
        "com.hxywizard": {
            "app_name": "HXY Setup Wizard",
            "purpose": "ODM initial setup wizard",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "None; setup is already complete",
            "evidence": "ODM post-setup redundant wizard"
        },
        "com.hxy.hxylivewallpaperone": {
            "app_name": "HXY Live Wallpaper 1",
            "purpose": "Preinstalled ODM live wallpaper",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "Removal of animated ODM wallpaper option",
            "evidence": "Unnecessary ODM graphical asset"
        },
        "com.hxy.hxylivewallpapertwo": {
            "app_name": "HXY Live Wallpaper 2",
            "purpose": "Preinstalled ODM live wallpaper",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "Removal of animated ODM wallpaper option",
            "evidence": "Unnecessary ODM graphical asset"
        },
        "com.hxy.hxylivewallpaperthree": {
            "app_name": "HXY Live Wallpaper 3",
            "purpose": "Preinstalled ODM live wallpaper",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "Removal of animated ODM wallpaper option",
            "evidence": "Unnecessary ODM graphical asset"
        },
        "com.yft.miniscreen": {
            "app_name": "YFT Mini Screen",
            "purpose": "ODM secondary screen / demo background service",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "None on standard single-screen devices",
            "evidence": "ODM demo background package"
        },
        "com.spk.universal": {
            "app_name": "Universal Phone Assistant",
            "purpose": "ODM promotional ecosystem package",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "Disables OEM promotional notifications",
            "evidence": "Oyster Labs OEM promotional bundle"
        },
        "com.teksun.factorytest": {
            "app_name": "Teksun Factory Test",
            "purpose": "Factory hardware testing diagnostic app",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "Disables factory test menu (not used in daily operation)",
            "evidence": "Factory production line test tool"
        },
        "com.sprd.validationtools": {
            "app_name": "Spreadtrum Validation Tools",
            "purpose": "Chipset factory validation testing",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "Disables Unisoc hardware factory validator",
            "evidence": "Unisoc BSP test tool"
        },
        "com.sprd.camta": {
            "app_name": "Camera Test Agent",
            "purpose": "Spreadtrum camera test agent",
            "category": "Manufacturer promotional applications",
            "risk": "SAFE",
            "side_effects": "None; standard Camera app is unaffected",
            "evidence": "Internal camera test harness"
        },
        "com.android.egg": {
            "app_name": "Android Easter Egg",
            "purpose": "Hidden OS Easter egg game",
            "category": "Preinstalled third-party applications",
            "risk": "SAFE",
            "side_effects": "Loss of easter egg in About Phone",
            "evidence": "AOSP easter egg component"
        },
        "com.android.dreams.phototable": {
            "app_name": "Photo Table Screensaver",
            "purpose": "Legacy daydream photo table screensaver",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "Loss of legacy photo screensaver",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.android.dreams.basic": {
            "app_name": "Basic Screensaver",
            "purpose": "Color screensaver",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "Loss of color daydream screensaver",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.android.bookmarkprovider": {
            "app_name": "Bookmark Provider",
            "purpose": "AOSP stock browser bookmark sync",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "None (modern browsers use own sync)",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.android.providers.partnerbookmarks": {
            "app_name": "Partner Bookmarks",
            "purpose": "OEM partner promotional bookmarks",
            "category": "Advertising and recommendation services",
            "risk": "SAFE",
            "side_effects": "Prevents injection of partner bookmarks",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.google.android.printservice.recommendation": {
            "app_name": "Print Service Recommendation",
            "purpose": "Recommends third-party print plugins",
            "category": "Advertising and recommendation services",
            "risk": "SAFE",
            "side_effects": "No automatic print plugin suggestions",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.android.bips": {
            "app_name": "Built-in Print Service",
            "purpose": "Default mopria print spooler driver",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "Cannot print directly to local network printers",
            "evidence": "UAD-NG: Recommended removal"
        }
    }

    # 2. Balanced additions (User requested 14, 16, 18 + Telemetry & Privacy Sandbox)
    BALANCED_ADDITIONS = {
        "com.google.android.projection.gearhead": {
            "app_name": "Android Auto",
            "purpose": "In-car display integration companion app",
            "category": "Optional Google applications",
            "risk": "SAFE",
            "side_effects": "In-car Android Auto projection will not launch (Requested by user #16)",
            "evidence": "User preference & UAD-NG removal"
        },
        "com.sprd.logmanager": {
            "app_name": "Spreadtrum Log Manager",
            "purpose": "Chipset background debug log collection daemon",
            "category": "Telemetry and analytics",
            "risk": "SAFE",
            "side_effects": "Stops continuous background logging; frees CPU and RAM (Requested #14)",
            "evidence": "Unisoc BSP telemetry service"
        },
        "com.sprd.engineermode": {
            "app_name": "Spreadtrum Engineer Mode",
            "purpose": "Diagnostic and hardware debugging interface",
            "category": "Telemetry and analytics",
            "risk": "SAFE",
            "side_effects": "Engineer mode secret codes will not open",
            "evidence": "Unisoc BSP diagnostic tool"
        },
        "com.google.android.feedback": {
            "app_name": "Google Feedback",
            "purpose": "Crash report and feedback uploader",
            "category": "Telemetry and analytics",
            "risk": "SAFE",
            "side_effects": "Cannot submit voluntary bug reports to Google",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.google.mainline.telemetry": {
            "app_name": "Mainline Telemetry",
            "purpose": "Google Mainline background telemetry collector",
            "category": "Telemetry and analytics",
            "risk": "SAFE",
            "side_effects": "Reduces background telemetry upload to Google",
            "evidence": "Android Mainline modular telemetry"
        },
        "com.google.android.adservices.api": {
            "app_name": "Android Ad Services API",
            "purpose": "Privacy Sandbox cross-app ad measurement and targeting",
            "category": "Advertising and recommendation services",
            "risk": "SAFE",
            "side_effects": "Blocks on-device advertising topics and measurement",
            "evidence": "Android 14 Privacy Sandbox ad framework"
        },
        "com.google.mainline.adservices": {
            "app_name": "Mainline Ad Services",
            "purpose": "Mainline Ad Services module",
            "category": "Advertising and recommendation services",
            "risk": "SAFE",
            "side_effects": "Blocks modular ad delivery framework",
            "evidence": "Android 14 AdServices module"
        },
        "com.google.android.ondevicepersonalization.services": {
            "app_name": "On-Device Personalization",
            "purpose": "Ad targeting and behavioral personalization",
            "category": "Advertising and recommendation services",
            "risk": "SAFE",
            "side_effects": "Disables background personalization profiling",
            "evidence": "Android 14 OnDevicePersonalization service"
        },
        "com.google.android.videos": {
            "app_name": "Google TV",
            "purpose": "Google TV / Google Play Movies store and player",
            "category": "Optional Google applications",
            "risk": "SAFE",
            "side_effects": "Loss of Google TV app (content still playable via web)",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.google.android.apps.youtube.music": {
            "app_name": "YouTube Music (Stock Preload)",
            "purpose": "Official YouTube Music system preload",
            "category": "Optional Google applications",
            "risk": "SAFE",
            "side_effects": "Stock app disabled; user has ReVanced YouTube Music",
            "evidence": "Redundant duplicate application"
        },
        "com.google.android.apps.tachyon": {
            "app_name": "Google Meet",
            "purpose": "Google video calling application",
            "category": "Optional Google applications",
            "risk": "SAFE",
            "side_effects": "Loss of standalone Meet video call app",
            "evidence": "UAD-NG: Recommended removal"
        },
        "com.mediatek.batterywarning": {
            "app_name": "MediaTek Battery Warning",
            "purpose": "Unused leftover MediaTek battery notification stub",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "None (device uses Unisoc hardware)",
            "evidence": "Orphaned OEM package"
        },
        "com.android.traceur": {
            "app_name": "System Tracing (Traceur)",
            "purpose": "Developer system performance trace logger",
            "category": "Telemetry and analytics",
            "risk": "SAFE",
            "side_effects": "Quick setting tile for developer tracing disabled",
            "evidence": "AOSP debugging tool"
        },
        "com.android.pedometer": {
            "app_name": "Stock Pedometer",
            "purpose": "AOSP step tracking service",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "Disables stock pedometer service",
            "evidence": "Unused background sensor poller"
        },
        "com.android.smspush": {
            "app_name": "WAP Push Service",
            "purpose": "Legacy 2G/3G WAP push message service",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "Loss of legacy WAP push; normal SMS unaffected",
            "evidence": "UAD-NG: Recommended removal (legacy vulnerability surface)"
        },
        "com.sprd.omacp": {
            "app_name": "OMA Client Provisioning",
            "purpose": "Legacy OMA carrier configuration push receiver",
            "category": "Unnecessary background services",
            "risk": "SAFE",
            "side_effects": "Carrier APNs configured via modern CarrierConfig; legacy push disabled",
            "evidence": "Legacy carrier push vector"
        }
    }

    # 3. Aggressive additions
    AGGRESSIVE_ADDITIONS = {
        "com.google.android.apps.docs": {
            "app_name": "Google Drive",
            "purpose": "Google Drive cloud storage",
            "category": "Optional Google applications",
            "risk": "CONDITIONAL",
            "side_effects": "Drive file sync disabled (web interface still accessible)",
            "evidence": "UAD-NG: Advanced"
        },
        "com.google.android.apps.wellbeing": {
            "app_name": "Digital Wellbeing",
            "purpose": "Screen time and app usage monitor",
            "category": "Optional Google applications",
            "risk": "CONDITIONAL",
            "side_effects": "Screen time tracking and bedtime mode disabled",
            "evidence": "UAD-NG: Advanced"
        },
        "com.google.android.apps.carrier.carrierwifi": {
            "app_name": "Carrier Wi-Fi",
            "purpose": "Automatic connection to partner carrier Wi-Fi networks",
            "category": "Optional Google applications",
            "risk": "CONDITIONAL",
            "side_effects": "Manual Wi-Fi selection only",
            "evidence": "UAD-NG: Recommended"
        },
        "com.sprd.linkturbo": {
            "app_name": "Spreadtrum Link Turbo",
            "purpose": "Concurrent Wi-Fi + Cellular acceleration service",
            "category": "Optional manufacturer features",
            "risk": "CONDITIONAL",
            "side_effects": "Standard single-network routing only",
            "evidence": "Unisoc network bonding daemon"
        },
        "com.google.android.tag": {
            "app_name": "NFC Tags",
            "purpose": "Reading passive NFC tags/posters",
            "category": "Optional Google applications",
            "risk": "CONDITIONAL",
            "side_effects": "Cannot read physical NFC tag stickers (Google Wallet payment unaffected)",
            "evidence": "UAD-NG: Recommended"
        },
        "com.android.soundrecorder": {
            "app_name": "Sound Recorder",
            "purpose": "Stock voice audio recorder",
            "category": "Optional manufacturer features",
            "risk": "CONDITIONAL",
            "side_effects": "Loss of stock voice recorder app",
            "evidence": "AOSP voice recorder"
        },
        "com.android.musicfx": {
            "app_name": "MusicFX",
            "purpose": "Audio equalizer effect interface",
            "category": "Optional manufacturer features",
            "risk": "CONDITIONAL",
            "side_effects": "Equalizer panel in media players will be disabled",
            "evidence": "AOSP audio effects processor"
        },
        "com.android.wallpaper.livepicker": {
            "app_name": "Live Wallpaper Picker",
            "purpose": "System selector for live wallpapers",
            "category": "Optional manufacturer features",
            "risk": "CONDITIONAL",
            "side_effects": "Cannot choose live wallpapers in wallpaper settings",
            "evidence": "UAD-NG: Recommended"
        }
    }

    conservative_set = set(CONSERVATIVE_CANDIDATES.keys())
    balanced_set = conservative_set.union(set(BALANCED_ADDITIONS.keys()))
    aggressive_set = balanced_set.union(set(AGGRESSIVE_ADDITIONS.keys()))

    audit_results = []
    for pkg, info in states.items():
        is_system = info["is_system"]
        u_info = uad.get(pkg, {})

        if pkg in EXPLICITLY_PROTECTED or any(pkg.startswith(p) for p in ["android.unisoc.", "android.overlay.", "com.unisoc.android."]) or pkg.endswith(".overlay"):
            app_name = pkg.split(".")[-1].replace("_", " ").title()
            purpose = u_info.get("description", "Core system framework / Protected user component").replace("\n", " ").strip()
            category = "Essential system components" if is_system else "User Installed Application"
            risk = "PROTECTED"
            confidence = "HIGH"
            rec = "RETAIN"
            side_effects = "Essential for device stability, user preference, or system operation"
            evidence = "Phase 7 Critical Protection List & User Preferences"
        elif pkg in CONSERVATIVE_CANDIDATES:
            meta = CONSERVATIVE_CANDIDATES[pkg]
            app_name = meta["app_name"]
            purpose = meta["purpose"]
            category = meta["category"]
            risk = meta["risk"]
            confidence = "HIGH"
            rec = "DISABLE (Conservative, Balanced, Aggressive)"
            side_effects = meta["side_effects"]
            evidence = meta["evidence"]
        elif pkg in BALANCED_ADDITIONS:
            meta = BALANCED_ADDITIONS[pkg]
            app_name = meta["app_name"]
            purpose = meta["purpose"]
            category = meta["category"]
            risk = meta["risk"]
            confidence = "HIGH"
            rec = "DISABLE (Balanced, Aggressive)"
            side_effects = meta["side_effects"]
            evidence = meta["evidence"]
        elif pkg in AGGRESSIVE_ADDITIONS:
            meta = AGGRESSIVE_ADDITIONS[pkg]
            app_name = meta["app_name"]
            purpose = meta["purpose"]
            category = meta["category"]
            risk = meta["risk"]
            confidence = "MEDIUM"
            rec = "DISABLE (Aggressive only)"
            side_effects = meta["side_effects"]
            evidence = meta["evidence"]
        else:
            app_name = pkg.split(".")[-1].replace("_", " ").title()
            purpose = u_info.get("description", "System package / Unverified integration").replace("\n", " ").strip()
            category = "Essential system components" if is_system else "Unknown packages"
            risk = "PROTECTED"
            confidence = "HIGH"
            rec = "RETAIN"
            side_effects = "Retained to guarantee stability (insufficient justification to disable)"
            evidence = "Phase 1 Safety Rule: Do not disable unknown or unverified packages"

        deps = ", ".join(u_info.get("dependencies", [])) or "None identified"

        audit_results.append({
            "Package ID": pkg,
            "App name": app_name,
            "Purpose": purpose,
            "Category": category,
            "Risk level": risk,
            "Confidence": confidence,
            "Dependencies": deps,
            "Recommendation": rec,
            "Potential side effects": side_effects,
            "Evidence": evidence
        })

    # Save CSV
    os.makedirs("reports", exist_ok=True)
    with open("reports/package-audit.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Package ID", "App name", "Purpose", "Category", "Risk level",
            "Confidence", "Dependencies", "Recommendation", "Potential side effects", "Evidence"
        ])
        writer.writeheader()
        writer.writerows(audit_results)

    # Save profiles
    os.makedirs("profiles", exist_ok=True)
    with open("profiles/conservative.json", "w", encoding="utf-8") as f:
        json.dump({"name": "conservative", "count": len(conservative_set), "packages": sorted(list(conservative_set))}, f, indent=2)

    with open("profiles/balanced.json", "w", encoding="utf-8") as f:
        json.dump({"name": "balanced", "count": len(balanced_set), "packages": sorted(list(balanced_set))}, f, indent=2)

    with open("profiles/aggressive.json", "w", encoding="utf-8") as f:
        json.dump({"name": "aggressive", "count": len(aggressive_set), "packages": sorted(list(aggressive_set))}, f, indent=2)

    print("\n[+] Audit completed successfully!")
    print(f"Total packages analyzed:         {len(audit_results)}")
    print(f"Conservative profile candidate count: {len(conservative_set)}")
    print(f"Balanced profile candidate count:     {len(balanced_set)}")
    print(f"Aggressive profile candidate count:   {len(aggressive_set)}")

if __name__ == "__main__":
    main()
