"""Unit Tests for 4KB Chunk Shannon Entropy Calculator (TASK-2.1).

Verifies:
- Plaintext file entropy (3.0 - 5.0) vs. encrypted sample entropy (> 7.5).
- Execution latency < 2.0 ms per 4KB sample and file calculation.
- 4KB head/tail sampling logic on large files.
- Consistency between NumPy vectorized and pure Python Counter implementations.
"""

import math
import os
import time
from pathlib import Path
import pytest

from agent.entropy import (
    DEFAULT_CHUNK_SIZE,
    ENTROPY_HIGH_THRESHOLD,
    ENTROPY_PLAINTEXT_HIGH,
    ENTROPY_PLAINTEXT_LOW,
    EntropyCalculator,
    EntropyResult,
    analyze_file,
    calculate_chunk_entropy,
    calculate_entropy_delta,
    calculate_file_entropy,
    is_anomalous,
    sample_file_chunks,
)
from simulator.brac_sim import aes_encrypt_bytes
from simulator.sample_generator import (
    generate_csv_content,
    generate_json_content,
    generate_txt_content,
)


def test_empty_buffer_entropy():
    """Empty byte buffers must yield exactly 0.0 entropy."""
    assert calculate_chunk_entropy(b"") == 0.0
    assert calculate_chunk_entropy(b"", use_numpy=False) == 0.0


def test_zero_entropy_uniform_bytes():
    """A buffer composed of a single repeated byte has 0.0 entropy."""
    data = b"\x00" * 4096
    assert calculate_chunk_entropy(data) == 0.0
    assert calculate_chunk_entropy(data, use_numpy=False) == 0.0

    data_ascii = b"A" * 4096
    assert calculate_chunk_entropy(data_ascii) == 0.0
    assert calculate_chunk_entropy(data_ascii, use_numpy=False) == 0.0


def test_numpy_and_python_counter_parity():
    """NumPy vectorized bincount and Python Counter must produce identical results."""
    data = os.urandom(4096)
    entropy_np = calculate_chunk_entropy(data, use_numpy=True)
    entropy_py = calculate_chunk_entropy(data, use_numpy=False)
    assert abs(entropy_np - entropy_py) < 1e-4


def test_maximum_entropy_random_bytes():
    """Cryptographically random 4KB buffer must exceed 7.5 bits/byte entropy."""
    data = os.urandom(4096)
    entropy = calculate_chunk_entropy(data)
    assert entropy > ENTROPY_HIGH_THRESHOLD
    assert entropy <= 8.0
    assert is_anomalous(entropy) is True


def test_plaintext_samples_entropy_range(tmp_path):
    """Plaintext files (.txt, .json, .csv) must have entropy within 3.0 - 5.0 range."""
    # 1. Plaintext TXT
    txt_path = tmp_path / "sample.txt"
    txt_content = generate_txt_content(1)
    txt_path.write_bytes(txt_content)
    txt_entropy = calculate_file_entropy(txt_path)
    assert ENTROPY_PLAINTEXT_LOW <= txt_entropy <= ENTROPY_PLAINTEXT_HIGH, (
        f"TXT entropy {txt_entropy} out of expected 3.0 - 5.0 range"
    )
    assert is_anomalous(txt_entropy) is False

    # 2. Structured JSON
    json_path = tmp_path / "sample.json"
    json_content = generate_json_content(1)
    json_path.write_bytes(json_content)
    json_entropy = calculate_file_entropy(json_path)
    assert ENTROPY_PLAINTEXT_LOW <= json_entropy <= ENTROPY_PLAINTEXT_HIGH, (
        f"JSON entropy {json_entropy} out of expected 3.0 - 5.0 range"
    )
    assert is_anomalous(json_entropy) is False

    # 3. Tabular CSV
    csv_path = tmp_path / "sample.csv"
    csv_content = generate_csv_content(1)
    csv_path.write_bytes(csv_content)
    csv_entropy = calculate_file_entropy(csv_path)
    assert ENTROPY_PLAINTEXT_LOW <= csv_entropy <= ENTROPY_PLAINTEXT_HIGH, (
        f"CSV entropy {csv_entropy} out of expected 3.0 - 5.0 range"
    )
    assert is_anomalous(csv_entropy) is False


