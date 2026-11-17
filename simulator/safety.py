"""Safety Guardrails for AegisRansom-X Sandbox Operations.

Strictly enforces that all file generator and simulator activities are confined
exclusively to the project's `./sandbox_targets/` directory.
"""

from pathlib import Path
import os
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SANDBOX_TARGETS_DIR = (PROJECT_ROOT / "sandbox_targets").resolve()


class SandboxViolationError(PermissionError):
    """Raised when an operation attempts to access or mutate files outside sandbox_targets/."""
    pass


def get_sandbox_dir() -> Path:
    """Return the canonical, validated path to the sandbox targets directory."""
    if not SANDBOX_TARGETS_DIR.exists():
        SANDBOX_TARGETS_DIR.mkdir(parents=True, exist_ok=True)
    return SANDBOX_TARGETS_DIR


def assert_inside_sandbox(target_path: Path) -> Path:
    """Validate that target_path resolves strictly inside sandbox_targets/.
    
    Resolves symlinks and relative path components ('..') to prevent directory traversal.
    Raises SandboxViolationError if the resolved path is not within SANDBOX_TARGETS_DIR.
    """
    resolved_sandbox = get_sandbox_dir()
    resolved_target = Path(target_path).resolve()

    try:
        # relative_to will raise ValueError if resolved_target is not within resolved_sandbox
        rel = resolved_target.relative_to(resolved_sandbox)
        # Prevent targeting the root of sandbox_targets itself for file mutations if needed
    except ValueError:
        raise SandboxViolationError(
            f"[CRITICAL SAFETY INTERLOCK] Security boundary violation: "
            f"Target path '{resolved_target}' is outside sandbox directory '{resolved_sandbox}'!"
        )

    return resolved_target
