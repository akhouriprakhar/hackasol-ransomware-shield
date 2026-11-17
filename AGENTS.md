# AGENTS.md - Multi-Agent Coordination Protocol

> **PURPOSE**: Governs subagent execution, file ownership locks, and context hygiene for rapid 36-hour hackathon iteration.

---

## 1. Streamlined Subagent Roles (Hackathon Optimized)

To eliminate handoff bottlenecks during a 36-hour sprint, agent execution is organized into three lean operational roles:

### Role 1: `Systems-Lead` (macOS Telemetry, Entropy & Containment)
- **Scope**: `agent/`, `simulator/`, `tests/` (agent tests)
- **Responsibilities**:
  - Implements macOS filesystem listener (`watchdog` on `FSEvents`) and micro-canaries.
  - Implements 4KB chunk Shannon entropy calculator (< 2ms).
  - Implements POSIX `SIGSTOP` freeze and `SIGCONT` resume via `psutil`.
  - Implements safe sandboxed benign simulator (`simulator/brac_sim.py`).
- **Boundary**: Does not touch `frontend/` or modify `backend/` routes.

### Role 2: `ML-Engine-Lead` (Offline Anomaly Detector & Explainability)
- **Scope**: `engine/`, `tests/` (engine tests)
- **Responsibilities**:
  - Implements local Scikit-Learn `IsolationForest` on telemetry feature vectors.
  - Implements composite Risk Arbiter (0–100 scale) and heuristic rules.
  - Generates deterministic local feature attribution (< 50ms inference, zero LLM dependencies).
- **Boundary**: No direct host process kills or frontend modifications.

### Role 3: `Fullstack-SOC-Lead` (FastAPI Server & React Console)
- **Scope**: `backend/`, `frontend/`
- **Responsibilities**:
  - Implements FastAPI server, WebSocket alert broadcaster (`/ws/alerts`), and SQLite audit log.
  - Builds high-density React + Vite + Tailwind dark-mode SOC dashboard.
  - Connects interactive Cryo-Release and Terminate buttons to backend action endpoints.
- **Boundary**: Uses documented schemas; does not rewrite core sensor logic.

---

## 2. File Ownership Partition Matrix

| Tree / Directory | Primary Owner | Read-Only Access |
| :--- | :--- | :--- |
| `agent/**`, `simulator/**` | `Systems-Lead` | All agents |
| `engine/**` | `ML-Engine-Lead` | All agents |
| `backend/**` | `Fullstack-SOC-Lead` | All agents |
| `frontend/**` | `Fullstack-SOC-Lead` | All agents |
| `tests/**` | Active Role for their module | Shared |
| Governance (`GEMINI.md`, `PRD.md`, etc.) | **Coordinator Only** | All agents |

---

## 3. Fast-Path /plan & Execution Rules

1. **Multi-File Edits**:
   - Single-module or 1–2 file modifications proceed directly without planning friction.
   - Cross-cutting edits spanning 3+ files or crossing backend/frontend data contracts require a short `/plan` artifact.
2. **Context Window Hygiene**:
   - Use targeted range reads (`read_file` with line bounds) on large logs or datasets.
   - Store detailed benchmark outputs and test reports in `<Artifact Directory>` instead of conversational streaming.
3. **Rollback & Conflict Resolution**:
   - The data schemas defined in `@ARCHITECTURE.md` are the single source of truth. If frontend and backend diverge, backend `schemas.py` takes precedence.
