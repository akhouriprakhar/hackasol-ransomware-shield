# Phase 6.3: Threat Lab & Matrix Tab (`SimulationView.tsx` & `SandboxDiskMatrix.tsx`)

## Objective
Build the Threat Lab & Matrix tab matching the dark obsidian theme, split into two primary columns: safe simulator controls on the left, and the ProcessGuardian allowlist boundary on the right, accompanied by the 54-file APFS disk matrix.

## Implementation Details
- **Component**: [`frontend/src/components/views/SimulationView.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/views/SimulationView.tsx)
- **Left Column**: `Safe Ransomware Simulator (brac_sim.py)` Control Card:
  - Compliance Badges: `Rulebook Sec 06/09 Compliant` & `Zero Live Malware`.
  - Hardcoded Sandbox Lock: Displayed with lock icon: `./sandbox_targets/`.
  - Attack Vector Selector: `BURST` (0ms loop), `STEALTH` (200ms delay), `BENIGN` (safe edits).
  - Target File Count Selector: `10`, `25`, `50`, `54` files.
  - Prominent Crimson Button: **"Trigger Safe Attack Sim"** (wired to `POST /api/simulate/start`).
  - Reset Button: **"Reset Sandbox"** (wired to `POST /api/simulator/reset`).
- **Right Column**: `ProcessGuardian Allowlist & Safety Boundary`:
  - Table of protected system roots: `kernel_task` (PID 0), `launchd` (PID 1), `WindowServer` (PID 142), `fseventsd` (PID 88).
  - Table of protected developer tools: `zsh`, `bash`, `python / python3`, `pytest`.
  - All entries tagged with green **`IMMUNE TO SIGSTOP`** badges.
- **54-File APFS Disk Matrix**:
  - Component: [`frontend/src/components/SandboxDiskMatrix.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/SandboxDiskMatrix.tsx)
  - 4 Canary Honeyfiles strip (`!_00_passwords.xlsx`, etc.) with `ARMED` / `TRIPPED` status.
  - 50 Monitored business documents grid showing intact vs. `.locked` encrypted state.
  - Interactive file inspector drawer on click showing file size, format, and path.

## Verification & Proof
- Verified file count selector updates payload to `startSimulator(mode, count)`.
- Verified live APFS disk matrix reflects file mutations in real time.
