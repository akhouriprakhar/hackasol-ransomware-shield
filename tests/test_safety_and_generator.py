"""Tests for sandbox safety guardrails and benign sample generator."""

from pathlib import Path
import pytest

from simulator.safety import (
    assert_inside_sandbox,
    get_sandbox_dir,
    SandboxViolationError,
    PROJECT_ROOT,
    SANDBOX_TARGETS_DIR,
)
from simulator.sample_generator import populate_sandbox, calculate_entropy


def test_sandbox_safety_valid_paths():
    """Verify that paths inside sandbox_targets are accepted."""
    sandbox_dir = get_sandbox_dir()
    test_file = sandbox_dir / "valid_test_file.txt"
    resolved = assert_inside_sandbox(test_file)
    assert resolved == test_file.resolve()


def test_sandbox_safety_rejects_external_paths():
    """Verify that paths outside sandbox_targets raise SandboxViolationError."""
    # Attempting to target project root
    with pytest.raises(SandboxViolationError):
        assert_inside_sandbox(PROJECT_ROOT / "GEMINI.md")

    # Attempting to target system paths
    with pytest.raises(SandboxViolationError):
        assert_inside_sandbox(Path("/tmp/malicious.txt"))

    # Attempting traversal
    with pytest.raises(SandboxViolationError):
        assert_inside_sandbox(SANDBOX_TARGETS_DIR / ".." / "outside.txt")


def test_sample_generator_populates_50_files():
    """Verify sample generator creates 50 benign files with low entropy."""
    sandbox_dir = get_sandbox_dir()
    files = populate_sandbox(target_dir=sandbox_dir, count=50, clean=True)

    assert len(files) == 50
    for path, entropy in files:
        assert path.exists()
        assert path.is_file()
        assert entropy < 6.0  # Well below ransomware threshold (7.5+)
        assert path.suffix in [".txt", ".json", ".csv", ".pdf"]


def test_entropy_calculation_accuracy():
    """Verify Shannon entropy calculation on known distributions."""
    # Zero entropy for uniform single byte
    single_char = b"A" * 1000
    assert calculate_entropy(single_char) == 0.0

    # Low entropy for English prose
    prose = b"This is a standard low entropy test text file with repeated normal characters."
    entropy = calculate_entropy(prose)
    assert 3.0 < entropy < 5.0
