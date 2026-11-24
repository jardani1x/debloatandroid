# AGENTS.md — CleanYourPhone Autonomous Roles & Execution Rules

## Operational Principles

1. **Sequential Lifecycle:**
   ```text
   DISCOVER → BACKUP → RESEARCH → CLASSIFY → PLAN → APPROVAL → DISABLE → VERIFY → RESTORE IF REQUIRED → REPORT
   ```
2. **Authority & Modification Rights:**
   - **Only the Main Execution Agent** holds authorization to run state-modifying ADB commands (`pm disable-user`, `pm enable`).
   - Subagents operate in strictly read-only mode for dependency analysis, research, and audit validation.
3. **Fail-Safe & Containment:**
   - No batch exceeds 5 packages.
   - After each batch, `com.android.systemui` PID and `android` package manager responsiveness must be verified.
   - If an error or process crash occurs, the script must immediately invoke rollback on the active batch and halt.

---

## Agent Specialization Roles

### 1. Main Execution Agent (`CleanYourPhone Orchestrator`)
- Owns live ADB connection and command execution.
- Manages target user boundary (`--user 0`).
- Validates pre-conditions and enforces user confirmation before modification.
- Records all operations into `logs/transactions.jsonl`.

### 2. Reconnaissance & Hardware Specialist
- Responsible for read-only device fingerprinting (`getprop`, `dumpsys`).
- Identifies underlying chipset BSP (e.g. Unisoc `ums9230`, MediaTek, Qualcomm, Tensor, Exynos).
- Detects OEM skin (One UI, HyperOS, ColorOS, OriginOS, Stock AOSP).

### 3. Package Dependency & Security Auditor
- Cross-references package inventories against UAD-NG database.
- Identifies privileged system integrations, declared services, and content providers via `dumpsys package`.
- Enforces strict protection on core telephony, IMS, biometrics, keystore, and emergency dispatch.

### 4. Verification & QA Agent
- Performs post-debloat functional verification across Home screen, Settings, Dialing, Play Store, and Connectivity.
- Analyzes `logcat` crash buffers for FATAL exceptions and ANRs.
- Compares RAM and process metrics against pre-modification baselines.
