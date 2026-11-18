# Phase 6.4: Incident Forensics Tab (`ForensicsView.tsx` & `IncidentPanel.tsx`)

## Objective
Provide an interactive forensics workbench displaying frozen process metadata, explainable AI factor breakdowns, and direct analyst cryo-remediation buttons.

## Implementation Details
- **Component**: [`frontend/src/components/views/ForensicsView.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/views/ForensicsView.tsx)
- **Cryo-Quarantine Dossier**: [`frontend/src/components/IncidentPanel.tsx`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/src/components/IncidentPanel.tsx)
  - Culprit PID, process name, interception timestamp, containment method (`POSIX_SIGSTOP`).
  - Animated MagicUI `BorderBeam` effect around quarantined container.
- **XAI Factor Attribution Sliders**:
  - `Canary Honeyfile Interaction`: Weight $0.46$
  - `4KB Chunk Shannon Entropy Delta`: Weight $0.27$
  - `Offline Isolation Forest Anomaly`: Weight $0.27$
- **Analyst Remediation Buttons**:
  1. **"1-Click APFS Rollback"**: Restores pre-encryption shadow cache and purges `.locked` files.
  2. **"Terminate (SIGKILL)"**: Permanently kills frozen process (wired to `POST /api/process/{pid}/signal`).
  3. **"Resume (SIGCONT)"**: Unfreezes process if deemed a false positive (wired to `POST /api/process/{pid}/signal`).
  4. Graceful offline fallback guarantees responsive feedback even during server restarts.

## Verification & Proof
- Verified signal dispatch to PID via REST API.
- Verified instant optimistic UI status updates (`CONTAINED` $\to$ `RESTORED` / `TERMINATED` / `RELEASED`).
