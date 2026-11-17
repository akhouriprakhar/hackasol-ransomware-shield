"""Configuration and constants for AegisRansom-X macOS Agent."""

import os
from pathlib import Path
from typing import Set

# Root directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SANDBOX_DIR = PROJECT_ROOT / "sandbox_targets"

# Canary file defaults (designed to sort first in directory enumerations)
CANARY_FILENAMES = [
    "!_00_passwords.xlsx",
    "_aa_financials.pdf",
    "!_00_credentials.txt",
    "_aa_audit.pdf",
]

# Protected system processes that must NEVER be frozen or terminated
PROTECTED_PROCESS_NAMES: Set[str] = {
    "kernel_task",
    "launchd",
    "WindowServer",
    "loginwindow",
    "fseventsd",
    "syslogd",
    "opendirectoryd",
    "diskarbitrationd",
    "mds",
    "mds_stores",
    "systemd",
    "init",
    "watchdog",
    "pytest",
    "node",
    "bash",
    "zsh",
    "sh",
    "sshd",
    "sudo",
}

# Protected PIDs (System root daemons and self/parent processes)
PROTECTED_PIDS: Set[int] = {0, 1}

# Telemetry limits
DEFAULT_CHUNK_SIZE: int = 4096
ENTROPY_HIGH_THRESHOLD: float = 7.5
EVENT_LATENCY_MAX_MS: float = 20.0
