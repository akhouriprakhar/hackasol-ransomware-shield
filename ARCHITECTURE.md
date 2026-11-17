# ARCHITECTURE.md - System Topology & Data Contracts

> **RUNTIME**: macOS Apple Silicon (`darwin-arm64`)  
> **ARCHITECTURAL PATTERN**: Local Event-Driven Asynchronous Pipeline + Micro-SOC Console  

---

## 1. Directory Tree Blueprint

```
/Users/akhouriprakhar/Downloads/Hack-a-Sol 5.0/
├── GEMINI.md                    # Root agy master constitution (<120 lines)
├── AGENTS.md                    # Lean subagent roles & file ownership
├── PRD.md                       # Hackathon product requirements & metrics
├── RULES.md                     # Locked dependencies & macOS constraints
├── ARCHITECTURE.md              # System topology, schemas & contracts
├── TASKS.md                     # Phased atomic task execution checklist
├── .env.example                 # Documented environment config
├── .gitignore                   # Multi-stack git exclusion rules
│
├── agent/                       # [macOS Telemetry & Containment]
│   ├── __init__.py
│   ├── config.py                # Environment & path configuration
│   ├── watcher.py               # FSEvents filesystem listener (watchdog)
│   ├── entropy.py               # 4KB chunk Shannon entropy calculator
│   ├── canary_manager.py        # Micro-canary deployment & tamper detection
│   └── containment.py           # POSIX SIGSTOP/SIGCONT cryo-freeze & rollback
│
├── engine/                      # [Offline ML & Risk Arbiter]
│   ├── __init__.py
│   ├── anomaly_model.py         # Scikit-learn Isolation Forest (<50ms offline)
│   ├── risk_arbiter.py          # Composite 0-100 risk score calculator
│   └── explainability.py        # Deterministic XAI feature attribution
│
├── backend/                     # [FastAPI Server & SQLite Hub]
│   ├── __init__.py
│   ├── main.py                  # Server entrypoint & route registration
│   ├── database.py              # SQLite WAL mode connection
│   ├── schemas.py               # Pydantic v2 data models
│   ├── ws_manager.py            # WebSocket alert broadcaster
│   └── routes/
│       ├── incidents.py         # Incident query & history
│       └── actions.py           # Analyst override (Resume, Kill, Restore)
│
├── frontend/                    # [React + Vite + Tailwind SOC Dashboard]
│   ├── index.html
│   ├── package.json
│   ├── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│           ├── Header.tsx       # System health & global threat posture
│           ├── KillChain.tsx    # Live incident event timeline
│           ├── EntropyRadar.tsx # Real-time entropy jump chart (Recharts)
│           └── ActionPanel.tsx  # Interactive Cryo-Release / Kill controls
│
├── simulator/                   # [Benign Ransomware Activity Simulator]
│   ├── __init__.py
│   └── brac_sim.py              # Harmless AES encryption simulator for sandbox
│
├── sandbox_targets/             # Strictly isolated directory for live demos
│   └── .gitkeep
│
└── tests/                       # [Verification Suite]
    ├── test_entropy.py          # Unit tests for chunked Shannon entropy
    ├── test_containment.py      # Tests for psutil POSIX SIGSTOP/SIGCONT
    └── test_risk_arbiter.py     # Tests for composite scoring & XAI
```

---

## 2. End-to-End System Sequence (macOS POSIX Containment)

```mermaid
sequenceDiagram
    autonumber
    participant Sim as Benign Simulator (brac_sim.py)
    participant FS as macOS FSEvents
    participant Agent as Agent (watcher + entropy)
    participant Engine as Offline ML (Isolation Forest)
    participant Contain as Containment (SIGSTOP)
    participant Backend as FastAPI & WebSocket Hub
    participant SOC as React SOC Dashboard

    Note over Sim,FS: Attack Simulation Begins in ./sandbox_targets/
    Sim->>FS: Rapid AES file encryption + rename (.locked)
    FS-->>Agent: FSEvents Stream (< 20ms)

    Agent->>Agent: 4KB Shannon Entropy (H > 7.5 in < 2ms)
    Agent->>Engine: Stream Feature Vector [Entropy, Velocity, Canary]
    Engine->>Engine: Local Isolation Forest Inference (< 50ms)
    Engine->>Engine: Composite Risk Score >= 80 (CRITICAL)

    critical Automated Cryo-Freeze (< 150ms)
        Engine->>Contain: Trigger Freeze on PID
        Contain->>Sim: psutil.Process.suspend() [POSIX SIGSTOP]
        Note over Sim: Process Execution Halted!
    end

    Engine->>Backend: Post Alert + XAI Trace Payload
    Backend->>SOC: Broadcast via WebSocket /ws/alerts
    Note over SOC: UI turns RED; Renders Kill Chain & XAI Breakdown

    opt Analyst Action
        SOC->>Backend: Analyst clicks "Resume (SIGCONT)" or "Rollback"
        Backend->>Contain: Dispatch Action
        Contain->>Sim: psutil.Process.resume() [POSIX SIGCONT]
    end
```

---

## 3. Data Contracts & Pydantic Schemas

### 3.1 Telemetry Event Payload
```json
{
  "event_id": "evt_4b2c1d",
  "timestamp": 1731835800.12,
  "event_type": "FILE_MODIFY",
  "file_path": "./sandbox_targets/data_01.txt.locked",
  "entropy_before": 3.42,
  "entropy_after": 7.91,
  "entropy_delta": 4.49,
  "pid": 48210,
  "process_name": "python3",
  "is_canary": false
}
```

### 3.2 Security Incident & XAI Payload (`/ws/alerts`)
```json
{
  "incident_id": "inc_99a8b7",
  "timestamp": 1731835800.25,
  "status": "CONTAINED",
  "risk_score": 94.0,
  "offending_pid": 48210,
  "process_name": "python3",
  "files_affected_count": 2,
  "detection_latency_ms": 130,
  "containment_method": "POSIX_SIGSTOP",
  "xai_breakdown": [
    { "factor": "CANARY_TRIPWIRE", "weight": 0.60 },
    { "factor": "ENTROPY_JUMP_ABOVE_7_5", "weight": 0.30 },
    { "factor": "WRITE_VELOCITY", "weight": 0.10 }
  ]
}
```

### 3.3 Analyst Action Request (`POST /api/v1/actions`)
```json
{
  "incident_id": "inc_99a8b7",
  "action": "RESUME_SIGCONT" 
}
```
*Valid actions*: `"RESUME_SIGCONT"`, `"TERMINATE_SIGKILL"`, `"ROLLBACK_RESTORE"`.
