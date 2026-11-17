# TASKS.md - Atomic Execution Roadmap

> **EXECUTION MODE**: macOS Apple Silicon · 100% Offline Local ML · Hack-a-Sol 5.0 (36-Hour Sprint)  
> **INSTRUCTIONS**: Execute sequentially. Check off `[ ]` to `[x]` upon meeting the Definition of Done (DoD).

---

## Phase 1: Environment Bootstrap & Safe Ransomware Simulator (READY TO EXECUTE)
- [x] **TASK-1.1: Git Repository Initialization & Hygiene**
  - Initialize local git repo on `main` branch.
  - Verify `.gitignore` excludes `.venv`, `__pycache__`, `node_modules`, and dummy sandbox artifacts.
  - *DoD*: `git status` shows clean tracking with governance files committed.
- [ ] **TASK-1.2: Python Virtual Environment & Dependency Lock**
  - Create Python 3.9+ virtual environment in `.venv/`.
  - Install runtime dependencies: `watchdog`, `psutil`, `scikit-learn`, `numpy`, `fastapi`, `uvicorn`, `pydantic`, `pytest`.
  - *DoD*: `python3 -m pytest --version` and imports of `psutil`, `watchdog`, `sklearn` succeed inside `.venv`.
- [ ] **TASK-1.3: Sandbox Workspace & Benign File Generator**
  - Create directory `./sandbox_targets/` with `.gitkeep`.
  - Build `simulator/sample_generator.py` that populates `./sandbox_targets/` with 50 harmless test files (`.txt`, `.json`, `.csv`, `.pdf` dummy buffers with typical low entropy ~3.5).
  - *DoD*: Running `python3 simulator/sample_generator.py` reliably creates 50 test files with low entropy.
- [ ] **TASK-1.4: Benign Ransomware Activity Simulator (`simulator/brac_sim.py`)**
  - Build safe simulator that performs high-speed AES encryption and appends `.locked` exclusively inside `./sandbox_targets/`.
  - Add hardcoded safety interlock: aborts immediately if target directory is outside `sandbox_targets/`.
  - Print live process PID and encryption velocity for observation.
  - *DoD*: Running `python3 simulator/brac_sim.py --dry-run` validates sandbox safety path and demonstrates file encryption on test targets.

---

## Phase 2: macOS Endpoint Sensing & Chunked Shannon Entropy
- [ ] **TASK-2.1: 4KB Chunk Shannon Entropy Calculator (`agent/entropy.py`)**
  - Implement fast byte-frequency entropy calculator on 4KB head/tail samples.
  - *DoD*: Unit test verifies plaintext file entropy ($3.0 - 5.0$) vs. encrypted sample entropy ($> 7.5$) in $< 2\text{ms}$.
- [ ] **TASK-2.2: Micro-Canary Honeyfile Manager (`agent/canary_manager.py`)**
  - Auto-generate canary files (`!_00_passwords.xlsx`, `_aa_financials.pdf`) in watched directories.
  - *DoD*: File write or rename targeting canary triggers an immediate priority interrupt flag.
- [ ] **TASK-2.3: macOS Filesystem Listener (`agent/watcher.py`)**
  - Implement `watchdog` observer using macOS `FSEvents` event loop on `./sandbox_targets/`.
  - *DoD*: Intercepts file create/modify/rename events and queues them with calculated entropy delta in $< 20\text{ms}$.

---

## Phase 3: 100% Offline ML Anomaly Model & Risk Arbiter
- [ ] **TASK-3.1: Offline Isolation Forest Model (`engine/anomaly_model.py`)**
  - Train and serialize a lightweight Scikit-Learn `IsolationForest` on feature vectors $[\Delta\text{Entropy}, \text{WriteVelocity}, \text{RenameRatio}, \text{CanaryHit}]$.
  - Ensure zero cloud/external API calls; inference time must be $< 50\text{ms}$.
  - *DoD*: Offline test proves model scores normal file edits $< 0.3$ and encrypted bursts $> 0.8$.
