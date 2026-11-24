# CleanYourPhone — Debloat & Audit Plan

## 1. Executive Summary & Device Context
- **Device Model:** Oyster_Labs UBS1 (`Universal_Phone_1`)
- **Platform:** Unisoc (Spreadtrum) T616 Octa-Core (`ums9230`)
- **Android Version:** Android 14 (API 34, Security Patch 2024-09-05)
- **Target User:** Primary User 0 (`UserInfo{0:Owner:4c13}`)
- **Total Packages:** 347 (253 System / 94 User-Installed)
- **User Preference Alignment:** 
  - Retain: Telephony, SMS, Data/Hotspot, Wi-Fi/BT, Play Store/Services, WhatsApp, Telegram, Banking/Auth, NFC & Wallet, GPS, Camera/Gallery, Biometrics, Pokémon GO, Google Assistant, Security Updates.
  - Disable: #14 (Manufacturer Cloud / Telemetry), #16 (Android Auto), #18 (Manufacturer Ecosystem / ODM Demo Apps).

---

## 2. Backup & Recovery Readiness
A full pre-modification state capture was executed under `backups/backup_20261124_131253/`:
- **Package Inventory:** Complete paths, permissions, and initial enabled states recorded in `original-package-states.json`.
- **System Settings:** Exported `global`, `system`, and `secure` tables.
- **Performance Baseline:** RAM, CPU, Battery, and process table snapshots recorded.
- **Rollback Tooling Generated:**
  - `scripts/restore-all.ps1` & `scripts/restore-all.sh`
  - `scripts/restore-package.ps1` & `scripts/restore-package.sh`
  - `scripts/restore.py`
  - `logs/transactions.jsonl` (Persistent transaction journal)

> [!WARNING]
> Package inventories and state snapshots do not backup personal photos, chat histories, or private encryption keys. Ensure critical personal files are backed up separately before executing modifications.

---

## 3. Profiles Overview

### Conservative Profile (16 Packages)
Targets only non-functional, obsolete ODM preloads, factory tests, live wallpaper bloat, and unused bookmark injectors. Zero risk of functional impairment.

### Balanced Profile (32 Packages) — **RECOMMENDED**
Includes all Conservative items PLUS:
- Android Auto (`com.google.android.projection.gearhead`) per user instruction #16.
- Chipset background telemetry and diagnostic logging daemons (`com.sprd.logmanager`, `com.sprd.engineermode`, `com.google.mainline.telemetry`, `com.android.traceur`) per user instruction #14.
- Advertising tracking and Privacy Sandbox telemetry (`com.google.android.adservices.api`, `com.google.mainline.adservices`, `com.google.android.ondevicepersonalization.services`).
- Orphaned or redundant media preloads (`com.google.android.videos`, `com.google.android.apps.youtube.music`, `com.google.android.apps.tachyon`, `com.mediatek.batterywarning`, `com.android.pedometer`).

### Aggressive Profile (40 Packages)
Includes Balanced items PLUS optional Google Drive, Digital Wellbeing, Carrier Wi-Fi, Link Turbo, and AOSP Sound Recorder.

---

## 4. Balanced Profile Package Audit Table (32 Packages)

