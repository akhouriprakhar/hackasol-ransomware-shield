"""macOS Filesystem Listener & Telemetry Collector (TASK-2.3).

Uses watchdog with native macOS FSEvents event loop on ./sandbox_targets/
to intercept file create, modify, and rename mutations. Computes real-time
Shannon entropy deltas, detects canary tripwires, and correlates PIDs in < 20ms.
"""

import os
import queue
import time
import uuid
from pathlib import Path
from typing import Callable, Dict, Optional, Union
from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from agent.canary_manager import CanaryManager
from agent.config import DEFAULT_CHUNK_SIZE, SANDBOX_DIR
from agent.entropy import EntropyCalculator, calculate_entropy_delta
from agent.process_guardian import ProcessGuardian
from backend.schemas import EventType, TelemetryEvent


class FilesystemWatcherHandler(FileSystemEventHandler):
    """Event handler intercepting macOS filesystem mutations with entropy telemetry."""

    def __init__(
        self,
        event_queue: queue.Queue,
        canary_manager: Optional[CanaryManager] = None,
        process_guardian: Optional[ProcessGuardian] = None,
        on_event_callback: Optional[Callable[[TelemetryEvent], None]] = None,
    ):
        super().__init__()
        self.event_queue = event_queue
        self.canary_manager = canary_manager or CanaryManager()
        self.process_guardian = process_guardian or ProcessGuardian()
        self.on_event_callback = on_event_callback

        # In-memory baseline entropy cache: path -> float
        self._entropy_cache: Dict[str, float] = {}

    def _should_ignore(self, path: str) -> bool:
        """Filter out hidden, system, or temporary files."""
        name = Path(path).name
        if name.startswith(".DS_Store") or name.endswith(".tmp") or name == ".gitkeep":
            return True
        return False

    def _process_event(
        self,
        event_type: EventType,
        file_path: str,
        src_path: Optional[str] = None,
    ) -> Optional[TelemetryEvent]:
        """Process file event, compute entropy delta, attribute PID, and queue event."""
        if self._should_ignore(file_path):
            return None

        t0 = time.perf_counter()
        target_path = Path(file_path).resolve()

        # 1. Determine Canary hit
        is_canary = self.canary_manager.is_canary(target_path)
        if src_path and not is_canary:
            is_canary = self.canary_manager.is_canary(src_path)

        # 2. Entropy before / after calculation
        resolved_str = str(target_path)
        entropy_before = self._entropy_cache.get(
            str(Path(src_path).resolve()) if src_path else resolved_str,
            0.0,
        )

        entropy_after = 0.0
        if event_type != EventType.FILE_DELETE and target_path.exists() and not target_path.is_dir():
            try:
                entropy_after = EntropyCalculator.calculate_file_entropy(
                    target_path,
                    chunk_size=DEFAULT_CHUNK_SIZE,
                )
                self._entropy_cache[resolved_str] = entropy_after
            except (OSError, FileNotFoundError):
                entropy_after = 0.0
        elif event_type == EventType.FILE_DELETE:
            self._entropy_cache.pop(resolved_str, None)

        delta = calculate_entropy_delta(entropy_before, entropy_after)

        # 3. Process attribution
        proc_info = self.process_guardian.attribute_event(target_path)
        pid = proc_info.pid if proc_info else None
        proc_name = proc_info.name if proc_info else None

        # 4. Construct TelemetryEvent matching schemas.py contract
        telemetry = TelemetryEvent(
            event_id=f"evt_{uuid.uuid4().hex[:6]}",
            timestamp=time.time(),
            event_type=event_type,
            file_path=resolved_str,
            entropy_before=entropy_before,
            entropy_after=entropy_after,
            entropy_delta=delta,
            pid=pid,
            process_name=proc_name,
            is_canary=is_canary,
        )

        # 5. Dispatch to queue and optional callback
        self.event_queue.put(telemetry)
        if self.on_event_callback:
            try:
                self.on_event_callback(telemetry)
            except Exception:
                pass

        t1 = time.perf_counter()
        duration_ms = (t1 - t0) * 1000.0
        # Return telemetry with internal dispatch telemetry
        return telemetry

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_event(EventType.FILE_CREATE, event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._process_event(EventType.FILE_MODIFY, event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            return
        self._process_event(EventType.FILE_RENAME, event.dest_path, src_path=event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        self._process_event(EventType.FILE_DELETE, event.src_path)


class FilesystemWatcher:
    """macOS FSEvents filesystem listener wrapping watchdog Observer."""

    def __init__(
        self,
        watch_dir: Optional[Union[str, Path]] = None,
        canary_manager: Optional[CanaryManager] = None,
        process_guardian: Optional[ProcessGuardian] = None,
        on_event: Optional[Callable[[TelemetryEvent], None]] = None,
    ):
        self.watch_dir = Path(watch_dir or SANDBOX_DIR).resolve()
        self.watch_dir.mkdir(parents=True, exist_ok=True)

        self.canary_manager = canary_manager or CanaryManager()
        self.process_guardian = process_guardian or ProcessGuardian()
        self.event_queue: queue.Queue[TelemetryEvent] = queue.Queue()

        self.handler = FilesystemWatcherHandler(
            event_queue=self.event_queue,
            canary_manager=self.canary_manager,
            process_guardian=self.process_guardian,
            on_event_callback=on_event,
        )

        self._observer: Optional[Observer] = None
        self._running: bool = False

    def start(self) -> None:
        """Start background FSEvents filesystem watcher."""
        if self._running:
            return

        self._observer = Observer()
        self._observer.schedule(self.handler, str(self.watch_dir), recursive=True)
        self._observer.start()
        self._running = True

    def stop(self) -> None:
        """Stop watcher and join thread cleanly."""
        if not self._running or not self._observer:
            return

        self._observer.stop()
        self._observer.join(timeout=2.0)
        self._running = False
        self._observer = None

    def is_alive(self) -> bool:
        """Check if observer is currently listening."""
        return self._running and self._observer is not None and self._observer.is_alive()

    def get_event(self, block: bool = True, timeout: Optional[float] = None) -> TelemetryEvent:
        """Fetch next TelemetryEvent from queue."""
        return self.event_queue.get(block=block, timeout=timeout)

    def queue_size(self) -> int:
        """Current number of pending telemetry events in queue."""
        return self.event_queue.qsize()

    def prime_baseline(self) -> int:
        """Pre-populate entropy cache for all existing files in watch_dir."""
        count = 0
        for p in self.watch_dir.rglob("*"):
            if p.is_file() and not self.handler._should_ignore(str(p)):
                try:
                    e = EntropyCalculator.calculate_file_entropy(p)
                    self.handler._entropy_cache[str(p.resolve())] = e
                    count += 1
                except Exception:
                    pass
        return count

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