- [ ] **TASK-3.2: Real-Time Composite Risk Arbiter & XAI (`engine/risk_arbiter.py`)**
  - Synthesize heuristic rules and ML anomaly score into atomic $0 - 100$ risk score.
  - Output deterministic feature attribution breakdown (`CANARY_TRIPWIRE`, `ENTROPY_JUMP`, `WRITE_VELOCITY`).
  - *DoD*: Risk score crosses $\ge 80$ within 3 encrypted files during simulation.

---

## Phase 4: Non-Destructive POSIX Cryo-Freeze Containment
- [ ] **TASK-4.1: POSIX Process Freeze & Resume Controller (`agent/containment.py`)**
  - Implement process suspension using `psutil.Process(pid).suspend()` (POSIX `SIGSTOP`).
  - Implement process resume using `psutil.Process(pid).resume()` (POSIX `SIGCONT`).
  - Implement termination fallback using `psutil.Process(pid).kill()` (`SIGKILL`).
  - *DoD*: Unit test launches a mock worker process, freezes it via `suspend()`, verifies execution halts, and resumes it cleanly.
- [ ] **TASK-4.2: End-to-End Autonomous Containment Verification**
  - Integrate sensor, risk arbiter, and cryo-freeze controller.
  - Run `brac_sim.py` against 50 dummy files.
  - *DoD*: `brac_sim.py` process is frozen with `SIGSTOP` within $< 1.0\text{s}$, with $\le 2$ files encrypted.

---

## Phase 5: FastAPI Server & WebSocket Broadcast Hub
- [ ] **TASK-5.1: FastAPI App & SQLite Audit Ledger (`backend/main.py`)**
  - Set up FastAPI app with SQLite WAL mode persistence for incidents and events.
  - *DoD*: Health check endpoint `GET /api/v1/health` responds in $< 10\text{ms}$.
- [ ] **TASK-5.2: Real-Time WebSocket Alerts Channel (`backend/ws_manager.py`)**
  - Implement `/ws/alerts` WebSocket broadcaster streaming telemetry and incidents.
  - *DoD*: Connected WebSocket client receives simulated incident payload within $50\text{ms}$ of freeze.
- [ ] **TASK-5.3: Analyst Control Endpoints (`backend/routes/actions.py`)**
  - Implement `POST /api/v1/actions` with actions: `RESUME_SIGCONT`, `TERMINATE_SIGKILL`, `ROLLBACK_RESTORE`.
  - *DoD*: REST call resumes or terminates the suspended process PID reliably.

---

## Phase 6: React + Vite + Tailwind SOC Dashboard
- [ ] **TASK-6.1: Scaffold React Vite Dashboard (`frontend/`)**
  - Initialize React + Vite + TypeScript in `frontend/` with Tailwind CSS dark-mode SOC theme.
  - *DoD*: Frontend builds cleanly and loads at `http://localhost:5173`.
- [ ] **TASK-6.2: Kill Chain Timeline & Threat Status Component**
  - Build real-time event timeline showing Canary hits, entropy surges, and Cryo-Freeze execution.
  - *DoD*: UI flashes RED and displays `CONTAINED (SIGSTOP)` badge upon receiving WebSocket alert.
- [ ] **TASK-6.3: Live Shannon Entropy Chart & Action Panel**
  - Render real-time entropy spike chart using Recharts.
  - Add interactive buttons for **Resume (SIGCONT)**, **Terminate (SIGKILL)**, and **Rollback Files**.
  - *DoD*: Clicking "Resume" triggers backend action and restores UI to green status.

---

## Phase 7: Live Jury Demo Script & Verification
- [ ] **TASK-7.1: End-to-End Live Hackathon Demonstration Dry Run**
  - Execute full demo flow: generate dummy files $\to$ start dashboard $\to$ trigger `brac_sim.py` $\to$ verify automatic freeze in $< 1\text{s}$ $\to$ analyst inspects XAI breakdown and restores files.
  - *DoD*: Total MTTD $< 1.0\text{s}$, blast radius $\le 2$ files, zero crashes.
