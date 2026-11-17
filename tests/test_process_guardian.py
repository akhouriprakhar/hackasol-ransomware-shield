"""Unit Tests for Process Guardian & Protected-Process Allowlist.

Verifies:
- macOS system process allowlist prevents SIGSTOP/SIGKILL targeting critical daemons.
- Protection of kernel_task (PID 0), launchd (PID 1), and Agent self process.
- Safe process attribution and error handling (NoSuchProcess, AccessDenied).
"""

import os
import subprocess
import sys
import pytest
import psutil

from agent.process_guardian import (
    ProcessGuardian,
    ProcessInfo,
    ProtectedProcessError,
)


def test_protected_system_pids():
    """PID 0, PID 1, self PID, and parent PID must be strictly protected."""
    guardian = ProcessGuardian()

    # PID 0 (Kernel)
    is_prot, reason = guardian.is_protected(0)
    assert is_prot is True
    assert "Kernel" in reason

    # PID 1 (launchd)
    is_prot, reason = guardian.is_protected(1)
    assert is_prot is True
    assert "launchd" in reason

    # Self PID
    is_prot, reason = guardian.is_protected(os.getpid())
    assert is_prot is True
    assert "self" in reason.lower()


def test_protected_process_names():
    """System daemons like WindowServer or fseventsd must be protected."""
    guardian = ProcessGuardian()
    assert "windowserver" in guardian.protected_names
    assert "launchd" in guardian.protected_names
    assert "fseventsd" in guardian.protected_names


def test_assert_safe_to_contain_guard():
    """Containment attempt on protected process must raise ProtectedProcessError."""
    guardian = ProcessGuardian()

    with pytest.raises(ProtectedProcessError) as exc_info:
        guardian.assert_safe_to_contain(1)
    assert "PID 1 is protected" in str(exc_info.value)

    with pytest.raises(ProtectedProcessError) as exc_info:
        guardian.assert_safe_to_contain(os.getpid())
    assert f"PID {os.getpid()} is protected" in str(exc_info.value)


def test_get_process_info_safe():
    """Metadata inspection must return valid ProcessInfo without raising."""
    guardian = ProcessGuardian()
    info = guardian.get_process_info(os.getpid())
    assert isinstance(info, ProcessInfo)
    assert info.pid == os.getpid()
    assert info.is_protected is True

    # Non-existent PID
    fake_pid = 99999999
    info_fake = guardian.get_process_info(fake_pid)
    assert info_fake.pid == fake_pid
    assert info_fake.status == "terminated"


def test_tracked_pid_lifecycle_and_attribution(tmp_path):
    """Can register, track, attribute, and unregister worker PIDs."""
    guardian = ProcessGuardian()

    # Launch a temporary benign worker subprocess
    worker = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(5)"])
    try:
        worker_pid = worker.pid
        guardian.register_tracked_pid(worker_pid)

        # Worker is not a protected system daemon
        is_prot, _ = guardian.is_protected(worker_pid)
        assert is_prot is False
        # Safety check passes
        guardian.assert_safe_to_contain(worker_pid)

        # Attribution test
        attr = guardian.attribute_event(tmp_path / "dummy.txt", hint_pid=worker_pid)
        assert attr is not None
        assert attr.pid == worker_pid

        # Unregister
        guardian.unregister_tracked_pid(worker_pid)
    finally:
        worker.terminate()
        worker.wait()
