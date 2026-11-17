"""Unit Tests for Micro-Canary Honeyfile Manager (TASK-2.2).

Verifies:
- Auto-generation of canary files (!_, _aa_ headers) in target directories.
- Immediate tripwire flag trigger upon write, modify, or rename.
- Robust recognition of ransomware-mutated names (.locked, .enc).
- Safe cleanup.
"""

from pathlib import Path
import pytest

from agent.canary_manager import (
    CANARY_FILENAMES,
    CanaryManager,
    CanaryTripwire,
    MOCK_PDF_HEADER,
    MOCK_XLSX_HEADER,
)


def test_canary_deployment(tmp_path):
    """Canary files must be auto-generated with realistic mock headers."""
    cm = CanaryManager()
    deployed = cm.deploy_canaries(tmp_path)

    assert len(deployed) == len(CANARY_FILENAMES)
    for p in deployed:
        assert p.exists()
        assert p.is_file()

    # Verify specific file formats
    xlsx_file = tmp_path / "!_00_passwords.xlsx"
    assert xlsx_file.exists()
    assert xlsx_file.read_bytes().startswith(b"PK\x03\x04")

    pdf_file = tmp_path / "_aa_financials.pdf"
    assert pdf_file.exists()
    assert pdf_file.read_bytes().startswith(b"%PDF-1.4")


def test_is_canary_identification(tmp_path):
    """is_canary must detect canary files by path, basename, and ransomware extensions."""
    cm = CanaryManager()
    cm.deploy_canaries(tmp_path)

    # 1. Direct path
    assert cm.is_canary(tmp_path / "!_00_passwords.xlsx") is True
    assert cm.is_canary(tmp_path / "_aa_financials.pdf") is True

    # 2. Ransomware mutated extensions
    assert cm.is_canary(tmp_path / "!_00_passwords.xlsx.locked") is True
    assert cm.is_canary(tmp_path / "_aa_financials.pdf.enc") is True
    assert cm.is_canary(tmp_path / "!_00_passwords.xlsx.crypto") is True

    # 3. Canary prefix convention
    assert cm.is_canary(tmp_path / "!_00_custom_credentials.txt") is True
    assert cm.is_canary(tmp_path / "_aa_secret_contracts.pdf") is True

    # 4. Benign normal files must return False
    assert cm.is_canary(tmp_path / "normal_data.csv") is False
    assert cm.is_canary(tmp_path / "notes_2026.txt") is False
    assert cm.is_canary(tmp_path / "report.json") is False


def test_canary_tripwire_tamper_alert(tmp_path):
    """DoD: File write or rename targeting canary triggers an immediate priority interrupt flag."""
    cm = CanaryManager()
    cm.deploy_canaries(tmp_path)

    target_canary = tmp_path / "!_00_passwords.xlsx"

    # Simulate write/modify event
    tripwire_modify = cm.check_tamper(target_canary, event_type="FILE_MODIFY")
    assert tripwire_modify is not None
    assert isinstance(tripwire_modify, CanaryTripwire)
    assert tripwire_modify.priority == "CRITICAL"
    assert tripwire_modify.canary_name == "!_00_passwords.xlsx"
    assert "breached by FILE_MODIFY" in tripwire_modify.description

    # Simulate rename event (.locked)
    renamed_path = tmp_path / "!_00_passwords.xlsx.locked"
    tripwire_rename = cm.check_tamper(renamed_path, event_type="FILE_RENAME")
    assert tripwire_rename is not None
    assert tripwire_rename.priority == "CRITICAL"
    assert "FILE_RENAME" in tripwire_rename.description

    # Normal file must not trip
    benign_tamper = cm.check_tamper(tmp_path / "user_notes.txt", event_type="FILE_MODIFY")
    assert benign_tamper is None


def test_canary_cleanup(tmp_path):
    """Canaries are cleanly unlinked upon cleanup call."""
    cm = CanaryManager()
    cm.deploy_canaries(tmp_path)
    assert len(cm.get_deployed_paths()) > 0

    removed = cm.cleanup_canaries(tmp_path)
    assert removed == len(CANARY_FILENAMES)
    assert len(cm.get_deployed_paths()) == 0

    for name in CANARY_FILENAMES:
        assert not (tmp_path / name).exists()
