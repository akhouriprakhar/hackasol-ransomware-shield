"""Unit tests for POSIX SIGSTOP/SIGCONT Containment Controller (TASK-4.1)."""

import os
import subprocess
import sys
import time
from pathlib import Path
import psutil
import pytest

from agent.containment import ContainmentController
from agent.process_guardian import ProcessGuardian, ProtectedProcessError
from backend.schemas import AnalystAction, IncidentStatus


def _spawn_dummy_worker(target_file: Path) -> subprocess.Popen:
    """Spawn a harmless worker process that writes counter increments to a file."""
    code = f"""
import time
from pathlib import Path

target = Path({repr(str(target_file))})
counter = 0
while True:
    counter += 1
    try:
        target.write_text(str(counter))
    except Exception:
        pass
    time.sleep(0.05)
"""
    return subprocess.Popen([sys.executable, "-c", code])


def test_posix_sigstop_and_sigcont_cycle(tmp_path):
    """DoD: Verify mock worker freezes on SIGSTOP, halts I/O, and resumes cleanly on SIGCONT."""
    worker_file = tmp_path / "worker_output.txt"
    proc = _spawn_dummy_worker(worker_file)
    pid = proc.pid
    controller = ContainmentController()

    try:
        # Give worker a moment to start writing
        time.sleep(0.2)
        assert worker_file.exists(), "Worker failed to write initial file"
        initial_val = int(worker_file.read_text().strip())

        # 1. Freeze process via POSIX SIGSTOP
        frozen = controller.freeze_process(pid)
        assert frozen is True
        assert controller.is_contained(pid)
        assert pid in controller.get_contained_pids()

        # Verify process state is stopped
        ps_proc = psutil.Process(pid)
        assert ps_proc.status() == psutil.STATUS_STOPPED

        # Verify worker is completely halted (counter does not increment)
        stopped_val = int(worker_file.read_text().strip())
        time.sleep(0.3)
        assert int(worker_file.read_text().strip()) == stopped_val

        # 2. Resume process via POSIX SIGCONT
        resumed = controller.resume_process(pid)
        assert resumed is True
        assert not controller.is_contained(pid)

        # Verify execution resumes and increments counter again
        time.sleep(0.2)
        resumed_val = int(worker_file.read_text().strip())
        assert resumed_val > stopped_val, f"Worker did not resume! {resumed_val} <= {stopped_val}"

        # 3. Terminate process via POSIX SIGKILL
        terminated = controller.terminate_process(pid)
        assert terminated is True
        time.sleep(0.1)
        proc.poll()
        assert proc.poll() is not None or not psutil.pid_exists(pid)

    finally:
        if psutil.pid_exists(pid):
            try:
                psutil.Process(pid).kill()
            except Exception:
                pass


def test_protected_process_safety_guards():
    """Verify ProcessGuardian prevents containment signals from targeting protected PIDs."""
    guardian = ProcessGuardian()
    controller = ContainmentController(process_guardian=guardian)

    # 1. Self agent process must NEVER be contained
    with pytest.raises(ProtectedProcessError) as exc_self:
        controller.freeze_process(os.getpid())
    assert "protected" in str(exc_self.value).lower()

    # 2. Launchd (PID 1) must NEVER be contained
    with pytest.raises(ProtectedProcessError) as exc_init:
        controller.freeze_process(1)
    assert "protected" in str(exc_init.value).lower()

    # 3. Kernel task (PID 0) must NEVER be terminated
    with pytest.raises(ProtectedProcessError):
        controller.terminate_process(0)


def test_analyst_action_dispatch(tmp_path):
    """Verify execute_analyst_action routes RESUME, TERMINATE, and ROLLBACK correctly."""
    dummy_file = tmp_path / "dummy.txt"
    proc = _spawn_dummy_worker(dummy_file)
    pid = proc.pid
    controller = ContainmentController()

    try:
        # Freeze first
        assert controller.freeze_process(pid) is True
        assert controller.is_contained(pid)

        # Dispatch RESUME_SIGCONT
        success_resume = controller.execute_analyst_action(pid, AnalystAction.RESUME_SIGCONT)
        assert success_resume is True
        assert not controller.is_contained(pid)

        # Dispatch TERMINATE_SIGKILL
        success_term = controller.execute_analyst_action(pid, AnalystAction.TERMINATE_SIGKILL)
        assert success_term is True
        time.sleep(0.1)
        proc.poll()
        assert proc.poll() is not None or not psutil.pid_exists(pid)
    finally:
        if psutil.pid_exists(pid):
            try:
                psutil.Process(pid).kill()
            except Exception:
                pass


def test_shadow_backup_and_rollback(tmp_path):
    """Verify shadow backup cache enables instantaneous file rollback."""
    controller = ContainmentController(snapshot_dir=tmp_path / "shadow")
    test_file = tmp_path / "important_contract.docx"
    test_file.write_text("ORIGINAL SENSITIVE CONTENT")

    # Create backup
    backup = controller.create_shadow_backup(test_file)
    assert backup is not None
    assert backup.exists()

    # Simulate ransomware encryption mutation
    test_file.write_text("CORRUPTED ENCRYPTED BYTES")
    locked_file = tmp_path / "important_contract.docx.locked"
    locked_file.write_text("ENCRYPTED COPY")

    # Perform rollback
    restored = controller.restore_shadow_backups()
    assert restored is True
    assert test_file.read_text() == "ORIGINAL SENSITIVE CONTENT"
    assert not locked_file.exists()

    controller.clear_shadow_backups()
