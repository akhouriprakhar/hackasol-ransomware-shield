"""AegisRansom-X Agent Package: macOS Endpoint Sensing & Containment."""

from agent.canary_manager import CanaryManager, CanaryTripwire
from agent.config import CANARY_FILENAMES, PROTECTED_PROCESS_NAMES, SANDBOX_DIR
from agent.containment import ContainedProcessRecord, ContainmentController
from agent.entropy import (
    EntropyCalculator,
    EntropyResult,
    calculate_chunk_entropy,
    calculate_entropy_delta,
    calculate_file_entropy,
    is_anomalous,
    sample_file_chunks,
)
from agent.process_guardian import ProcessGuardian, ProcessInfo, ProtectedProcessError
from agent.watcher import FilesystemWatcher, FilesystemWatcherHandler

__all__ = [
    "CANARY_FILENAMES",
    "CanaryManager",
    "CanaryTripwire",
    "ContainedProcessRecord",
    "ContainmentController",
    "EntropyCalculator",
    "EntropyResult",
    "FilesystemWatcher",
    "FilesystemWatcherHandler",
    "PROTECTED_PROCESS_NAMES",
    "ProcessGuardian",
    "ProcessInfo",
    "ProtectedProcessError",
    "SANDBOX_DIR",
    "calculate_chunk_entropy",
    "calculate_entropy_delta",
    "calculate_file_entropy",
    "is_anomalous",
    "sample_file_chunks",
]
