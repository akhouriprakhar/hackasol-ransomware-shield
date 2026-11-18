# Phase 6.2: Command Center Tab (`OverviewView.tsx`)

## Objective
Implement the main Command Center view featuring the 4-card KPI strip, real-time Recharts Shannon entropy line chart, and scrolling FSEvents kernel log stream.

## Implementation Details
- **Component**: [`frontend/src/components/views/OverviewView.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/views/OverviewView.tsx)
- **(1) 4-Card Top KPI Strip**:
  1. `4KB Chunk Shannon Entropy H(X): 7.92 / 8.0 (<1.8ms)`:
     - Prominent metric display with critical threshold indicator ($H \ge 7.50$).
  2. `Intercept Latency: 3.0ms`:
     - Displays POSIX SIGSTOP dispatch speed ($< 5.0\text{ms}$ hardware target).
  3. `Micro-Canaries Armed: 4/4 (!_00_passwords.xlsx)`:
     - Shows armed alphabetical honeyfile tripwires.
  4. `ProcessGuardian Allowlist: Active`:
     - Shows zero-host-freeze protection active for system roots and developer tools.
- **(2) Real-Time Shannon Entropy Waveform Line Chart (Recharts)**:
  - Responsive line chart plotting Shannon entropy ($0.0 - 8.0$) across file write events.
  - Dashed crimson reference line at $H(X) = 7.5$ labeled:
    `CRITICAL THRESHOLD: 7.5 H(X) [POSIX SIGSTOP FREEZE]`
  - Tooltip inspects exact file name, timestamp, entropy score, and canary status.
- **(3) Live Sentinel Kernel Log Stream**:
  - Live scrolling box rendering FSEvents hooks (`FILE_MODIFY`, `FILE_RENAME`, `FILE_CREATE`).
  - Displays ML inference time for each write ($12\text{ms} - 28\text{ms}$, well below $< 50\text{ms}$).
- **Command Center Threat Arbiter Ribbon**:
  - Direct 1-Click Rollback and Threat Lab shortcut buttons directly within the Command Center.

## Verification & Proof
- Recharts chart rendered inside fixed `h-[300px]` canvas, preventing zero-height layout collapses.
- Real-time updates delivered via WebSocket `/ws/telemetry`.
