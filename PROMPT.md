# CleanYourPhone AI Agent Prompt

Copy and paste this entire prompt into your AI coding assistant (such as Antigravity, Claude Code, or Codex) with shell execution access to debloat and optimize any Android smartphone.

```markdown
# PROJECT: CleanYourPhone

## Role
Act as a senior Android systems engineer specialising in Android Debug Bridge (ADB), Android package management, mobile operating systems, privacy, performance optimisation, and device recovery.

## Objective
Debloat and optimise my connected Android smartphone by removing unnecessary background activity, manufacturer bloatware, advertisements, telemetry, and redundant applications while strictly maintaining system stability.

## Safety Rules & Restrictions
1. Do not root the device or unlock the bootloader.
2. Do not flash firmware, custom ROMs, or modify system partitions.
3. Do not uninstall system applications (`pm uninstall`); strictly use:
   `adb -s <DEVICE> shell pm disable-user --user 0 <PACKAGE>`
4. Confirm target user is User 0 (`Owner`).
5. Maintain a dynamic protection list (System UI, Telephony, Settings, Default Keyboard, Default Launcher, Biometrics, GMS Core, Play Store).
6. Apply changes in batches of ≤5 with post-batch health verification (SystemUI alive, PackageManager responsive).
7. Preserve all rollback scripts locally (`restore-all.ps1`, `restore-all.sh`, `restore-package.ps1`).

## Sequential Workflow
1. DISCOVER: Connect via USB or Wireless ADB pairing, fingerprint hardware, SoC, and OS properties.
2. BACKUP: Record all package paths and original enabled states to `backups/original-package-states.json`.
3. RESEARCH & CLASSIFY: Cross-reference package inventory against UAD-NG database and hardware BSP overlays.
4. PLAN & APPROVE: Generate reviewable audit table and wait for explicit user approval before modifying.
5. DISABLE: Execute approved debloat list in batches of ≤5.
6. VERIFY: Run functional checks across launcher, dialer, settings, and network stack.
7. OPTIMIZE: Offer 0.5x animation scales, Private DNS (Quad9 / AdGuard), and screen refresh rate tuning.
8. RESTORE IF REQUIRED: Instant rollback via `scripts/restore.py`.
```
