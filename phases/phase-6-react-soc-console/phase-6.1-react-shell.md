# Phase 6.1: Dark-Mode Obsidian Shell & Emergency Alert Banner (`App.tsx` & `NavigationHeader.tsx`)

## Objective
Build the overarching shell for the AegisRansom-X SOC console matching the specified obsidian color system, providing an emergency containment banner, fluid navigation, and a sticky status footer.

## Design System Specifications
- **Background**: `#080A0F` (deep obsidian void)
- **Cards & Surfaces**: `#11141D` (dark slate panel)
- **Borders & Dividers**: `1px solid #1F2433` (subtle grid stroke)
- **Typography**: `JetBrains Mono` for all metrics, latencies, PIDs, and entropy values; `Inter` for headers and labels
- **State Colors**:
  - Crimson `#EF4444`: Alerts, high entropy, cryo-freeze containment
  - Emerald `#10B981`: Safe states, allowlist immunity, APFS rollback
  - Amber `#F59E0B`: Canary tripwires, warnings
  - Tactical Cyan `#00F0FF`: Live streams, FSEvents telemetry

## Key Components
1. **Top Emergency Alert Banner**:
   - Component: [`frontend/src/components/NavigationHeader.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/NavigationHeader.tsx)
   - Text: *"Threat Cryo-Preserved: PID 32247 halted via POSIX SIGSTOP in 3.0ms | Blast radius locked: 0 / 54 files"*
   - Action: Green **"1-Click APFS Rollback"** button with instant visual confirmation badge upon click.
2. **Tab Navigation**:
   - 4 Tabs: `"Command Center"`, `"Threat Lab & Matrix"`, `"Incident Forensics"`, `"Kernel Telemetry"`.
   - Animated pill indicator powered by Framer Motion `layoutId="activeNavIndicator"`.
3. **Sticky Bottom Footer**:
   - Text: *"Apple Silicon M-Series (Darwin ARM64) · POSIX SIGSTOP Containment · Local Scikit-Learn IsolationForest · 100% Offline Operational"*.

## Verification & Proof
- `npm run build`: Zero errors.
- HTTP 200 on `http://127.0.0.1:5173`.
- Tested banner dismiss and rollback click states.
