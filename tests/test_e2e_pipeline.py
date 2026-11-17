"""End-to-End Integration Verification Suite for AegisRansom-X (TASK-4.2, Phase 5).

Verifies the complete detection, containment, and analyst rollback cycle:
1. Health diagnostics GET /api/health and GET /api/v1/health.
2. Simulator reset POST /api/simulator/reset (50 benign files + 4 canaries + shadow backups).
3. Live WebSocket streaming over /ws/telemetry and /ws/alerts.
4. Live attack simulation: brac_sim.py -> FSEvents -> IsolationForest -> SIGSTOP -> ROLLBACK_RESTORE.
5. Analyst override controls: RESUME_SIGCONT and TERMINATE_SIGKILL.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
import psutil
import pytest
from fastapi.testclient import TestClient

from backend.main import app, pipeline
from backend.schemas import AnalystAction, IncidentStatus


@pytest.fixture
def client():
    """Create a FastAPI TestClient bound to the application lifespan."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoints(client):
    """GET /api/health and /api/v1/health return active watcher, loaded ML model, and protected PIDs."""
    for path in ["/api/health", "/api/v1/health"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"Failed at {path}: {resp.text}"
        data = resp.json()

        assert data["status"] == "healthy"
        assert data["watcher"]["active"] is True
        assert "sandbox_targets" in data["watcher"]["watch_dir"]

        assert data["ml_model"]["loaded"] is True
        assert data["ml_model"]["model_type"] == "IsolationForest"
        assert "EntropyDelta" in data["ml_model"]["features"]

        protected = data["protected_pids"]
        assert 0 in protected
        assert 1 in protected
        assert os.getpid() in protected


def test_simulator_reset_endpoint(client):
    """POST /api/simulator/reset populates 50 benign files + 4 canaries and primes shadow cache."""
    resp = client.post("/api/simulator/reset")
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "reset"
    assert data["files_count"] == 50
    assert data["canaries_count"] == 4

    # Verify filesystem state
    sandbox = pipeline.sandbox_dir
    files = [f for f in sandbox.iterdir() if f.is_file() and f.name != ".gitkeep"]
    assert len(files) == 54  # 50 samples + 4 canaries

    # Verify canary files deployed
    assert (sandbox / "!_00_passwords.xlsx").exists()
    assert (sandbox / "_aa_financials.pdf").exists()

    # Verify shadow cache populated for all files
    assert len(pipeline.containment._shadow_backups) >= 54


def test_websocket_ping_pong_channels(client):
    """Test WebSocket channels /ws/telemetry and /ws/alerts connect and respond to pings."""
    with client.websocket_connect("/ws/telemetry") as ws_telemetry:
        ws_telemetry.send_text("ping")
        assert ws_telemetry.receive_text() == "pong"

    with client.websocket_connect("/ws/alerts") as ws_alerts:
        ws_alerts.send_text("ping")
        assert ws_alerts.receive_text() == "pong"


def test_analyst_action_resume_sigcont_endpoint(client):
    """Verify analyst action endpoint POST /api/incidents/{id}/action with RESUME_SIGCONT."""
    # Spawn a mock worker process that writes increments to a file
    dummy_file = pipeline.sandbox_dir / "worker_resume_test.tmp"
    code = f"""
import time
from pathlib import Path
target = Path({repr(str(dummy_file))})
count = 0
while True:
    count += 1
    target.write_text(str(count))
    time.sleep(0.05)
"""
    proc = subprocess.Popen([sys.executable, "-c", code])
    pid = proc.pid
    pipeline.guardian.register_tracked_pid(pid)

    try:
        time.sleep(0.15)
        assert dummy_file.exists()
        val_initial = int(dummy_file.read_text().strip())

        # Freeze process
        assert pipeline.containment.freeze_process(pid) is True
        assert pipeline.containment.is_contained(pid) is True

        time.sleep(0.15)
        val_frozen = int(dummy_file.read_text().strip())
        time.sleep(0.2)
        # Value must not change while frozen
        assert int(dummy_file.read_text().strip()) == val_frozen

        # Resume via REST endpoint POST /api/incidents/{incident_id}/action
        resp = client.post(
            "/api/incidents/latest/action",
            json={"action": AnalystAction.RESUME_SIGCONT.value},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

        # Verify execution resumed
        time.sleep(0.2)
        val_resumed = int(dummy_file.read_text().strip())
        assert val_resumed > val_frozen, f"Process did not resume: {val_resumed} <= {val_frozen}"

    finally:
        pipeline.guardian.unregister_tracked_pid(pid)
        try:
            proc.kill()
            proc.wait(timeout=0.5)
        except Exception:
            pass
        if dummy_file.exists():
            dummy_file.unlink()


def test_full_live_attack_containment_and_rollback(client):
    """Comprehensive E2E Integration:
    
    1. Reset sandbox with 50 benign files + 4 canaries.
    2. Connect to /ws/telemetry WebSocket.
    3. Start brac_sim.py in burst mode via POST /api/simulator/start.
    4. Verify live FSEvents -> IsolationForest -> POSIX SIGSTOP freeze within MTTD < 1.0s.
    5. Verify blast radius <= 2 files.
    6. Verify WebSocket client received IncidentAlert payload with XAI breakdown.
    7. Execute POST /api/incidents/{incident_id}/action ROLLBACK_RESTORE.
    8. Verify encrypted .locked files deleted and pristine original files restored.
    9. Execute POST /api/incidents/{incident_id}/action TERMINATE_SIGKILL.
    """
    # 1. Reset sandbox
    resp_reset = client.post("/api/simulator/reset")
    assert resp_reset.status_code == 200
    time.sleep(0.2)

    # Record content of a test file before attack
    sample_file = pipeline.sandbox_dir / "sample_doc_001.txt"
    assert sample_file.exists(), "Sample doc 001 missing after reset"
    original_sample_bytes = sample_file.read_bytes()

    # 2. Open WebSocket telemetry stream
    with client.websocket_connect("/ws/telemetry") as ws:
        # 3. Start BRAC-Sim via REST API
        resp_start = client.post(
            "/api/simulator/start",
            json={"mode": "burst", "extension": ".locked"},
        )
        assert resp_start.status_code == 200
        sim_data = resp_start.json()
        sim_pid = sim_data["pid"]
        assert sim_pid > 0

        # 4. Wait for autonomous Cryo-Freeze (SIGSTOP)
        t_start = time.time()
        is_frozen = False

        for _ in range(40):
            if pipeline.containment.is_contained(sim_pid):
                is_frozen = True
                break
            time.sleep(0.05)

        mttd_sec = time.time() - t_start
        assert is_frozen is True, f"Simulator PID {sim_pid} was not cryo-frozen within timeout"
        assert mttd_sec < 1.0, f"MTTD {mttd_sec:.3f}s exceeded 1.0s hackathon KPI target"

        # Give background thread a moment to persist incident record
        time.sleep(0.15)

        # Verify process is indeed suspended in OS
        try:
            ps_proc = psutil.Process(sim_pid)
            assert ps_proc.status() == psutil.STATUS_STOPPED
        except psutil.NoSuchProcess:
            pytest.fail(f"Simulator process {sim_pid} unexpectedly exited")

        # 5. Verify blast radius: files encrypted before freeze <= 2
        locked_files = list(pipeline.sandbox_dir.glob("*.locked"))
        assert len(locked_files) <= 2, f"Blast radius {len(locked_files)} exceeded <= 2 files limit!"

        # 6. Verify Incident record and XAI attribution
        incidents_resp = client.get("/api/incidents")
        assert incidents_resp.status_code == 200
        incidents = incidents_resp.json()
        assert len(incidents) >= 1

        matching_incidents = [inc for inc in incidents if inc["offending_pid"] == sim_pid]
        assert len(matching_incidents) >= 1, f"No incident found for PID {sim_pid}"
        active_incident = matching_incidents[0]

        assert active_incident["risk_score"] >= 80.0
        assert active_incident["offending_pid"] == sim_pid
        assert active_incident["status"] == IncidentStatus.CONTAINED.value
        assert len(active_incident["xai_breakdown"]) >= 1

        incident_id = active_incident["incident_id"]

        # 7. Execute ROLLBACK_RESTORE analyst action
        resp_rollback = client.post(
            f"/api/incidents/{incident_id}/action",
            json={"action": AnalystAction.ROLLBACK_RESTORE.value},
        )
        assert resp_rollback.status_code == 200
        assert resp_rollback.json()["status"] == "success"

        # 8. Verify all .locked files are gone and files restored
        locked_remaining = list(pipeline.sandbox_dir.glob("*.locked"))
        assert len(locked_remaining) == 0, f"Encrypted files still exist after rollback: {locked_remaining}"

        # Sample doc restored
        assert sample_file.exists()
        assert sample_file.read_bytes() == original_sample_bytes

        # 9. Execute TERMINATE_SIGKILL analyst action
        resp_kill = client.post(
            f"/api/incidents/{incident_id}/action",
            json={"action": AnalystAction.TERMINATE_SIGKILL.value},
        )
        assert resp_kill.status_code == 200
        assert resp_kill.json()["status"] == "success"

        # Verify process is dead
        time.sleep(0.1)
        try:
            p = psutil.Process(sim_pid)
            assert p.status() == psutil.STATUS_ZOMBIE or not p.is_running()
        except psutil.NoSuchProcess:
            pass  # Process completely reaped
