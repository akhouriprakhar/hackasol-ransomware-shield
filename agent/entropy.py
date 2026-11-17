"""Fast 4KB Chunk Shannon Entropy Calculator for macOS Endpoint Sensing.

Part of AegisRansom-X Agent: Real-time byte-frequency entropy calculation
on 4KB head/tail samples to detect rapid ransomware encryption activity.
"""

import math
import os
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# Default chunk size: 4096 bytes (4KB)
DEFAULT_CHUNK_SIZE: int = 4096

# Theoretical maximum entropy for 8-bit bytes: log2(256) = 8.0
MAX_ENTROPY: float = 8.0

# Critical thresholds
ENTROPY_HIGH_THRESHOLD: float = 7.5      # Ransomware / AES encrypted payload
ENTROPY_PLAINTEXT_LOW: float = 3.0       # Typical lower bound for normal docs
ENTROPY_PLAINTEXT_HIGH: float = 5.0      # Typical upper bound for normal text/code/data


@dataclass(frozen=True)
class EntropyResult:
    """Telemetry report for entropy calculation."""
    entropy: float
    sample_size: int
    file_size: int
    duration_ms: float
    is_high_entropy: bool
    file_path: Optional[str] = None


class EntropyCalculator:
    """Shannon entropy calculator optimized for 4KB chunk sampling."""

    DEFAULT_CHUNK_SIZE: int = DEFAULT_CHUNK_SIZE
    MAX_ENTROPY: float = MAX_ENTROPY
    HIGH_THRESHOLD: float = ENTROPY_HIGH_THRESHOLD

    @staticmethod
    def calculate_chunk_entropy(data: bytes, use_numpy: bool = True) -> float:
        """Calculate Shannon entropy H(X) for a byte sequence.

        Formula:
            H(X) = -sum(P(x_i) * log2(P(x_i)))
        where P(x_i) is the frequency of byte value x_i.

        Args:
            data: Raw byte buffer.
            use_numpy: If True and numpy is available, use vectorized bincount.

        Returns:
            Shannon entropy in bits per byte [0.0, 8.0].
        """
        total_len = len(data)
        if total_len == 0:
            return 0.0

        if HAS_NUMPY and use_numpy:
            arr = np.frombuffer(data, dtype=np.uint8)
            counts = np.bincount(arr, minlength=256)
            nonzero_counts = counts[counts > 0]
            probs = nonzero_counts / total_len
            entropy = -float(np.sum(probs * np.log2(probs)))
        else:
            counter = Counter(data)
            entropy = 0.0
            for count in counter.values():
                p = count / total_len
                entropy -= p * math.log2(p)

        # Numerical stability clamp to [0.0, 8.0]
        if entropy < 0.0:
            return 0.0
        if entropy > MAX_ENTROPY:
            return MAX_ENTROPY
        return round(entropy, 4)

    @classmethod
    def sample_file_chunks(
        cls,
        file_path: Union[str, Path],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Tuple[bytes, int]:
        """Read 4KB head and tail samples of a file without scanning unbounded size.

        For files <= 2 * chunk_size: reads the entire file.
        For files > 2 * chunk_size: reads first chunk_size (head) + last chunk_size (tail).

        Args:
            file_path: Path to target file.
            chunk_size: Byte size of head and tail samples (default 4KB).

        Returns:
            Tuple of (sampled_bytes, total_file_size).

        Raises:
            FileNotFoundError: If target file does not exist.
            IsADirectoryError: If path is a directory.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Target file does not exist: {path}")
        if path.is_dir():
            raise IsADirectoryError(f"Target path is a directory, not a file: {path}")

        file_size = path.stat().st_size
        if file_size == 0:
            return b"", 0

        with open(path, "rb") as f:
            if file_size <= chunk_size * 2:
                # File fits within 2 chunks: read entirely with zero overlap
                return f.read(), file_size

            # Sample head (chunk_size)
            head = f.read(chunk_size)

            # Sample tail (chunk_size) from end of file
            f.seek(file_size - chunk_size, os.SEEK_SET)
            tail = f.read(chunk_size)

            return head + tail, file_size

    @classmethod
    def calculate_file_entropy(
        cls,
        file_path: Union[str, Path],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> float:
        """Sample 4KB head/tail and calculate Shannon entropy.

        Args:
            file_path: Target file path.
            chunk_size: Chunk sample size in bytes (default 4096).

        Returns:
            Shannon entropy [0.0, 8.0].
        """
        sampled_bytes, _ = cls.sample_file_chunks(file_path, chunk_size=chunk_size)
        return cls.calculate_chunk_entropy(sampled_bytes)

    @classmethod
    def analyze_file(
        cls,
        file_path: Union[str, Path],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> EntropyResult:
        """Full analysis of a file's entropy with timing telemetry.

        Args:
            file_path: Target file path.
            chunk_size: Chunk sample size in bytes (default 4096).

        Returns:
            EntropyResult dataclass containing entropy, duration, and flags.
        """
        start_time = time.perf_counter()
        sampled_bytes, file_size = cls.sample_file_chunks(file_path, chunk_size=chunk_size)
        entropy = cls.calculate_chunk_entropy(sampled_bytes)
        duration_ms = (time.perf_counter() - start_time) * 1000.0

        return EntropyResult(
            entropy=entropy,
            sample_size=len(sampled_bytes),
            file_size=file_size,
            duration_ms=round(duration_ms, 3),
            is_high_entropy=(entropy >= cls.HIGH_THRESHOLD),
            file_path=str(file_path),
        )

    @staticmethod
    def calculate_entropy_delta(entropy_before: float, entropy_after: float) -> float:
        """Compute change in entropy between pre- and post-write telemetry."""
        return round(entropy_after - entropy_before, 4)

    @classmethod
    def is_anomalous(cls, entropy: float, threshold: float = ENTROPY_HIGH_THRESHOLD) -> bool:
        """Check if entropy exceeds the ransomware threat threshold."""
        return entropy >= threshold


# Module-level convenience functions
calculate_chunk_entropy = EntropyCalculator.calculate_chunk_entropy
calculate_file_entropy = EntropyCalculator.calculate_file_entropy
sample_file_chunks = EntropyCalculator.sample_file_chunks
analyze_file = EntropyCalculator.analyze_file
calculate_entropy_delta = EntropyCalculator.calculate_entropy_delta
is_anomalous = EntropyCalculator.is_anomalous
