#!/usr/bin/env python3
"""Standalone Live Demo Verification Script for AegisRansom-X.

Verifies the end-to-end autonomous defense pipeline on http://127.0.0.1:8000:
1. Health diagnostics check
2. Sandbox reset (50 benign files + 4 micro-canaries)
3. Benign user activity (asserting 0 alerts / zero false positives)
4. Burst ransomware attack:
   - Asserts offending PID enters macOS 'T' (SIGSTOP) state via psutil
   - Asserts blast radius on disk in ./sandbox_targets/ is <= 2 files
   - Asserts detection latency / MTTD < 100ms
5. 1-Click Rollback (asserting 0 .locked files remain on disk)
6. Terminate process (asserting SIGKILL halts the culprit)
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SANDBOX_DIR = PROJECT_ROOT / "sandbox_targets"
BASE_URL = "http://127.0.0.1:8000"


def http_get(endpoint: str, timeout: float = 5.0) -> Tuple[int, Any]:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data) if data else {}
    except urllib.error.HTTPError as e:
        err_data = e.read().decode("utf-8")
        return e.code, json.loads(err_data) if err_data else {}
    except Exception as e:
        return 0, str(e)


def http_post(endpoint: str, payload: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Tuple[int, Any]:
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
            return resp.status, json.loads(data) if data else {}
    except urllib.error.HTTPError as e:
        err_data = e.read().decode("utf-8")
        return e.code, json.loads(err_data) if err_data else {}
    except Exception as e:
        return 0, str(e)


def is_server_ready() -> bool:
    status, data = http_get("/api/health", timeout=1.0)
    return status == 200 and isinstance(data, dict) and data.get("status") == "healthy"


def start_temporary_server() -> Optional[subprocess.Popen]:
    """Start uvicorn in background if not already active."""
    if is_server_ready():
        print("  [•] Detected active FastAPI server running on http://127.0.0.1:8000")
        return None

    print("  [•] Starting temporary FastAPI server on http://127.0.0.1:8000...")
    python_bin = PROJECT_ROOT / ".venv" / "bin" / "python"
    if not python_bin.exists():
        python_bin = Path(sys.executable)

    uvicorn_cmd = [
        str(python_bin),
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--log-level",
        "error",
    ]

    proc = subprocess.Popen(
        uvicorn_cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(30):
        time.sleep(0.2)
        if is_server_ready():
            print("  [✔] Temporary FastAPI server ready.")
            return proc

    proc.kill()
    raise RuntimeError("Failed to launch temporary FastAPI server within timeout.")


def run_verification() -> bool:
    results: List[Tuple[str, str, str, bool]] = []
    server_proc = start_temporary_server()

    try:
        # Step 1: Health Diagnostic
        status, health = http_get("/api/health")
        passed = (
            status == 200
            and health.get("watcher", {}).get("active") is True
            and health.get("ml_model", {}).get("loaded") is True
        )
        results.append((
            "System Health",
            f"HTTP {status} (Watcher: Active, ML: Loaded)",
            "Active / 100% Offline ML",
            passed,
        ))

        # Step 2: Sandbox Reset
        status, reset_data = http_post("/api/simulator/reset")
        files_count = reset_data.get("files_count", 0)
        canaries_count = reset_data.get("canaries_count", 0)
        passed = status == 200 and files_count == 50 and canaries_count == 4
        results.append((
            "Sandbox Reset",
            f"HTTP {status} ({files_count} files + {canaries_count} canaries)",
            "50 benign + 4 canaries",
            passed,
        ))

        # Step 3: Benign User Activity
        status, benign_data = http_post("/api/simulator/start", {"mode": "benign"})
        time.sleep(0.4)
        _, incidents_after_benign = http_get("/api/incidents?limit=5")
        _, health_benign = http_get("/api/health")
        contained_pids = health_benign.get("contained_pids", [])
        
        passed = (
            status == 200
            and benign_data.get("status") == "started"
            and len(contained_pids) == 0
        )
        results.append((
            "Benign Activity",
            f"HTTP {status} (Zero false positives, {len(contained_pids)} frozen)",
            "0 alerts / Unfrozen",
            passed,
        ))

        # Step 4: Burst Ransomware Attack & Autonomous Containment
        t0 = time.perf_counter()
        status, burst_data = http_post("/api/simulator/start", {"mode": "burst", "extension": ".locked"})
        sim_pid = burst_data.get("pid", 0)
        
        is_frozen = False
        ps_state = "UNKNOWN"
        mttd_latency_ms = 0.0

        for _ in range(40):
            time.sleep(0.04)
            if sim_pid > 0:
                try:
                    p = psutil.Process(sim_pid)
                    ps_state = p.status()
                    if ps_state == psutil.STATUS_STOPPED:
                        is_frozen = True
                        mttd_latency_ms = (time.perf_counter() - t0) * 1000.0
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        # Check incidents API for exact detection latency
        time.sleep(0.1)
        _, inc_list = http_get("/api/incidents?limit=1")
        if inc_list and isinstance(inc_list, list) and len(inc_list) > 0:
            rec_latency = inc_list[0].get("detection_latency_ms", mttd_latency_ms)
            if rec_latency > 0:
                mttd_latency_ms = rec_latency

        # Check disk blast radius
        locked_files = list(SANDBOX_DIR.glob("*.locked"))
        blast_radius = len(locked_files)

        attack_passed = (
            is_frozen
            and ps_state == psutil.STATUS_STOPPED
            and blast_radius <= 2
            and mttd_latency_ms < 100.0
        )
        results.append((
            "Burst Attack Freeze",
            f"State: '{ps_state}' (SIGSTOP) | MTTD: {mttd_latency_ms:.1f}ms",
            "macOS 'T' Stopped & MTTD < 100ms",
            attack_passed,
        ))
        results.append((
            "Blast Radius on Disk",
            f"{blast_radius} .locked file(s) created before freeze",
            "<= 2 files affected",
            blast_radius <= 2,
        ))

        # Step 5: 1-Click Rollback (Zero Loss)
        status, rollback_data = http_post("/api/incidents/latest/action", {"action": "ROLLBACK_RESTORE"})
        time.sleep(0.1)
        remaining_locked = list(SANDBOX_DIR.glob("*.locked"))
        rollback_passed = status == 200 and len(remaining_locked) == 0
        results.append((
            "1-Click Rollback",
            f"HTTP {status} ({len(remaining_locked)} .locked files remaining)",
            "0 .locked files (Zero Loss)",
            rollback_passed,
        ))

        # Step 6: Terminate Process (SIGKILL)
        status, term_data = http_post("/api/incidents/latest/action", {"action": "TERMINATE_SIGKILL"})
        time.sleep(0.1)
        is_dead = False
        try:
            p = psutil.Process(sim_pid)
            is_dead = (p.status() == psutil.STATUS_ZOMBIE) or (not p.is_running())
        except psutil.NoSuchProcess:
            is_dead = True

        term_passed = status == 200 and is_dead
        results.append((
            "Terminate (SIGKILL)",
            f"HTTP {status} (PID {sim_pid} terminated)",
            "Process Dead",
            term_passed,
        ))

    finally:
        if server_proc:
            print("  [•] Halting temporary FastAPI server...")
            server_proc.kill()
            server_proc.wait(timeout=2.0)
        # Ensure any simulator processes reaped
        pkill_cmd = ["pkill", "-f", "simulator/brac_sim.py"]
        subprocess.run(pkill_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Print Clean Formatted Pass/Fail Table
    print("\n" + "=" * 80)
    print("     🛡️  AEGISRANSOM-X // LIVE DEMO STAGE READINESS VERIFICATION")
    print("=" * 80)
    print(f"{'CHECK':<25} | {'OBSERVED OUTPUT':<30} | {'EXPECTED':<12} | {'STATUS'}")
    print("-" * 80)

    all_passed = True
    for name, observed, expected, passed in results:
        status_str = "\033[0;32mPASS\033[0m" if passed else "\033[0;31mFAIL\033[0m"
        print(f"{name:<25} | {observed:<30} | {expected:<12} | {status_str}")
        if not passed:
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("\033[0;32m[✔] ALL LIVE DEMO VERIFICATION CHECKS PASSED PERFECTLY!\033[0m\n")
    else:
        print("\033[0;31m[✘] ONE OR MORE VERIFICATION CHECKS FAILED.\033[0m\n")

    return all_passed


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
