# Phase 6: React + Vite + Tailwind Dark-Mode SOC Console

> **PHASE STATUS**: `COMPLETED & VERIFIED`  
> **SCOPE**: Production-grade dark obsidian SOC dashboard, emergency alert banner, 4 workflow tabs, and interactive controls.

---

## Executive Summary

Phase 6 provides the analyst user interface for AegisRansom-X. Built with React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, and Framer Motion, it implements a deep obsidian theme (`#080A0F`, `#11141D`, `#1F2433`) strictly avoiding generic AI aesthetics. It organizes workflows into 4 specialized tabs, features an emergency containment banner with a 1-click APFS rollback button, and connects to the backend via WebSocket and REST.

---

## Sub-Phase Breakdown

1. [**Phase 6.1: Dark-Mode Obsidian Shell & Emergency Alert Banner**](./phase-6.1-react-shell.md)
   - Deep obsidian palette: `#080A0F` (bg), `#11141D` (cards), `1px #1F2433` (borders), `JetBrains Mono` for metrics.
   - Top emergency alert banner: *"Threat Cryo-Preserved: PID 32247 halted via POSIX SIGSTOP in 3.0ms | Blast radius locked: 0 / 54 files"* with green **"1-Click APFS Rollback"** button.
   - Sticky bottom status footer: *"Apple Silicon M-Series (Darwin ARM64) · POSIX SIGSTOP Containment · Local Scikit-Learn IsolationForest · 100% Offline Operational"*.
2. [**Phase 6.2: Command Center Tab**](./phase-6.2-command-center.md)
   - 4-card top KPI strip showing entropy, intercept latency, armed canaries, and allowlist.
   - Real-time Recharts line chart plotting Shannon entropy ($0.0 - 8.0$) with dashed crimson threshold line at $H(X) = 7.5$.
   - Live scrolling FSEvents kernel log stream with Isolation Forest inference times ($< 50\text{ms}$).
   - Command Center Threat Arbiter & Action Ribbon.
3. [**Phase 6.3: Threat Lab & Matrix Tab**](./phase-6.3-threat-lab-matrix.md)
   - Two-column layout:
     - Left: `Safe Ransomware Simulator (brac_sim.py)` control card (Sec 06/09 badges, `./sandbox_targets/` lock, file count selector, "Trigger Safe Attack Sim" button).
     - Right: `ProcessGuardian Allowlist & Safety Boundary` table (`kernel_task`, `launchd`, `WindowServer`, `fseventsd`, `zsh`, `python`).
   - Interactive 54-File APFS Disk Matrix with file inspector drawer.
4. [**Phase 6.4: Incident Forensics Tab**](./phase-6.4-forensics-vault.md)
   - Cryo-Quarantine Dossier & XAI Attribution factor breakdown.
   - Remediation controls: 1-Click Rollback, Terminate (SIGKILL), Resume (SIGCONT).
5. [**Phase 6.5: Kernel Telemetry Tab**](./phase-6.5-kernel-telemetry.md)
   - Live FSEvents ring buffer table with search, quick filters, and JSON export.

---

## Verification Evidence
- Production build: `npm run build` completed with zero TypeScript errors.
- Dev server running on `http://127.0.0.1:5173`.
- Tested in browser: instant tab switching, live telemetry updates, immediate button click feedback.
