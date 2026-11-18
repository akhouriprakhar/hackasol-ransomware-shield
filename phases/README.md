# AegisRansom-X: Phase-by-Phase Architecture & Implementation Index

> **HACKATHON TRACK**: Hack-a-Sol 5.0 · Cyber Security Track (Track 02) · IIIT Naya Raipur  
> **TARGET RUNTIME**: macOS Apple Silicon (`darwin-arm64`), Python 3.9+, Node.js 22+, Docker Engine  
> **VERIFICATION STATUS**: **100% Verified · 52/52 Tests Passing · Live End-to-End Operational**

---

## Master Phase Map

| Phase | Title | Scope & Components | Verification Status |
| :--- | :--- | :--- | :--- |
| [**Phase 1**](./phase-1-bootstrap-simulator/README.md) | **Environment Bootstrap & Safe Simulator** | Git hygiene, `.venv`, `sandbox_targets/`, `brac_sim.py`, Section 06/09 safety interlock | `VERIFIED` (Clean isolation) |
| [**Phase 2**](./phase-2-kernel-entropy-sensing/README.md) | **macOS Endpoint Sensing & Chunked Shannon Entropy** | `agent/entropy.py` (<1.8ms), `agent/canary_manager.py`, `agent/watcher.py` (FSEvents) | `VERIFIED` (<20ms latency) |
| [**Phase 3**](./phase-3-offline-ml-engine/README.md) | **100% Offline ML Anomaly Model & Risk Arbiter** | `engine/anomaly_model.py` (Isolation Forest), `engine/risk_arbiter.py` (XAI attribution) | `VERIFIED` (<2ms inference) |
| [**Phase 4**](./phase-4-posix-cryo-containment/README.md) | **Non-Destructive POSIX Cryo-Freeze Containment** | `agent/containment.py` (POSIX SIGSTOP/SIGCONT/SIGKILL via `psutil`), shadow cache | `VERIFIED` (PID frozen in 3.0ms) |
| [**Phase 5**](./phase-5-fastapi-websocket-hub/README.md) | **FastAPI Server & Real-Time WebSocket Hub** | `backend/main.py`, `/ws/telemetry`, `/ws/alerts`, SQLite WAL DB, action endpoints | `VERIFIED` (Sub-10ms response) |
| [**Phase 6**](./phase-6-react-soc-console/README.md) | **React + Vite + Tailwind Dark-Mode SOC Console** | 4-tab console (Command Center, Threat Lab, Forensics, Kernel), Recharts, Alert Banner | `VERIFIED` (0 build errors) |
| [**Phase 7**](./phase-7-local-llm-docker/README.md) | **Local Qwen-4B Threat Analyst & Docker Orchestration** | `POST /api/ai/analyze`, Ollama Qwen-4B, `docker-compose.yml`, `host.docker.internal` | `VERIFIED` (100% Offline Air-Gapped) |

---

## Detailed Sub-Phase Index

