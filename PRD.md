# PRD.md - Product Requirements Document
## Project: `AegisRansom-X` (macOS Ransomware Pre-Encryption Containment)

> **TRACK**: Cyber Security (Track 02) · Hack-a-Sol 5.0 (IIIT Naya Raipur)  
> **RUNTIME TARGET**: macOS (Apple Silicon), Python 3.9+, Node.js v26+  
> **EXECUTION MODE**: 100% Offline Local Inference  

---

## 1. Problem Statement & Hackathon Objective

### 1.1 The Post-Encryption Gap
Standard antivirus and EDR tools detect ransomware after mass encryption is already underway or when a ransom note appears. In a live enterprise scenario, this results in catastrophic data loss and protracted recovery.

### 1.2 The `AegisRansom-X` Solution
`AegisRansom-X` is a proactive, pre-encryption containment system tailored for macOS. It pairs near-instant userspace telemetry with 4KB chunk Shannon entropy evaluation, a 100% local Scikit-Learn Isolation Forest model, and instant POSIX `SIGSTOP` process freezing. 

During simulated attacks, the system halts the malicious process within **$< 1.0\text{ second}$**, limiting damage to **$\le 2$ dummy files** while preserving process RAM intact for live forensic inspection.

---

## 2. Core Personas & Live Demo Scenarios

1. **Hackathon Jury / Evaluation Panel**:
   - Observes live attack execution via `simulator/brac_sim.py` targeting 100 dummy files in `./sandbox_targets/`.
   - Sees the console flash RED within 500ms, status switch to `CRITICAL / CONTAINED`, the process frozen with `SIGSTOP`, and only 2 files modified.
   - Inspects the Explainable AI attribution chart showing why the model triggered.
2. **SOC Analyst / Incident Responder**:
   - Uses the React dashboard to inspect frozen process metadata (PID, parent process, command line, entropy delta).
   - Exercises interactive controls: **Resume (SIGCONT)**, **Terminate (SIGKILL)**, or **Rollback** affected files from the pre-encryption shadow cache.

---

## 3. Success Metrics & Performance Targets (KPIs)

- **Detection Latency (MTTD)**: $< 1.0\text{ second}$ from first encryption write (Hackathon target: $< 5.0\text{s}$).
- **Containment Latency (MTTC)**: $< 200\text{ milliseconds}$ from risk score threshold breach ($\ge 80$).
- **Offline ML Inference**: $< 50\text{ milliseconds}$ per telemetry window. Zero external network calls.
- **Blast Radius**: $\le 2$ files affected out of 100 in benchmark simulations.
- **Agent Footprint**: $< 3\%$ average CPU utilization during bursts; $< 100\text{ MB}$ RAM footprint.

---

## 4. Functional Requirements

### Module 1: macOS Endpoint Sensing (`agent/`)
- **FR-1: Real-Time Filesystem Monitoring**:
  - Intercepts file events (`CREATE`, `MODIFY`, `MOVED`, `DELETED`) on `./sandbox_targets/` using `watchdog` with native macOS `FSEvents` event loop.
- **FR-2: Fast Chunked Shannon Entropy**:
  - Computes Shannon entropy on 4KB sample chunks:
    $$H(X) = -\sum_{i=1}^{n} P(x_i) \log_2 P(x_i)$$
  - Normal files: $3.0 - 5.5$; Encrypted/compressed files: $> 7.5$. Execution latency $< 2\text{ms}$ per file.
- **FR-3: Micro-Canary Honeyfile Traps**:
  - Automatically provisions high-priority canary files (`!_00_credentials.xlsx`, `_aa_audit.pdf`) in watched roots. Any write or rename mutation immediately generates a critical priority interrupt (+80 risk points).
- **FR-4: Process Correlation**:
  - Inspects PID, executable name, command-line arguments, and parent PID using `psutil`.

### Module 2: Offline ML & Risk Arbiter (`engine/`)
- **FR-5: 100% Offline Isolation Forest Anomaly Detector**:
  - Evaluates sliding telemetry feature vectors:
    $$\vec{X} = [\Delta\text{Entropy}, \text{WriteVelocity}, \text{RenameCount}, \text{CanaryHit}, \text{NonStandardExt}]$$
  - Trained offline on benign developer/office activity vs. synthetic ransomware burst profiles.
- **FR-6: Real-Time Composite Risk Arbiter (0–100 Scale)**:
  - Aggregates ML anomaly score and heuristic rule hits. Risk score $\ge 80$ triggers immediate containment.
- **FR-7: Deterministic Explainable AI (XAI)**:
  - Generates top 3 contributing signals with percentage attribution (e.g., `[Canary Tamper: 70%, Entropy Surge: 25%, Write Velocity: 5%]`) with zero external LLM dependencies.

### Module 3: Active Containment (`agent/containment.py`)
- **FR-8: Non-Destructive POSIX Cryo-Freeze**:
  - Instantly suspends the target PID via `psutil.Process(pid).suspend()` (POSIX `SIGSTOP`), halting file I/O immediately without terminating the process.
- **FR-9: Analyst Controls**:
  - Supports analyst override via REST: `RESUME` (POSIX `SIGCONT`), `TERMINATE` (`SIGKILL`), and `RESTORE` (replaces encrypted files from temporary snapshot buffer).

### Module 4: Live SOC Dashboard (`backend/` & `frontend/`)
- **FR-10: Real-Time WebSocket Streaming**:
  - FastAPI streams live telemetry events and incident updates via `/ws/alerts`.
- **FR-11: Dark-Mode Threat Console**:
  - High-density React + Vite dashboard displaying:
    - Global Threat Posture & Status Badge (`NORMAL` vs `CONTAINED`).
    - Live Kill Chain Event Timeline.
    - Real-Time Shannon Entropy radar chart (Recharts).
    - Triage Drawer with XAI attribution and interactive action buttons.

### Module 5: Safe Demo Simulator (`simulator/`)
- **FR-12: Benign Ransomware Activity Simulator (`brac_sim.py`)**:
  - Generates 100 harmless dummy files in `./sandbox_targets/`.
  - Simulates rapid AES encryption and extension mutation (`.locked`).
  - Confined exclusively to `./sandbox_targets/` by strict path verification.

---

## 5. Explicit Out-of-Scope Boundaries (Hackathon Pruned)

- ❌ Windows Win32 APIs, registry hooks, or Linux eBPF drivers.
- ❌ External cloud LLMs, OpenAI/Gemini API calls, or cloud SIEM integrations.
- ❌ Complex user auth, multi-tenant RBAC, or enterprise SSO.
- ❌ Live destructive malware samples.
