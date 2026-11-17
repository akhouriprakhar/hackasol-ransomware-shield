# RULES.md - Hard Technical Constraints & Anti-Patterns

> **PURPOSE**: Enforces locked dependencies, naming standards, execution safety, and anti-patterns for Hack-a-Sol 5.0.

---

## 1. Locked Tech Stack & Runtime Mandates

### Backend, Agent & ML Core (Python 3.9+)
- **OS Target**: macOS Apple Silicon (`darwin-arm64`).
- **Telemetry & Process Control**: `watchdog >= 3.0.0` (using `FSEvents`), `psutil >= 5.9.0` (POSIX `SIGSTOP`/`SIGCONT`).
- **Machine Learning**: `scikit-learn >= 1.2.0`, `numpy >= 1.24.0` (Offline execution only).
- **Web & Async**: `fastapi >= 0.100.0`, `uvicorn >= 0.22.0`, `websockets >= 11.0`, `pydantic >= 2.0.0`.
- **Database**: Python standard library `sqlite3` (WAL mode enabled).
- **Test Runner**: `pytest >= 7.3.0`.

### Frontend SOC Dashboard (Node.js v26+ & React)
- **Framework**: React 18+ with TypeScript (`.tsx`).
- **Build Tool**: Vite (`vite >= 5.0.0`).
- **Styling & Components**: Tailwind CSS, `lucide-react`, `recharts >= 2.10.0`.
- **Networking**: Native browser WebSocket API + lightweight `fetch`.

---

## 2. Strictly FORBIDDEN Anti-Patterns

- ❌ **No Windows or Linux OS Branching**: Do not include Win32 API calls (`ctypes.windll`, `ReadDirectoryChangesW`, `vssadmin`) or Linux-specific eBPF/fanotify. All process control is strictly POSIX via `psutil`.
- ❌ **No External Cloud APIs or LLMs in Detection**: Detection and XAI scoring must run 100% locally and offline in `< 50ms`. Never call OpenAI, Gemini, or remote endpoints inside the telemetry loop.
- ❌ **No Shell Injection Risks**: Never use `subprocess.Popen(..., shell=True)` or unsanitized `os.system()`. Commands must be passed as validated token lists.
- ❌ **No Unbounded File Scanning**: Do not calculate entropy on entire multi-gigabyte files. Strictly sample 4KB chunks (head + tail) to keep agent CPU `< 3%`.
- ❌ **No Live Malware**: Never run real ransomware payloads. Attack simulation is strictly handled by `simulator/brac_sim.py` targeting `./sandbox_targets/`.

---

## 3. Mandatory Naming & Code Conventions

| Component | Convention | Example |
| :--- | :--- | :--- |
| **Python Modules** | snake_case | `entropy.py`, `containment.py` |
| **Python Classes** | PascalCase | `EntropyCalculator`, `RiskArbiter` |
| **Python Functions** | snake_case | `calculate_chunk_entropy()`, `freeze_process()` |
| **TypeScript Components** | PascalCase | `KillChain.tsx`, `EntropyRadar.tsx` |
| **REST Endpoints** | kebab-case | `GET /api/v1/incidents`, `POST /api/v1/actions` |
| **WebSocket Paths** | kebab-case | `/ws/alerts`, `/ws/telemetry` |

---

## 4. Error Handling & Safety Fallbacks

1. **Defensive Signal Handling**:
   ```python
   try:
       proc = psutil.Process(pid)
       proc.suspend()  # Sends POSIX SIGSTOP
   except psutil.NoSuchProcess:
       logger.warning("Target PID %d exited before suspension.", pid)
   except psutil.AccessDenied:
       logger.error("Insufficient permissions to suspend PID %d.", pid)
   ```
2. **Heuristic Engine Failover**:
   - If the ML Isolation Forest model encounters an unexpected input shape or fails to initialize, immediately fail over to deterministic heuristic thresholds (Canary tamper + Entropy $\ge 7.5$) without crashing the telemetry loop.
3. **Sandbox Boundary Enforcement**:
   - `simulator/brac_sim.py` must verify `os.path.abspath(target_dir)` resolves strictly inside `sandbox_targets` before initiating any file modification.
