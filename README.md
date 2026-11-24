# CleanYourPhone (debloatandroid)

A safety-first, reversible Android debloating and system optimization framework tailored for modern Android smartphones.

Adapted from [CleanYourTV](https://github.com/Gathin23/cleanyourtv) and informed by the [Universal Android Debloater Next Generation (UAD-NG)](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation) database.

---

## Architecture & Principles

1. **Non-Destructive Debloating:** Uses `pm disable-user --user 0 <PACKAGE>` exclusively. No packages are uninstalled (`pm uninstall`), preserving original APKs in system partitions and ensuring 100% reversible operations.
2. **Zero Root / Zero Bootloader Modification:** Operates within official Android Debug Bridge (ADB) user permissions without tripping SafetyNet, Play Integrity, or Knox.
3. **Target Primary User Only:** All actions explicitly target Android User `0`, leaving work profiles and secondary spaces untouched.
4. **Independent Dynamic Protection:** Explicitly protects SystemUI, Telephony/IMS/VoLTE, Biometrics, Package Installers, Default Keyboards/Launchers, Google Play Services, and hardware HAL overlays (`ums9230`/Unisoc BSP).
5. **Audited Rollback Mechanism:** Every action is journaled to `logs/transactions.jsonl`. Complete baseline states are serialized in `backups/original-package-states.json`.

---

## Directory Structure

```text
CleanYourPhone/
    README.md                              # Project documentation & operational guidelines
    AGENTS.md                              # Subagent and autonomous system operational roles
    backups/                               # Timestamped system snapshots & baseline metrics
        original-package-states.json       # Exact original state of all 347 packages
        backup_YYYYMMDD_HHMMSS/            # Full backup snapshots (getprop, settings, baseline dumps)
    profiles/                              # Reviewable debloating profiles
        conservative.json                  # 16 Packages (Factory tests, ODM live wallpapers, bookmark injectors)
        balanced.json                      # 32 Packages (Recommended - Telemetry, AdServices, Android Auto, OEM bloat)
        aggressive.json                    # 40 Packages (Optional Google & OEM convenience features)
    reports/                               # Generated inspection & verification reports
        device-profile.json                # Complete hardware and firmware fingerprint
        package-audit.csv                  # Complete 347-package audit spreadsheet
        debloat-report.md                  # Detailed classification, rationale & evidence
        performance-comparison.md          # Before-and-after performance metrics
        verification-results.md            # Subsystem pass/fail verification table
    scripts/                               # Portable automation scripts
        detect-device.py                   # Automated hardware, OS & package reconnaissance
        audit.py                           # Cross-references inventory against UAD-NG & protection rules
        debloat.py                         # Batch executor with dry-run, verification & rollback
        restore.py                         # Single, batch, and full restoration tool
        check-after-update.py              # Read-only post-OTA firmware audit tool
        restore-all.ps1 / restore-all.sh   # Direct platform rollback scripts
        restore-package.ps1 / .sh          # Single package restore scripts
    logs/
        transactions.jsonl                 # Immutable JSON Lines transaction log
    tests/
        test_debloat_mock.py               # Unit tests with mocked ADB responses
```

---

## Target Device Profile (Tested Session)

- **Manufacturer & Model:** Oyster_Labs UBS1 (`Universal_Phone_1`)
- **Chipset:** Unisoc (Spreadtrum) T616 Octa-Core (`ums9230`)
- **OS Version:** Android 14 (API Level 34, Security Patch 2024-09-05)
- **Active Android User:** User 0 (`Owner`)
- **Connection Type:** Official Paired Wireless ADB (TLS)

---

## Usage Guide

### 1. Device Reconnaissance
Connect device via USB or Wireless ADB, then run:
```powershell
python scripts/detect-device.py
```

### 2. Full System Snapshot
Creates a timestamped snapshot of settings, package enabled states, and performance baselines:
```powershell
python scripts/backup.py
```

### 3. Generate Audit & Review Profiles
Cross-reference installed packages against UAD-NG and generate reviewable profiles:
```powershell
python scripts/audit.py
```

### 4. Execute Debloating (Controlled Batches)
Dry-run mode (default, no changes applied):
```powershell
python scripts/debloat.py --profile balanced
```

Apply live changes (executed in batches of ≤5 with post-batch stability verification):
```powershell
python scripts/debloat.py --profile balanced --apply
```

### 5. Post-Debloat Verification & Comparison
Validate system stability and calculate before/after resource metrics:
```powershell
python scripts/verify-and-compare.py
```

### 6. Restoring Packages
Restore all packages back to their original baseline states:
```powershell
python scripts/restore.py --all
# Or using native PowerShell:
.\scripts\restore-all.ps1
```

Restore a single package:
```powershell
python scripts/restore.py --package com.google.android.projection.gearhead
# Or using native PowerShell:
.\scripts\restore-package.ps1 -PackageName com.google.android.projection.gearhead
```

### 7. Post-OTA Firmware Update Audit
After receiving an Android system update:
```powershell
python scripts/check-after-update.py
```

---

## Security & Privacy Notice
No personal device serial numbers, IP credentials, MAC addresses, or private photos are tracked in this repository. All scripts are idempotent, reviewable, and designed for device recovery.
