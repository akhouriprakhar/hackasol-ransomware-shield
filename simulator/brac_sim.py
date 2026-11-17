"""Benign Ransomware Activity Simulator (BRAC-Sim).

Simulates rapid ransomware-like AES encryption, extension renaming (.locked),
and high entropy spikes strictly confined to ./sandbox_targets/.

HARD SAFETY INTERLOCK:
Under no circumstances will this tool encrypt, rename, or delete any file
outside the canonical ./sandbox_targets/ directory. All paths are validated
with assert_inside_sandbox().
"""

import argparse
import math
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.safety import (
    assert_inside_sandbox,
    get_sandbox_dir,
    SandboxViolationError,
)

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class SimSpeedMode(str, Enum):
    BURST = "burst"      # Zero delay between files (maximum I/O velocity)
    NORMAL = "normal"    # 50ms delay between files
    STEALTH = "stealth"  # 200ms delay between files


@dataclass
class EncryptionResult:
    original_path: Path
    encrypted_path: Path
    original_size: int
    encrypted_size: int
    entropy_before: float
    entropy_after: float
    duration_ms: float
    success: bool
    error: Optional[str] = None


def calculate_shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy H(X) = -sum(P(x) * log2(P(x)))."""
    if not data:
        return 0.0
    counter = Counter(data)
    total = len(data)
    entropy = 0.0
    for count in counter.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def aes_encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Encrypt byte buffer using AES-256-CBC with PKCS7 padding."""
    if HAS_CRYPTOGRAPHY:
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        # Prepend IV and magic header for identification
        return b"AEGIS_LOCKED:" + iv + ciphertext
    else:
        # Fallback high-entropy pseudo-AES stream generator
        iv = os.urandom(16)
        keystream = (key + iv) * (len(data) // 48 + 1)
        xored = bytes(b ^ k for b, k in zip(data, keystream[:len(data)]))
        return b"AEGIS_LOCKED:" + iv + xored


class BenignRansomwareSimulator:
    """Safely simulates ransomware encryption patterns on test sandbox files."""

    def __init__(
        self,
        target_dir: Optional[Path] = None,
        extension: str = ".locked",
        speed_mode: SimSpeedMode = SimSpeedMode.NORMAL,
        custom_delay_sec: Optional[float] = None,
        dry_run: bool = False,
        max_files: Optional[int] = None,
    ):
        # Strict boundary validation
        raw_target = Path(target_dir) if target_dir else get_sandbox_dir()
        self.target_dir = assert_inside_sandbox(raw_target)

        self.extension = extension if extension.startswith(".") else f".{extension}"
        self.speed_mode = speed_mode
        self.dry_run = dry_run
        self.max_files = max_files
        self.key = os.urandom(32)  # 256-bit ephemeral key

        if custom_delay_sec is not None:
            self.delay_sec = max(0.0, custom_delay_sec)
        elif speed_mode == SimSpeedMode.BURST:
            self.delay_sec = 0.0
        elif speed_mode == SimSpeedMode.STEALTH:
            self.delay_sec = 0.20
        else:
            self.delay_sec = 0.05

        self.results: List[EncryptionResult] = []
        self.aborted = False

    def discover_eligible_files(self) -> List[Path]:
        """Find non-locked files strictly within sandbox_targets."""
        assert_inside_sandbox(self.target_dir)
        eligible: List[Path] = []

        for entry in sorted(self.target_dir.iterdir()):
            if entry.is_file():
                # Skip .gitkeep and already locked files
                if entry.name == ".gitkeep" or entry.name.endswith(self.extension):
                    continue
                # Double-check safety interlock for each file
                assert_inside_sandbox(entry)
                eligible.append(entry)

        if self.max_files is not None and self.max_files > 0:
            eligible = eligible[:self.max_files]

        return eligible

    def encrypt_single_file(self, file_path: Path) -> EncryptionResult:
        """Encrypt a single file inside sandbox_targets and append .locked."""
        # Enforce boundary
        assert_inside_sandbox(file_path)

        t_start = time.perf_counter()
        original_data = file_path.read_bytes()
        entropy_before = calculate_shannon_entropy(original_data)

        # Encrypt in memory
        encrypted_data = aes_encrypt_bytes(original_data, self.key)
        entropy_after = calculate_shannon_entropy(encrypted_data)

        target_locked_path = file_path.with_name(file_path.name + self.extension)
        assert_inside_sandbox(target_locked_path)

        if not self.dry_run:
            # Atomic replacement: write to .locked and unlink original
            target_locked_path.write_bytes(encrypted_data)
            try:
                file_path.unlink()
            except OSError:
                pass

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        return EncryptionResult(
            original_path=file_path,
            encrypted_path=target_locked_path,
            original_size=len(original_data),
            encrypted_size=len(encrypted_data),
            entropy_before=entropy_before,
            entropy_after=entropy_after,
            duration_ms=duration_ms,
            success=True,
        )

    def run(self) -> List[EncryptionResult]:
        """Execute the simulation across discovered files."""
        assert_inside_sandbox(self.target_dir)
        files = self.discover_eligible_files()
        self.results.clear()

        pid = os.getpid()
        print(f"=================================================================")
        print(f"[*] BRAC-Sim [PID: {pid}] - Benign Ransomware Activity Simulator")
        print(f"[*] Target Directory: {self.target_dir}")
        print(f"[*] Mode: {self.speed_mode.value.upper()} (Delay: {self.delay_sec:.3f}s)")
        print(f"[*] Dry-Run Mode: {'ENABLED (No disk modifications)' if self.dry_run else 'DISABLED (Live encryption)'}")
        print(f"[*] Discovered Eligible Targets: {len(files)} files")
        print(f"=================================================================\n")

        if not files:
            print("[!] No eligible target files found. Run simulator/sample_generator.py first.")
            return self.results

        sim_start_time = time.perf_counter()

        for idx, target_file in enumerate(files, start=1):
            if self.aborted:
                print(f"[!] Simulation aborted at file {idx}/{len(files)}.")
                break

            try:
                res = self.encrypt_single_file(target_file)
                self.results.append(res)

                elapsed_total = time.perf_counter() - sim_start_time
                velocity = len(self.results) / max(0.001, elapsed_total)

                status_tag = "[DRY-RUN]" if self.dry_run else "[LOCKED]"
                print(
                    f"{status_tag} ({idx:03d}/{len(files):03d}) "
                    f"{target_file.name} -> {res.encrypted_path.name} | "
                    f"H(x): {res.entropy_before:.2f} -> {res.entropy_after:.2f} | "
                    f"Latency: {res.duration_ms:.2f}ms | Rate: {velocity:.1f} f/s"
                )

                if self.delay_sec > 0:
                    time.sleep(self.delay_sec)

            except SandboxViolationError as sve:
                print(f"[FATAL SAFETY INTERLOCK] {sve}")
                self.aborted = True
                raise
            except Exception as e:
                print(f"[ERROR] Failed to encrypt {target_file.name}: {e}")

        total_time = time.perf_counter() - sim_start_time
        print(f"\n=================================================================")
        print(f"[+] Simulation Completed.")
        print(f"[+] Total Files Processed: {len(self.results)}")
        print(f"[+] Total Elapsed Time:   {total_time:.3f} seconds")
        if self.results:
            avg_entropy_before = sum(r.entropy_before for r in self.results) / len(self.results)
            avg_entropy_after = sum(r.entropy_after for r in self.results) / len(self.results)
            print(f"[+] Mean Entropy Before:  {avg_entropy_before:.2f}")
            print(f"[+] Mean Entropy After:   {avg_entropy_after:.2f} (High Entropy Jump!)")
        print(f"=================================================================\n")

        return self.results


def main():
    parser = argparse.ArgumentParser(description="BRAC-Sim: Benign Ransomware Activity Simulator for macOS Containment Demo.")
    parser.add_argument("--dir", type=str, default=None, help="Target sandbox directory (must be strictly inside sandbox_targets/)")
    parser.add_argument("--mode", type=str, choices=["burst", "normal", "stealth"], default="normal", help="Simulation speed profile")
    parser.add_argument("--delay", type=float, default=None, help="Custom sleep delay in seconds between files")
    parser.add_argument("--extension", type=str, default=".locked", help="Target mutated extension (default: .locked)")
    parser.add_argument("--max-files", type=int, default=None, help="Limit maximum files to encrypt")
    parser.add_argument("--dry-run", action="store_true", help="Simulate encryption and entropy calculation without modifying disk")

    args = parser.parse_args()

    try:
        speed_mode = SimSpeedMode(args.mode)
        sim = BenignRansomwareSimulator(
            target_dir=Path(args.dir) if args.dir else None,
            extension=args.extension,
            speed_mode=speed_mode,
            custom_delay_sec=args.delay,
            dry_run=args.dry_run,
            max_files=args.max_files,
        )
        sim.run()
    except SandboxViolationError as sve:
        print(f"[FATAL] Safety interlock triggered: {sve}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[!] Simulation interrupted by user.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
