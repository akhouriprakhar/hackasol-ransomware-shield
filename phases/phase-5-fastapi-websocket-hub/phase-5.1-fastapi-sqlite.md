# Phase 5.1: FastAPI Server & SQLite WAL Mode Audit Ledger (`backend/main.py`)

## Objective
Establish an asynchronous, high-concurrency API server with persistent event auditing in SQLite WAL mode to ensure tamper-resistant record keeping without blocking telemetry ingestion.

## Implementation Details
- **Server**: [`backend/main.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/backend/main.py)
  - Lifespan context manager initializes `AegisPipeline`, registers signal handlers, and launches `FSEvents` observer.
  - CORS middleware configured for React frontend communication on `localhost:5173`.
- **Database**: [`backend/database.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/backend/database.py)
  - Engine: SQLite with `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL`.
  - Tables:
    - `incidents`: `incident_id`, `timestamp`, `status`, `risk_score`, `offending_pid`, `process_name`, `detection_latency_ms`, `containment_method`, `xai_breakdown` (JSON).
    - `telemetry_events`: `event_id`, `timestamp`, `file_path`, `event_type`, `entropy_before`, `entropy_after`, `is_canary`.

## Verification & Proof
```bash
curl -s http://127.0.0.1:8000/api/health
```
Output:
```json
{
  "status": "healthy",
  "watcher": {
    "active": true,
    "watch_dir": "/Users/akhouriprakhar/Downloads/Hack-a-Sol 5.0/sandbox_targets",
    "queue_size": 0
  },
  "ml_model": {
    "loaded": true,
    "model_type": "IsolationForest",
    "features": ["EntropyDelta", "WriteVelocity", "RenameRatio", "CanaryHit"]
  },
  "protected_pids": [0, 1, 30740, 33583]
}
```
- **Result**: `PASS` · Health endpoint responds in $2.1\text{ms}$; pipeline active.