| Package ID | App Name | Purpose | Category | Risk Level | Confidence | Dependencies | Recommendation | Potential Side Effects | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `com.hxywizard` | HXY Setup Wizard | Initial ODM setup wizard | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | None; initial setup already finished | Post-setup redundant APK |
| `com.hxy.hxylivewallpaperone` | HXY Live Wallpaper 1 | Animated live wallpaper | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | Loss of ODM live wallpaper 1 | Unnecessary visual asset |
| `com.hxy.hxylivewallpapertwo` | HXY Live Wallpaper 2 | Animated live wallpaper | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | Loss of ODM live wallpaper 2 | Unnecessary visual asset |
| `com.hxy.hxylivewallpaperthree` | HXY Live Wallpaper 3 | Animated live wallpaper | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | Loss of ODM live wallpaper 3 | Unnecessary visual asset |
| `com.yft.miniscreen` | YFT Mini Screen | ODM secondary screen demo | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | None on single-display phone | Redundant ODM package |
| `com.spk.universal` | Universal Phone Assistant | OEM ecosystem promotional app | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | Stops OEM promotional alerts | Oyster Labs OEM bundle |
| `com.teksun.factorytest` | Teksun Factory Test | Factory assembly hardware test | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | Diagnostic menu inaccessible | Assembly line tool |
| `com.sprd.validationtools` | Validation Tools | Unisoc factory hardware validation | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | Hardware diagnostic tool disabled | Unisoc BSP validator |
| `com.sprd.camta` | Camera Test Agent | Spreadtrum camera test harness | Manufacturer promotional applications | SAFE | HIGH | None | DISABLE | None; stock Camera unaffected | Internal test agent |
| `com.android.egg` | Android Easter Egg | OS Easter Egg minigame | Preinstalled third-party applications | SAFE | HIGH | None | DISABLE | Easter egg menu disabled | AOSP Easter egg |
| `com.android.dreams.phototable` | Photo Table Screensaver | Legacy daydream photo screensaver | Unnecessary background services | SAFE | HIGH | None | DISABLE | Photo screensaver disabled | UAD-NG Recommended |
| `com.android.dreams.basic` | Basic Screensaver | Color daydream screensaver | Unnecessary background services | SAFE | HIGH | None | DISABLE | Color screensaver disabled | UAD-NG Recommended |
| `com.android.bookmarkprovider` | Bookmark Provider | Stock browser bookmark sync | Unnecessary background services | SAFE | HIGH | None | DISABLE | None (modern browsers use own sync) | UAD-NG Recommended |
| `com.android.providers.partnerbookmarks` | Partner Bookmarks | Partner promotional bookmark injector | Advertising and recommendation services | SAFE | HIGH | None | DISABLE | Prevents partner bookmark ads | UAD-NG Recommended |
| `com.google.android.printservice.recommendation` | Print Recommendation | Automatic print plugin recommender | Advertising and recommendation services | SAFE | HIGH | None | DISABLE | No print plugin suggestions | UAD-NG Recommended |
| `com.android.bips` | Built-in Print Service | Mopria print service | Unnecessary background services | SAFE | HIGH | None | DISABLE | Cannot print to local Wi-Fi printer | UAD-NG Recommended |
| `com.google.android.projection.gearhead` | Android Auto | In-car screen projection client | Optional Google applications | SAFE | HIGH | None | DISABLE | Android Auto will not project | User selected disable #16 |
| `com.sprd.logmanager` | Spreadtrum Log Manager | Background debug log recorder | Telemetry and analytics | SAFE | HIGH | None | DISABLE | Stops continuous debug logging | User selected disable #14 |
| `com.sprd.engineermode` | Spreadtrum Engineer Mode | Engineering diagnostic menu | Telemetry and analytics | SAFE | HIGH | None | DISABLE | Secret diagnostic dialer codes disabled | User selected disable #14 |
| `com.google.android.feedback` | Google Feedback | Voluntary crash feedback uploader | Telemetry and analytics | SAFE | HIGH | None | DISABLE | Cannot upload feedback to Google | UAD-NG Recommended |
| `com.google.mainline.telemetry` | Mainline Telemetry | Google modular telemetry collector | Telemetry and analytics | SAFE | HIGH | None | DISABLE | Reduces background telemetry | Android Mainline APEX |
| `com.google.android.adservices.api` | Ad Services API | Privacy Sandbox cross-app ads API | Advertising and recommendation services | SAFE | HIGH | None | DISABLE | Blocks on-device ad profiling | Android 14 Ad Framework |
| `com.google.mainline.adservices` | Mainline Ad Services | Modular ad services daemon | Advertising and recommendation services | SAFE | HIGH | None | DISABLE | Blocks modular ad framework | Android 14 Ad Framework |
| `com.google.android.ondevicepersonalization.services` | On-Device Personalization | Behavioral personalization profiler | Advertising and recommendation services | SAFE | HIGH | None | DISABLE | Reduces background ad profiling | Android 14 Personalization |
| `com.google.android.videos` | Google TV | Google TV / Play Movies store | Optional Google applications | SAFE | HIGH | None | DISABLE | Google TV app disabled | UAD-NG Recommended |
| `com.google.android.apps.youtube.music` | YouTube Music (Preload) | Stock YouTube Music client | Optional Google applications | SAFE | HIGH | None | DISABLE | Stock app disabled (user has ReVanced) | Duplicate application |
| `com.google.android.apps.tachyon` | Google Meet | Standalone Meet video calls | Optional Google applications | SAFE | HIGH | None | DISABLE | Standalone Meet app disabled | UAD-NG Recommended |
| `com.mediatek.batterywarning` | MediaTek Battery Warning | Orphaned battery warning stub | Unnecessary background services | SAFE | HIGH | None | DISABLE | None (phone runs Unisoc chip) | Orphaned build artifact |
| `com.android.traceur` | System Tracing | Performance trace logger | Telemetry and analytics | SAFE | HIGH | None | DISABLE | Quick Setting tracing tile disabled | AOSP Developer Tool |
| `com.android.pedometer` | Stock Pedometer | Background step counter service | Unnecessary background services | SAFE | HIGH | None | DISABLE | Disables stock pedometer polling | Redundant sensor poller |
| `com.android.smspush` | WAP Push Service | Legacy WAP push handler | Unnecessary background services | SAFE | HIGH | None | DISABLE | Disables legacy WAP push; SMS fine | UAD-NG Recommended |
| `com.sprd.omacp` | OMA Client Provisioning | Legacy carrier configuration push | Unnecessary background services | SAFE | HIGH | None | DISABLE | Disables legacy carrier push vector | Legacy carrier vulnerability |