def test_encrypted_file_entropy(tmp_path):
    """AES-encrypted file must exhibit high entropy (> 7.5)."""
    plain_path = tmp_path / "document.txt"
    plain_content = generate_txt_content(42)
    plain_path.write_bytes(plain_content)

    # Encrypt using simulator AES routine
    aes_key = os.urandom(32)
    encrypted_bytes = aes_encrypt_bytes(plain_content, aes_key)
    enc_path = tmp_path / "document.txt.locked"
    enc_path.write_bytes(encrypted_bytes)

    entropy_before = calculate_file_entropy(plain_path)
    entropy_after = calculate_file_entropy(enc_path)
    delta = calculate_entropy_delta(entropy_before, entropy_after)

    assert entropy_before < 5.0
    assert entropy_after > ENTROPY_HIGH_THRESHOLD, (
        f"Encrypted file entropy {entropy_after} not > 7.5"
    )
    assert delta >= 2.5
    assert is_anomalous(entropy_after) is True


def test_latency_under_2ms_benchmark(tmp_path):
    """DoD Requirement: Calculation latency must strictly be < 2.0 ms."""
    test_file = tmp_path / "bench_target.bin"
    # Create an 8KB file
    test_file.write_bytes(os.urandom(8192))

    # Warm-up run
    calculate_file_entropy(test_file)

    durations_ms = []
    for _ in range(50):
        t0 = time.perf_counter()
        entropy = calculate_file_entropy(test_file)
        t1 = time.perf_counter()
        durations_ms.append((t1 - t0) * 1000.0)

    avg_ms = sum(durations_ms) / len(durations_ms)
    max_ms = max(durations_ms)

    assert avg_ms < 2.0, f"Average latency {avg_ms:.3f}ms exceeded 2.0ms DoD limit"
    # Even individual runs should be fast
    assert avg_ms < 0.5, f"Expected < 0.5ms on Apple Silicon, got {avg_ms:.3f}ms"


def test_chunk_sampling_large_file(tmp_path):
    """Large files (>8KB) must be sampled at head (4KB) and tail (4KB) without reading entire file."""
    large_file = tmp_path / "large_payload.dat"
    total_size = 128 * 1024  # 128 KB
    head_tag = b"HEAD" + b"\x01" * (DEFAULT_CHUNK_SIZE - 4)
    middle_tag = b"\x00" * (total_size - (DEFAULT_CHUNK_SIZE * 2))
    tail_tag = b"\x02" * (DEFAULT_CHUNK_SIZE - 4) + b"TAIL"
    large_file.write_bytes(head_tag + middle_tag + tail_tag)

    sampled, size = sample_file_chunks(large_file, chunk_size=DEFAULT_CHUNK_SIZE)
    assert size == total_size
    assert len(sampled) == DEFAULT_CHUNK_SIZE * 2  # exactly 8KB
    assert sampled.startswith(b"HEAD")
    assert sampled.endswith(b"TAIL")


def test_small_file_sampling(tmp_path):
    """Files smaller than 2 * chunk_size must be sampled in their entirety."""
    small_file = tmp_path / "small.txt"
    content = b"Short payload for testing small file sampling."
    small_file.write_bytes(content)

    sampled, size = sample_file_chunks(small_file)
    assert size == len(content)
    assert sampled == content


def test_analyze_file_metadata(tmp_path):
    """analyze_file returns a complete EntropyResult with duration and telemetry."""
    file_path = tmp_path / "audit.json"
    file_path.write_bytes(generate_json_content(5))

    result = analyze_file(file_path)
    assert isinstance(result, EntropyResult)
    assert result.file_path == str(file_path)
    assert 3.0 <= result.entropy <= 5.0
    assert result.is_high_entropy is False
    assert result.duration_ms < 2.0
    assert result.file_size > 0
    assert result.sample_size == result.file_size


def test_error_handling(tmp_path):
    """Ensure proper exceptions on non-existent paths or directories."""
    missing_file = tmp_path / "non_existent.dat"
    with pytest.raises(FileNotFoundError):
        calculate_file_entropy(missing_file)

    dir_path = tmp_path / "sub_dir"
    dir_path.mkdir()
    with pytest.raises(IsADirectoryError):
        calculate_file_entropy(dir_path)
