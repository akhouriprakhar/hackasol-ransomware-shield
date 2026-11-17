"""POSIX Cryo-Freeze & Containment Controller for macOS (TASK-4.1).

Enforces non-destructive process suspension (POSIX SIGSTOP) and resumption
(POSIX SIGCONT) via psutil. Guaranteed safe by wiring directly to
ProcessGuardian.assert_safe_to_contain before any signal dispatch.
"""

import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import psutil

from agent.process_guardian import ProcessGuardian, ProtectedProcessError
from backend.schemas import AnalystAction, IncidentStatus

logger = logging.getLogger(__name__)


@dataclass
class ContainedProcessRecord:
    """Audit record of a contained process."""
    pid: int
    name: str
    cmdline: List[str]
    freeze_timestamp: float
    status: IncidentStatus
    resumed_timestamp: Optional[float] = None
    terminated_timestamp: Optional[float] = None


class ContainmentController:
    """Manages POSIX SIGSTOP cryo-freeze, SIGCONT resume, and SIGKILL termination."""

    def __init__(
        self,
        process_guardian: Optional[ProcessGuardian] = None,
        snapshot_dir: Optional[Union[str, Path]] = None,
    ):
        self.guardian = process_guardian or ProcessGuardian()
        self.snapshot_dir = Path(snapshot_dir or (Path(__file__).resolve().parent.parent / ".shadow_cache"))
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # In-memory tracking of contained PIDs: PID -> ContainedProcessRecord
        self._contained_pids: Dict[int, ContainedProcessRecord] = {}
        # Pre-encryption file backups: original_path -> backup_path
        self._shadow_backups: Dict[str, Path] = {}

    def is_contained(self, pid: int) -> bool:
        """Check if PID is currently tracked as cryo-frozen."""
        if pid not in self._contained_pids:
            return False
        record = self._contained_pids[pid]
        return record.status == IncidentStatus.CONTAINED

    def get_contained_pids(self) -> Set[int]:
        """Return the set of all currently active cryo-frozen PIDs."""
        return {
            pid for pid, rec in self._contained_pids.items()
            if rec.status == IncidentStatus.CONTAINED
        }

    def get_record(self, pid: int) -> Optional[ContainedProcessRecord]:
        """Fetch audit record for a given PID."""
        return self._contained_pids.get(pid)

    def freeze_process(self, pid: int) -> bool:
        """Instantly freeze a process using POSIX SIGSTOP.
        
        Guards:
            Calls self.guardian.assert_safe_to_contain(pid) first.
            Raises ProtectedProcessError if PID is protected.
            Handles psutil.NoSuchProcess and psutil.AccessDenied safely.
            
        Returns:
            True if process was suspended successfully, False otherwise.
        """
        # 1. Enforce strict safety boundary check
        self.guardian.assert_safe_to_contain(pid)

        # 2. Dispatch POSIX SIGSTOP via psutil
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            try:
                cmdline = proc.cmdline()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cmdline = []

            proc.suspend()  # Dispatches POSIX SIGSTOP
            logger.info("Cryo-Freeze SUCCESS: Process %s (PID %d) suspended via SIGSTOP.", name, pid)

            # Record containment audit state
            self._contained_pids[pid] = ContainedProcessRecord(
                pid=pid,
                name=name,
                cmdline=cmdline,
                freeze_timestamp=time.time(),
                status=IncidentStatus.CONTAINED,
            )
            return True

        except psutil.NoSuchProcess:
            logger.warning("Target PID %d exited before suspension.", pid)
            return False
        except psutil.AccessDenied:
            logger.error("Insufficient permissions to suspend PID %d.", pid)
            return False

    def resume_process(self, pid: int) -> bool:
        """Resume a suspended process using POSIX SIGCONT.
        
        Returns:
            True if process was resumed successfully, False otherwise.
        """
        try:
            proc = psutil.Process(pid)
            proc.resume()  # Dispatches POSIX SIGCONT
            logger.info("Cryo-Release SUCCESS: Process PID %d resumed via SIGCONT.", pid)

            if pid in self._contained_pids:
                self._contained_pids[pid].status = IncidentStatus.RELEASED
                self._contained_pids[pid].resumed_timestamp = time.time()
            return True

        except psutil.NoSuchProcess:
            logger.warning("Target PID %d exited before resume.", pid)
            if pid in self._contained_pids:
                self._contained_pids[pid].status = IncidentStatus.TERMINATED
            return False
        except psutil.AccessDenied:
            logger.error("Insufficient permissions to resume PID %d.", pid)
            return False

    def terminate_process(self, pid: int) -> bool:
        """Terminate a process using POSIX SIGKILL.
        
        Guards:
            Calls self.guardian.assert_safe_to_contain(pid) first.
            
        Returns:
            True if process was killed successfully, False otherwise.
        """
        self.guardian.assert_safe_to_contain(pid)

        try:
            proc = psutil.Process(pid)
            proc.kill()  # Dispatches POSIX SIGKILL
            logger.info("Termination SUCCESS: Process PID %d terminated via SIGKILL.", pid)

            if pid in self._contained_pids:
                self._contained_pids[pid].status = IncidentStatus.TERMINATED
                self._contained_pids[pid].terminated_timestamp = time.time()
            return True

        except psutil.NoSuchProcess:
            logger.info("Target PID %d already exited.", pid)
            if pid in self._contained_pids:
                self._contained_pids[pid].status = IncidentStatus.TERMINATED
            return True
        except psutil.AccessDenied:
            logger.error("Insufficient permissions to kill PID %d.", pid)
            return False

    def execute_analyst_action(self, pid: int, action: AnalystAction) -> bool:
        """Dispatch analyst action to corresponding process control method."""
        if action == AnalystAction.RESUME_SIGCONT:
            return self.resume_process(pid)
        elif action == AnalystAction.TERMINATE_SIGKILL:
            return self.terminate_process(pid)
        elif action == AnalystAction.ROLLBACK_RESTORE:
            return self.restore_shadow_backups()
        else:
            raise ValueError(f"Unknown analyst action: {action}")

    # --- Pre-Encryption Shadow Backup & Rollback Engine ---

    def create_shadow_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Create a shadow copy of a file before modification for instantaneous rollback."""
        src = Path(file_path).resolve()
        if not src.is_file():
            return None

        resolved_src = str(src)
        if resolved_src in self._shadow_backups:
            return self._shadow_backups[resolved_src]

        # Store in snapshot_dir preserving relative structure or hashing
        backup_file = self.snapshot_dir / f"bak_{abs(hash(resolved_src))}_{src.name}"
        try:
            shutil.copy2(src, backup_file)
            self._shadow_backups[resolved_src] = backup_file
            return backup_file
        except Exception as e:
            logger.warning("Failed to create shadow backup of %s: %s", src, e)
            return None

    def restore_shadow_backups(self) -> bool:
        """Rollback all backed-up files from the shadow cache to restore original state."""
        success = True
        for orig_str, backup_path in list(self._shadow_backups.items()):
            try:
                orig_path = Path(orig_str)
                # If ransomware appended .locked, also clean up the encrypted version
                locked_variant = Path(str(orig_path) + ".locked")
                if locked_variant.exists():
                    locked_variant.unlink()

                shutil.copy2(backup_path, orig_path)
                logger.info("Rollback restored original file: %s", orig_path)
            except Exception as e:
                logger.error("Failed to restore %s: %s", orig_str, e)
                success = False

        # Mark contained processes as RESTORED if applicable
        for record in self._contained_pids.values():
            if record.status == IncidentStatus.CONTAINED:
                record.status = IncidentStatus.RESTORED

        return success

    def clear_shadow_backups(self) -> None:
        """Clean up the shadow cache."""
        for backup_path in self._shadow_backups.values():
            try:
                if backup_path.exists():
                    backup_path.unlink()
            except Exception:
                pass
        self._shadow_backups.clear()
