"""Integrated Detection, Telemetry & Containment Pipeline for AegisRansom-X.

Coordinates FilesystemWatcher, ProcessGuardian, CanaryManager, RiskArbiter,
and ContainmentController into an event-driven engine wired to FastAPI & WebSockets.
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import psutil

from agent.canary_manager import CanaryManager
from agent.config import PROJECT_ROOT, SANDBOX_DIR
from agent.containment import ContainmentController
from agent.process_guardian import ProcessGuardian
from agent.watcher import FilesystemWatcher
from backend.database import AuditLedger
from backend.llm_copilot import LLMCopilotService
from backend.schemas import (

    AnalystAction,
    IncidentAlert,
    IncidentStatus,
    SimulatorStartRequest,
    TelemetryEvent,
)
from backend.ws_manager import ConnectionManager, ws_manager
from engine.anomaly_model import AnomalyDetector
from engine.risk_arbiter import RiskArbiter
from simulator.sample_generator import populate_sandbox

logger = logging.getLogger(__name__)


class AegisPipeline:
    """Central orchestrator for sensing, ML risk arbitration, and cryo-containment."""

    def __init__(
        self,
        sandbox_dir: Optional[Path] = None,
        db_path: Optional[Path] = None,
        ws_conn_mgr: Optional[ConnectionManager] = None,
    ):
        self.sandbox_dir = Path(sandbox_dir or SANDBOX_DIR).resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

        self.database = AuditLedger(db_path=db_path)
        self.ws_mgr = ws_conn_mgr or ws_manager

        self.guardian = ProcessGuardian()
        self.canary_manager = CanaryManager()
        self.containment = ContainmentController(process_guardian=self.guardian)

        self.anomaly_detector = AnomalyDetector()
        self.arbiter = RiskArbiter(anomaly_detector=self.anomaly_detector)
        self.copilot = LLMCopilotService(ws_conn_mgr=self.ws_mgr)


        self.watcher = FilesystemWatcher(
            watch_dir=self.sandbox_dir,
            canary_manager=self.canary_manager,
            process_guardian=self.guardian,
            on_event=self._handle_telemetry_event,
        )

        self.active_sim_procs: List[subprocess.Popen] = []
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._latest_incident: Optional[IncidentAlert] = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Bind the active asyncio event loop for thread-safe WebSocket broadcasts."""
        self.loop = loop

    def start(self) -> None:
        """Start background filesystem monitoring."""
        self.watcher.start()
        logger.info("AegisPipeline started watching %s", self.sandbox_dir)

    def stop(self) -> None:
        """Stop watcher and terminate any managed simulator processes."""
        self.stop_all_simulators()
        self.watcher.stop()
        logger.info("AegisPipeline stopped.")

    def dispatch_async(self, coro) -> None:
        """Safely schedule a coroutine onto the main asyncio loop from worker threads."""
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.loop)

    def _handle_telemetry_event(self, event: TelemetryEvent) -> None:
        """Process event from watcher thread, execute containment if critical, and broadcast."""
        t0 = time.perf_counter()

        # 1. Persist telemetry event & broadcast
        self.database.record_telemetry_event(event)
        self.dispatch_async(self.ws_mgr.broadcast_telemetry(event))

        # 2. Risk evaluation via composite arbiter (ML + Heuristics)
        assessment = self.arbiter.evaluate_event(event)

        # 3. Containment trigger threshold breach (Risk >= 80.0)
        if assessment.is_critical:
            target_pid = assessment.process_pid

            # Fallback PID correlation if event had none
            if not target_pid or target_pid <= 0:
                tracked = self.guardian.get_tracked_pids()
                if tracked:
                    target_pid = next(iter(tracked))
                else:
                    target_pid = self._discover_simulator_pid()

            if target_pid and target_pid > 0 and not self.containment.is_contained(target_pid):
                detection_latency_ms = (time.perf_counter() - t0) * 1000.0
                frozen = self.containment.freeze_process(target_pid)

                if frozen:
                    alert = self.arbiter.create_incident_alert(
                        assessment,
                        detection_latency_ms=max(1.0, detection_latency_ms),
                    )
                    # Offending PID ensure set
                    alert.offending_pid = target_pid
                    self._latest_incident = alert

                    self.database.record_incident(alert)
                    self.dispatch_async(self.ws_mgr.broadcast_incident(alert))
                    logger.warning(
                        "CRITICAL THREAT CONTAINED: PID %d frozen (Risk: %.1f). Latency: %.2fms",
                        target_pid,
                        assessment.risk_score,
                        detection_latency_ms,
                    )

                    # 4. Asynchronous Tier-2 AI Copilot (Dispatched post-freeze, never blocks hot path)
                    window = self.arbiter._get_window(target_pid)
                    affected_list = list(window.affected_files) if window else [event.file_path]
                    canary_name = os.path.basename(event.file_path) if event.is_canary else None

                    self.dispatch_async(
                        self.copilot.analyze_incident_async(
                            incident=alert,
                            target_file=event.file_path,
                            affected_files=affected_list,
                            canary_name=canary_name,
                        )
                    )


    def _discover_simulator_pid(self) -> Optional[int]:
        """Scan running processes for brac_sim.py in cmdline."""
        try:
            for p in psutil.process_iter(["pid", "name", "cmdline"]):
                cmdline = p.info.get("cmdline") or []
                if any("brac_sim.py" in arg for arg in cmdline):
                    pid = p.info["pid"]
                    self.guardian.register_tracked_pid(pid)
                    return pid
        except Exception:
            pass
        return None

    def start_simulator(self, req: SimulatorStartRequest) -> Dict[str, Union[str, int]]:
        """Launch brac_sim.py against sandbox_targets or simulate benign activity."""
        if req.mode.lower() == "benign":
            # Perform harmless, low-entropy modifications on up to 5 non-canary files
            txt_files = [f for f in sorted(self.sandbox_dir.glob("*.txt")) if not self.canary_manager.is_canary(f)]
            if not txt_files:
                # If no txt files exist, generate a benign sample file
                sample_file = self.sandbox_dir / "sample_doc_001.txt"
                sample_file.write_text("Quarterly audit notes: Developer workstation complies with corporate security policy.\n", encoding="utf-8")
                txt_files = [sample_file]

            modified = 0
            for f in txt_files:
                try:
                    with open(f, "a", encoding="utf-8") as fp:
                        fp.write(f"\n# Benign audit check at {time.strftime('%Y-%m-%d %H:%M:%S')}: Routine low-entropy edit.\n")
                    modified += 1
                    if modified >= (req.max_files or 5):
                        break
                except Exception as e:
                    logger.warning("Error during benign edit on %s: %s", f, e)
            logger.info("Executed benign activity simulation across %d files", modified)
            return {
                "status": "started",
                "mode": "benign",
                "message": f"Benign user editing activity simulated across {modified} files (low entropy, zero threat)",
            }

        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "simulator" / "brac_sim.py"),
            "--mode", req.mode,
            "--extension", req.extension,
        ]
        if req.max_files is not None:
            cmd.extend(["--max-files", str(req.max_files)])
        if req.delay is not None:
            cmd.extend(["--delay", str(req.delay)])

        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.active_sim_procs.append(proc)
        self.guardian.register_tracked_pid(proc.pid)
        logger.info("Launched simulator [PID %d] in mode %s", proc.pid, req.mode)

        return {
            "status": "started",
            "pid": proc.pid,
            "mode": req.mode,
            "message": f"BRAC-Sim started with PID {proc.pid}",
        }

    def stop_all_simulators(self) -> None:
        """Terminate all simulator child processes."""
        for proc in self.active_sim_procs:
            if proc.poll() is None:
                try:
                    proc.kill()
                    proc.wait(timeout=0.5)
                except Exception:
                    pass
                self.guardian.unregister_tracked_pid(proc.pid)
        self.active_sim_procs.clear()

    def reset_sandbox(self) -> Dict[str, Union[str, int]]:
        """Reset sandbox_targets with fresh 50 benign files + 4 canaries and prime shadow cache."""
        # 1. Stop any running simulators
        self.stop_all_simulators()

        # 2. Populate 50 fresh benign files
        files = populate_sandbox(target_dir=self.sandbox_dir, count=50, clean=True)

        # 3. Deploy micro-canary honeyfiles
        canaries = self.canary_manager.deploy_canaries(target_dir=self.sandbox_dir)

        # 4. Create pre-encryption shadow backups for instantaneous rollback
        self.containment.clear_shadow_backups()
        for f in self.sandbox_dir.iterdir():
            if f.is_file() and f.name != ".gitkeep":
                self.containment.create_shadow_backup(f)

        # 5. Prime entropy baseline cache in watcher
        self.watcher.prime_baseline()

        # 6. Reset ML sliding windows and active incidents
        self.arbiter.reset_window()
        self._latest_incident = None
        self.copilot._incident_narratives.clear()


        logger.info("Sandbox reset completed: %d files + %d canaries.", len(files), len(canaries))
        return {
            "status": "reset",
            "files_count": len(files),
            "canaries_count": len(canaries),
            "message": "Sandbox targets reset with fresh 50 benign files and 4 canaries.",
        }

    def execute_action(
        self,
        incident_id: str,
        action: AnalystAction,
    ) -> Dict[str, Any]:
        """Execute analyst action (RESUME_SIGCONT, TERMINATE_SIGKILL, ROLLBACK_RESTORE)."""
        incident: Optional[IncidentAlert] = None
        target_pid: Optional[int] = None

        if incident_id.lower() == "latest":
            # Priority 1: If any PID is currently frozen/contained, target that PID
            contained = self.containment.get_contained_pids()
            if contained:
                target_pid = next(iter(contained))
                # Check if there is an incident associated with this PID
                recent = self.database.get_recent_incidents(10)
                for inc in recent:
                    if inc.offending_pid == target_pid:
                        incident = inc
                        break
            else:
                incident = self._latest_incident or (
                    self.database.get_recent_incidents(1)[0]
                    if self.database.get_recent_incidents(1)
                    else None
                )
                if incident:
                    target_pid = incident.offending_pid
        else:
            incident = self.database.get_incident(incident_id)
            if incident:
                target_pid = incident.offending_pid

        # Fallback PID if incident was not found or has pid 0
        if not target_pid or target_pid <= 0:
            contained = self.containment.get_contained_pids()
            if contained:
                target_pid = next(iter(contained))

        result_msg = ""
        success = False

        if action == AnalystAction.RESUME_SIGCONT:
            if not target_pid:
                return {"status": "error", "message": "No PID found to resume"}
            success = self.containment.resume_process(target_pid)
            result_msg = f"Process {target_pid} resumed via SIGCONT"
            new_status = IncidentStatus.RELEASED

        elif action == AnalystAction.TERMINATE_SIGKILL:
            if not target_pid:
                return {"status": "error", "message": "No PID found to terminate"}
            success = self.containment.terminate_process(target_pid)
            result_msg = f"Process {target_pid} terminated via SIGKILL"
            new_status = IncidentStatus.TERMINATED

        elif action == AnalystAction.ROLLBACK_RESTORE:
            success = self.containment.restore_shadow_backups()
            result_msg = "Files successfully restored from pre-encryption shadow cache"
            new_status = IncidentStatus.RESTORED

        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

        # Update incident in DB and broadcast updated state
        if incident:
            incident.status = new_status
            self.database.update_incident_status(incident.incident_id, new_status)
            self.dispatch_async(self.ws_mgr.broadcast_incident(incident))

        return {
            "status": "success" if success else "failed",
            "incident_id": incident_id,
            "action": action.value if hasattr(action, "value") else str(action),
            "result": result_msg,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Compile health check diagnostics."""
        model_loaded = (
            self.arbiter.anomaly_detector.model is not None
        )
        total_files = 0
        locked_files = 0
        try:
            for p in self.sandbox_dir.iterdir():
                if p.name == ".gitkeep":
                    continue
                total_files += 1
                if p.name.endswith(".locked"):
                    locked_files += 1
        except Exception:
            pass

        return {
            "status": "healthy",
            "watcher": {
                "active": self.watcher.is_alive(),
                "watch_dir": str(self.watcher.watch_dir),
                "queue_size": self.watcher.queue_size(),
            },
            "ml_model": {
                "loaded": model_loaded,
                "model_type": "IsolationForest",
                "features": [
                    "EntropyDelta",
                    "WriteVelocity",
                    "RenameRatio",
                    "CanaryHit",
                ],
            },
            "protected_pids": sorted(list(self.guardian.protected_pids)),
            "contained_pids": sorted(list(self.containment.get_contained_pids())),
            "tracked_pids": sorted(list(self.guardian.get_tracked_pids())),
            "sandbox": {
                "total_files": total_files,
                "locked_files": locked_files,
            },
            "copilot": {
                "model": self.copilot.model,
                "ollama_url": self.copilot.ollama_url,
            },
            "latest_incident": self._latest_incident.model_dump() if self._latest_incident else None,

            "timestamp": time.time(),
        }
