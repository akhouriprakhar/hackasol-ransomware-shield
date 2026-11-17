"""Micro-Canary Honeyfile Manager for macOS Endpoint Sensing (TASK-2.2).

Deploys strategically named honeyfiles (!_, _aa_) that sort first in filesystem
enumerations. Any mutation (WRITE, MODIFY, RENAME, DELETE) on these honeyfiles
immediately triggers a critical priority interrupt flag.
"""

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from agent.config import CANARY_FILENAMES, SANDBOX_DIR


# Realistic binary mock headers for canary file types
MOCK_XLSX_HEADER = (
    b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00"
    b"[Content_Types].xml Mock Corporate Password Vault"
)
MOCK_PDF_HEADER = (
    b"%PDF-1.4\n"
    b"%\xe2\xe3\xcf\xd3\n"
    b"1 0 obj\n<< /Title (Corporate Financial Audit 2026) >>\nendobj\n"
)
MOCK_TXT_HEADER = (
    b"=== HIGH PRIORITY CREDENTIAL VAULT ===\n"
    b"Master Root Key: sec_live_9988221100aa\n"
    b"Database Host: db.internal.enterprise:5432\n"
)


@dataclass(frozen=True)
class CanaryTripwire:
    """Tripwire event emitted when a canary file is touched."""
    canary_name: str
    file_path: str
    event_type: str
    timestamp: float
    priority: str = "CRITICAL"
    description: str = "Unauthorized canary honeyfile mutation detected"


class CanaryManager:
    """Manages deployment, tracking, and tamper detection for micro-canaries."""

    def __init__(self, canary_names: Optional[List[str]] = None):
        self.canary_names: List[str] = canary_names or list(CANARY_FILENAMES)
        self._deployed_canaries: Dict[str, Path] = {}
        self._canary_basenames: Set[str] = set(self.canary_names)
        # Prefixes commonly indicating honeyfiles
        self._canary_prefixes: Tuple[str, ...] = ("!_00_", "_aa_", "!canary_")

    def deploy_canaries(self, target_dir: Optional[Union[str, Path]] = None) -> List[Path]:
        """Deploy honeyfiles into target directory.

        Args:
            target_dir: Target directory (defaults to configured SANDBOX_DIR).

        Returns:
            List of deployed canary Path objects.
        """
        directory = Path(target_dir or SANDBOX_DIR).resolve()
        directory.mkdir(parents=True, exist_ok=True)

        deployed = []
        for name in self.canary_names:
            canary_path = directory / name
            content = self._generate_canary_content(name)
            canary_path.write_bytes(content)
            self._deployed_canaries[str(canary_path.resolve())] = canary_path
            deployed.append(canary_path)

        return deployed

    def _generate_canary_content(self, filename: str) -> bytes:
        """Generate realistic content matching file extension."""
        lower = filename.lower()
        if lower.endswith(".xlsx"):
            return MOCK_XLSX_HEADER + (b"\x00" * 256)
        elif lower.endswith(".pdf"):
            return MOCK_PDF_HEADER + (b"\x00" * 256)
        else:
            return MOCK_TXT_HEADER + (b"\n" * 50)

    def is_canary(self, file_path: Union[str, Path]) -> bool:
        """Check if a file path corresponds to a canary honeyfile.

        Handles original names as well as ransomware-mutated names
        (e.g., '!_00_passwords.xlsx.locked' or '!_00_passwords.xlsx.enc').
        """
        path_str = str(file_path)
        # 1. Exact path match in registry
        resolved = str(Path(file_path).resolve()) if Path(file_path).is_absolute() else None
        if resolved and resolved in self._deployed_canaries:
            return True

        # 2. Check basename and stripped extensions (.locked, .enc, etc.)
        filename = Path(file_path).name
        # Strip common ransomware extensions iteratively
        test_name = filename
        for _ in range(2):
            if test_name.endswith((".locked", ".enc", ".crypto", ".ransom", ".aes")):
                test_name = test_name.rsplit(".", 1)[0]

        if test_name in self._canary_basenames:
            return True

        # 3. Check canary prefixes
        if any(filename.startswith(prefix) for prefix in ("!_00_", "_aa_", "!canary_")):
            return True

        return False

    def check_tamper(
        self,
        file_path: Union[str, Path],
        event_type: str = "FILE_MODIFY",
    ) -> Optional[CanaryTripwire]:
        """Check if an event touches a canary and return tripwire alert if so.

        Args:
            file_path: Path of affected file.
            event_type: Filesystem event type (e.g. FILE_MODIFY, FILE_RENAME).

        Returns:
            CanaryTripwire if canary was targeted, None otherwise.
        """
        if not self.is_canary(file_path):
            return None

        filename = Path(file_path).name
        return CanaryTripwire(
            canary_name=filename,
            file_path=str(file_path),
            event_type=event_type,
            timestamp=time.time(),
            priority="CRITICAL",
            description=f"Canary honeyfile {filename} breached by {event_type}",
        )

    def cleanup_canaries(self, target_dir: Optional[Union[str, Path]] = None) -> int:
        """Safely remove deployed canary files."""
        removed_count = 0
        directory = Path(target_dir or SANDBOX_DIR).resolve()

        for name in self.canary_names:
            canary_path = directory / name
            if canary_path.exists():
                try:
                    canary_path.unlink()
                    removed_count += 1
                except OSError:
                    pass

        self._deployed_canaries.clear()
        return removed_count

    def get_deployed_paths(self) -> List[Path]:
        """Return list of active deployed canary paths."""
        return list(self._deployed_canaries.values())
