"""PID Attribution & Protected-Process Allowlist for macOS (AegisRansom-X).

Provides safe process attribution for filesystem events and enforces a strict
macOS allowlist preventing POSIX SIGSTOP/SIGKILL from ever targeting system
daemons, root processes, or the agent itself.
"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import psutil

from agent.config import PROTECTED_PIDS, PROTECTED_PROCESS_NAMES


class ProtectedProcessError(RuntimeError):
    """Raised when an action targets a protected system or agent process."""
    pass


@dataclass(frozen=True)
class ProcessInfo:
    """Snapshot of process metadata attributed to a filesystem event."""
    pid: int
    name: str
    cmdline: List[str] = field(default_factory=list)
    ppid: Optional[int] = None
    status: str = "running"
    username: Optional[str] = None
    is_protected: bool = False
    protection_reason: Optional[str] = None


class ProcessGuardian:
    """Manages PID attribution and enforces protected process allowlists."""

    def __init__(
        self,
        custom_protected_names: Optional[Set[str]] = None,
        custom_protected_pids: Optional[Set[int]] = None,
    ):
        # Normalize protected names to lowercase for case-insensitive matching
        self.protected_names: Set[str] = {
            name.lower() for name in PROTECTED_PROCESS_NAMES
        }
        if custom_protected_names:
            self.protected_names.update(name.lower() for name in custom_protected_names)

        self.protected_pids: Set[int] = set(PROTECTED_PIDS)
        if custom_protected_pids:
            self.protected_pids.update(custom_protected_pids)

        # Always protect self (the agent) and parent process (the shell/runner)
        self.protected_pids.add(os.getpid())
        try:
            self.protected_pids.add(os.getppid())
        except AttributeError:
            pass

        # Registry for explicit simulator/monitored process tracking
        self._tracked_pids: Set[int] = set()

    def register_tracked_pid(self, pid: int) -> None:
        """Register a known target process (e.g. simulator worker PID)."""
        if pid > 0 and not self.is_protected(pid)[0]:
            self._tracked_pids.add(pid)

    def unregister_tracked_pid(self, pid: int) -> None:
        """Remove a PID from tracked list."""
        self._tracked_pids.discard(pid)

    def get_tracked_pids(self) -> Set[int]:
        """Return the current set of tracked target PIDs."""
        return set(self._tracked_pids)

    def is_protected(self, pid: int) -> Tuple[bool, Optional[str]]:
        """Check if a process is on the protected allowlist.

        Returns:
            Tuple of (is_protected: bool, reason: Optional[str]).
        """
        # 1. Check critical PIDs
        if pid in self.protected_pids:
            if pid == 0:
                return True, "Kernel task (PID 0)"
            elif pid == 1:
                return True, "System root launchd (PID 1)"
            elif pid == os.getpid():
                return True, "AegisRansom-X Agent self process"
            elif pid == os.getppid():
                return True, "Parent shell or test runner"
            return True, f"Protected PID {pid}"

        if pid <= 1:
            return True, f"Low system PID {pid}"

        # 2. Inspect process details via psutil
        try:
            proc = psutil.Process(pid)
            name = proc.name().lower()
            if name in self.protected_names:
                return True, f"Protected system/developer process name: {name}"

            # Check if root UID
            try:
                uids = proc.uids()
                if uids.real == 0:
                    return True, "Root-owned system process"
            except (AttributeError, psutil.AccessDenied):
                pass

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            if pid < 100:
                return True, f"Protected low PID {pid} (uninspectable)"

        return False, None

    def assert_safe_to_contain(self, pid: int) -> None:
        """Enforce safety guard before any containment signal is dispatched.

        Raises:
            ProtectedProcessError: If PID is protected.
        """
        protected, reason = self.is_protected(pid)
        if protected:
            raise ProtectedProcessError(
                f"Containment aborted: PID {pid} is protected ({reason})."
            )

    def get_process_info(self, pid: int) -> ProcessInfo:
        """Safely fetch metadata for a PID without throwing uncaught psutil errors."""
        protected, reason = self.is_protected(pid)
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            try:
                cmdline = proc.cmdline()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                cmdline = []
            try:
                ppid = proc.ppid()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                ppid = None
            try:
                status = proc.status()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                status = "unknown"
            try:
                username = proc.username()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                username = None

            return ProcessInfo(
                pid=pid,
                name=name,
                cmdline=cmdline,
                ppid=ppid,
                status=status,
                username=username,
                is_protected=protected,
                protection_reason=reason,
            )
        except psutil.NoSuchProcess:
            return ProcessInfo(
                pid=pid,
                name="<exited>",
                is_protected=protected,
                protection_reason=reason or "Process exited",
                status="terminated",
            )
        except psutil.AccessDenied:
            return ProcessInfo(
                pid=pid,
                name="<access_denied>",
                is_protected=True,
                protection_reason="System permission boundary",
                status="restricted",
            )

    def attribute_event(
        self,
        file_path: Union[str, Path],
        hint_pid: Optional[int] = None,
        scan_all_processes: bool = False,
    ) -> Optional[ProcessInfo]:
        """Attribute a filesystem mutation to the responsible process PID.

        Inspection priority:
        1. If explicit valid hint_pid provided, verify and return (< 0.1ms).
        2. If active registered tracked PIDs exist, check if still running (< 0.1ms).
        3. If scan_all_processes is True, scan current user processes with open file handles.
        """
        # 1. Hint PID inspection (< 0.1ms)
        if hint_pid and hint_pid > 0:
            try:
                if psutil.pid_exists(hint_pid):
                    return self.get_process_info(hint_pid)
            except Exception:
                pass

        # 2. Check tracked PIDs (e.g. active simulator) (< 0.1ms)
        for tpid in list(self._tracked_pids):
            try:
                if psutil.pid_exists(tpid):
                    proc = psutil.Process(tpid)
                    if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                        return self.get_process_info(tpid)
                else:
                    self._tracked_pids.discard(tpid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self._tracked_pids.discard(tpid)

        # 3. Optional deep open-files scan if requested
        if scan_all_processes:
            target_resolved = str(Path(file_path).resolve())
            try:
                current_uid = os.getuid()
                for proc in psutil.process_iter(["pid", "name", "uids"]):
                    try:
                        if proc.info["uids"] and proc.info["uids"].real == current_uid:
                            pid = proc.info["pid"]
                            if pid == os.getpid() or pid in self.protected_pids:
                                continue
                            for f in proc.open_files():
                                if f.path == target_resolved:
                                    return self.get_process_info(pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                pass

        return None
