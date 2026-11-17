"""Tests for Benign Ransomware Activity Simulator (BRAC-Sim)."""

from pathlib import Path
import pytest

from simulator.safety import SandboxViolationError, get_sandbox_dir
from simulator.brac_sim import (
    BenignRansomwareSimulator,
    SimSpeedMode,
    calculate_shannon_entropy,
    aes_encrypt_bytes,
)


@pytest.fixture
def sandbox_test_file(tmp_path_factory):
    """Create a temporary test file inside sandbox_targets for live test."""
    sandbox_dir = get_sandbox_dir()
    test_file = sandbox_dir / "unit_test_sample.txt"
    test_content = (
        b"Standard office memorandum. Quarterly metrics indicate positive growth. "
        b"Entropy should be typical low English text entropy under 5.0.\n"
    ) * 25  # ~2KB realistic office document
    test_file.write_bytes(test_content)
    yield test_file
    # Cleanup
    locked_file = test_file.with_name(test_file.name + ".locked")
    if test_file.exists():
        test_file.unlink()
    if locked_file.exists():
        locked_file.unlink()


def test_safety_interlock_blocks_external_targets():
    """Verify simulator refuses initialization on external directory."""
    with pytest.raises(SandboxViolationError):
        BenignRansomwareSimulator(target_dir=Path("/var/log"))

    with pytest.raises(SandboxViolationError):
        BenignRansomwareSimulator(target_dir=Path(".."))


def test_dry_run_does_not_mutate_disk(sandbox_test_file):
    """Verify dry run calculates entropy jump without creating .locked file."""
    sim = BenignRansomwareSimulator(
        target_dir=get_sandbox_dir(),
        speed_mode=SimSpeedMode.BURST,
        dry_run=True,
        max_files=1,
    )
    results = sim.run()

    assert len(results) >= 1
    sample_result = results[0]
    assert sample_result.entropy_before < 5.5
    assert sample_result.entropy_after > 7.5
    # Verify original file still exists and .locked was not written
    assert sandbox_test_file.exists()
    locked_path = sandbox_test_file.with_name(sandbox_test_file.name + ".locked")
    assert not locked_path.exists()


def test_live_encryption_within_sandbox(sandbox_test_file):
    """Verify live encryption produces .locked file with high entropy."""
    sim = BenignRansomwareSimulator(
        target_dir=get_sandbox_dir(),
        speed_mode=SimSpeedMode.BURST,
        dry_run=False,
    )
    result = sim.encrypt_single_file(sandbox_test_file)

    assert result.success is True
    assert result.entropy_after > 7.5
    assert result.duration_ms < 20.0  # Must be fast (< 20ms)

    # Verify locked file exists on disk
    assert result.encrypted_path.exists()
    assert result.encrypted_path.read_bytes().startswith(b"AEGIS_LOCKED:")
    assert not sandbox_test_file.exists()


def test_configurable_speed_modes():
    """Verify delay timings for burst, normal, and stealth modes."""
    sim_burst = BenignRansomwareSimulator(speed_mode=SimSpeedMode.BURST)
    assert sim_burst.delay_sec == 0.0

    sim_normal = BenignRansomwareSimulator(speed_mode=SimSpeedMode.NORMAL)
    assert sim_normal.delay_sec == 0.05

    sim_stealth = BenignRansomwareSimulator(speed_mode=SimSpeedMode.STEALTH)
    assert sim_stealth.delay_sec == 0.20

    sim_custom = BenignRansomwareSimulator(custom_delay_sec=0.012)
    assert sim_custom.delay_sec == 0.012
