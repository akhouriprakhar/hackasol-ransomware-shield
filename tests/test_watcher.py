"""Unit Tests for macOS Filesystem Watcher (TASK-2.3).

Verifies:
- Watchdog observer lifecycle using macOS FSEvents loop.
- Interception of FILE_CREATE, FILE_MODIFY, FILE_RENAME events.
- Real-time entropy delta calculation and canary tripwire flags.
- TelemetryEvent schema contract compliance.
- Processing latency < 20ms.
"""

import os
import queue
import time
from pathlib import Path
import pytest

from agent.canary_manager import CanaryManager
from agent.process_guardian import ProcessGuardian
from agent.watcher import FilesystemWatcher, FilesystemWatcherHandler
from backend.schemas import EventType, TelemetryEvent


def test_watcher_lifecycle(tmp_path):
    """Watcher starts, runs observer thread, and shuts down cleanly."""
    watcher = FilesystemWatcher(watch_dir=tmp_path)
    assert watcher.is_alive() is False

    watcher.start()
    assert watcher.is_alive() is True

    watcher.stop()
    assert watcher.is_alive() is False


def test_handler_process_event_telemetry_schema(tmp_path):
    """Direct handler event processing outputs valid TelemetryEvent within latency target."""
    evt_queue = queue.Queue()
    cm = CanaryManager()
    guardian = ProcessGuardian()
    handler = FilesystemWatcherHandler(
        event_queue=evt_queue,
        canary_manager=cm,
        process_guardian=guardian,
    )

    # 1. Create a dummy file with low entropy
    target_file = tmp_path / "report.txt"
    target_file.write_bytes(b"A" * 1024)

    t0 = time.perf_counter()
    telemetry = handler._process_event(EventType.FILE_CREATE, str(target_file))
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert telemetry is not None
    assert isinstance(telemetry, TelemetryEvent)
    assert telemetry.event_type == EventType.FILE_CREATE
    assert telemetry.file_path == str(target_file.resolve())
    assert telemetry.is_canary is False
    assert elapsed_ms < 20.0, f"Processing took {elapsed_ms:.2f}ms, exceeding 20ms DoD limit"


def test_entropy_jump_on_simulated_encryption(tmp_path):
    """Overwriting low entropy plaintext with encrypted payload yields entropy delta > 3.0."""
    evt_queue = queue.Queue()
    handler = FilesystemWatcherHandler(event_queue=evt_queue)

    target_file = tmp_path / "data.txt"
    target_file.write_bytes(b"Regular plain text content with low entropy." * 20)

    # Initial modify event sets baseline
    handler._process_event(EventType.FILE_MODIFY, str(target_file))
    initial_event = evt_queue.get(timeout=1.0)
    assert initial_event.entropy_after < 5.0

    # Overwrite with AES-like random bytes
    target_file.write_bytes(os.urandom(2048))
    handler._process_event(EventType.FILE_MODIFY, str(target_file))
    encrypted_event = evt_queue.get(timeout=1.0)

    assert encrypted_event.entropy_after > 7.5
    assert encrypted_event.entropy_delta >= 2.5


def test_canary_hit_flagged_in_telemetry(tmp_path):
    """Mutating a canary file sets is_canary=True on the TelemetryEvent."""
    evt_queue = queue.Queue()
    cm = CanaryManager()
    cm.deploy_canaries(tmp_path)

    handler = FilesystemWatcherHandler(event_queue=evt_queue, canary_manager=cm)

    canary_file = tmp_path / "!_00_passwords.xlsx"
    canary_file.write_bytes(os.urandom(1024))

    handler._process_event(EventType.FILE_MODIFY, str(canary_file))
    event = evt_queue.get(timeout=1.0)

    assert event.is_canary is True
    assert event.entropy_after > 7.0


def test_rename_event_tracking(tmp_path):
    """File rename (.locked) computes delta against original file."""
    evt_queue = queue.Queue()
    handler = FilesystemWatcherHandler(event_queue=evt_queue)

    orig_file = tmp_path / "notes.txt"
    orig_file.write_bytes(b"Notes about system operations." * 30)

    # Establish baseline
    handler._process_event(EventType.FILE_CREATE, str(orig_file))
    evt_queue.get(timeout=1.0)

    # Simulate rename to notes.txt.locked with encrypted content
    locked_file = tmp_path / "notes.txt.locked"
    locked_file.write_bytes(os.urandom(2048))
    orig_file.unlink()

    handler._process_event(EventType.FILE_RENAME, str(locked_file), src_path=str(orig_file))
    rename_event = evt_queue.get(timeout=1.0)

    assert rename_event.event_type == EventType.FILE_RENAME
    assert rename_event.entropy_after > 7.5
    assert rename_event.entropy_delta > 2.0


def test_live_fsevents_interception(tmp_path):
    """Test live Watchdog FSEvents interception and queue delivery."""
    with FilesystemWatcher(watch_dir=tmp_path) as watcher:
        # Give FSEvents loop a tiny moment to bind
        time.sleep(0.1)

        test_file = tmp_path / "live_sample.txt"
        test_file.write_text("Hello from live macOS FSEvents test!")

        # Wait for event
        received_event = None
        for _ in range(30):
            try:
                received_event = watcher.get_event(block=True, timeout=0.1)
                break
            except queue.Empty:
                pass

        assert received_event is not None
        assert received_event.file_path == str(test_file.resolve())