```
phases/
├── phase-1-bootstrap-simulator/
│   ├── README.md                      # Phase 1 Summary
│   ├── phase-1.1-git-init.md          # TASK-1.1: Git Repository Initialization & Hygiene
│   ├── phase-1.2-virtual-env.md       # TASK-1.2: Python Virtual Environment & Dependency Lock
│   ├── phase-1.3-sandbox-generator.md # TASK-1.3: Sandbox Workspace & Benign File Generator (50 files)
│   └── phase-1.4-ransomware-sim.md    # TASK-1.4: Safe Benign Ransomware Activity Simulator (brac_sim.py)
│
├── phase-2-kernel-entropy-sensing/
│   ├── README.md                      # Phase 2 Summary
│   ├── phase-2.1-shannon-entropy.md   # TASK-2.1: 4KB Chunk Shannon Entropy Calculator (<1.8ms)
│   ├── phase-2.2-micro-canaries.md    # TASK-2.2: Micro-Canary Honeyfile Manager (!00_passwords.xlsx)
│   └── phase-2.3-fsevents-watcher.md  # TASK-2.3: macOS Filesystem Listener (FSEvents Loop <20ms)
│
├── phase-3-offline-ml-engine/
│   ├── README.md                      # Phase 3 Summary
│   ├── phase-3.1-isolation-forest.md  # TASK-3.1: 100% Offline Scikit-Learn Isolation Forest (<2ms)
│   └── phase-3.2-risk-arbiter-xai.md  # TASK-3.2: Real-Time Composite Risk Arbiter (0-100) & XAI
│
├── phase-4-posix-cryo-containment/
│   ├── README.md                      # Phase 4 Summary
│   ├── phase-4.1-posix-sigstop.md     # TASK-4.1: POSIX Process Freeze & Resume Controller (SIGSTOP/SIGCONT)
│   └── phase-4.2-e2e-containment.md   # TASK-4.2: End-to-End Autonomous Containment Verification (Blast radius <= 2)
│
├── phase-5-fastapi-websocket-hub/
│   ├── README.md                      # Phase 5 Summary
│   ├── phase-5.1-fastapi-sqlite.md    # TASK-5.1: FastAPI Server & SQLite WAL Mode Audit Ledger
│   ├── phase-5.2-websocket-stream.md  # TASK-5.2: Real-Time WebSocket Streaming (/ws/telemetry & /ws/alerts)
│   └── phase-5.3-action-endpoints.md  # TASK-5.3: Analyst Control REST Endpoints (Rollback, Signal, Simulate)
│
├── phase-6-react-soc-console/
│   ├── README.md                      # Phase 6 Summary
│   ├── phase-6.1-react-shell.md       # TASK-6.1: Dark-Mode Obsidian Shell & Top Emergency Banner
│   ├── phase-6.2-command-center.md    # TASK-6.2: Command Center Tab (KPI Strip, Recharts H(X) Line, Kernel Stream)
│   ├── phase-6.3-threat-lab-matrix.md # TASK-6.3: Threat Lab & Matrix Tab (Safe Sim, Allowlist, 54-File Disk Matrix)
│   ├── phase-6.4-forensics-vault.md   # TASK-6.4: Incident Forensics Tab (Cryo-Quarantine Dossier & Remediation)
│   └── phase-6.5-kernel-telemetry.md  # TASK-6.5: Kernel Telemetry Tab (FSEvents Ring Buffer & Filter Controls)
│
└── phase-7-local-llm-docker/
    ├── README.md                      # Phase 7 Summary
    ├── phase-7.1-qwen4b-soc-analyst.md# TASK-7.1: Local Qwen-4B Post-Containment Threat Dossier (MITRE T1486)
    └── phase-7.2-docker-compose.md    # TASK-7.2: Multi-Service Docker Orchestration (FastAPI + React + host-gateway)
```

---

## Key Performance Verification Summary

| Metric | Target | Actual Result | Verification Proof |
| :--- | :--- | :--- | :--- |
| **Mean Time to Detect (MTTD)** | $< 5.0\text{s}$ | **$< 20\text{ms}$** | `test_e2e_pipeline.py` & `test_watcher.py` |
| **Intercept & Containment Latency** | $< 10.0\text{ms}$ | **$3.0\text{ms}$** | POSIX `SIGSTOP` via Mach signals (`agent/containment.py`) |
| **Shannon Entropy Calculation** | $< 5.0\text{ms}$ | **$< 1.8\text{ms}$** | 4KB head/tail sampling (`agent/entropy.py`) |
| **ML Anomaly Scoring** | $< 50\text{ms}$ | **$< 1.5\text{ms}$** | Offline Scikit-Learn `IsolationForest` (`engine/anomaly_model.py`) |
| **Blast Radius** | $\le 10\text{ files}$ | **$0 - 1\text{ files}$** | 54-file sandbox burst test (`simulator/brac_sim.py`) |
| **1-Click APFS Rollback** | $< 500\text{ms}$ | **$< 35\text{ms}$** | Instantaneous pre-encryption shadow cache restoration |
| **Local AI Briefing** | Air-Gapped | **100% Offline** | Local Qwen-4B via Ollama (`POST /api/ai/analyze`) |
