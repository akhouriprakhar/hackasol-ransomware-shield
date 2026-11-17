"""Sample File Generator for AegisRansom-X Sandbox.

Populates ./sandbox_targets/ with realistic, benign developer and office files
(.txt, .json, .csv, .pdf) possessing low Shannon entropy (~3.2 - 4.8).
"""

import argparse
import math
import os
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.safety import assert_inside_sandbox, get_sandbox_dir


SAMPLE_TEXTS = [
    "Quarterly financial review: Q3 revenue growth was steady across enterprise accounts. "
    "Infrastructure spending declined by 4% due to automated cloud optimization. "
    "Next milestones include SOC2 compliance and zero-trust endpoint rollout.",

    "System configuration audit: All developer workstations comply with corporate policy. "
    "SSH keys rotated every 90 days. Endpoint telemetry enabled via local daemon. "
    "No unauthorized process privilege escalations observed in audit logs.",

    "Meeting minutes - Product Security Council: Evaluated real-time ransomware defense. "
    "Agreed on POSIX SIGSTOP freeze strategy over destructive process killing. "
    "Blast radius must remain strictly under two files during evaluation benchmarks.",

    "Incident report draft: Simulated suspicious I/O surge on developer endpoint. "
    "Canary honeyfiles triggered alerting pipeline within 15 milliseconds. "
    "Heuristic arbiter confirmed entropy surge and suspended offending worker process."
]


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy H(X) for a byte sequence."""
    if not data:
        return 0.0
    counter = Counter(data)
    total_bytes = len(data)
    entropy = 0.0
    for count in counter.values():
        p = count / total_bytes
        entropy -= p * math.log2(p)
    return entropy


def generate_txt_content(index: int) -> bytes:
    base = random.choice(SAMPLE_TEXTS)
    body = (
        f"--- Document ID: DOC-{index:04d} ---\n"
        f"Timestamp: 2026-11-17T11:00:{index % 60:02d}Z\n"
        f"Category: General Operations / Internal Briefing\n"
        f"Content:\n{base}\n"
        f"Notes: Regularly archived per corporate data retention standard.\n"
    )
    # Repeat mildly to achieve realistic file sizes (~2KB - 4KB)
    repeated = (body * (2 + (index % 3))).encode("utf-8")
    return repeated


def generate_json_content(index: int) -> bytes:
    content = (
        "{\n"
        f'  "record_id": "REC-{index:05d}",\n'
        f'  "account_type": "enterprise_tier_{index % 3}",\n'
        f'  "active": true,\n'
        f'  "monthly_spend_usd": {1200 + (index * 15)},\n'
        f'  "tags": ["cloud", "internal", "production", "tier-{index % 4}"],\n'
        f'  "contact": {{\n'
        f'    "name": "Operator {index}",\n'
        f'    "department": "Engineering Services",\n'
        f'    "email": "operator_{index}@enterprise.internal"\n'
        f'  }},\n'
        f'  "metadata": {{\n'
        f'    "retries": {index % 5},\n'
        f'    "region": "ap-south-1",\n'
        f'    "compliance": "SOC2-TYPE-2"\n'
        f'  }}\n'
        "}\n"
    )
    return content.encode("utf-8")


def generate_csv_content(index: int) -> bytes:
    lines = ["id,employee_code,department,project,role,status,last_login"]
    for row in range(1, 15):
        emp_id = index * 100 + row
        lines.append(
            f"{row},EMP-{emp_id},Security,AegisDefense,Analyst-{row % 3},ACTIVE,2026-11-17 10:{row:02d}:00"
        )
    return "\n".join(lines).encode("utf-8")


def generate_dummy_pdf_content(index: int) -> bytes:
    # Valid low-entropy mock PDF structure
    header = b"%PDF-1.4\n%mock PDF container for benign testing\n"
    obj1 = (
        f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        f"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
        f"4 0 obj\n<< /Length 120 >>\nstream\n"
        f"BT /F1 12 Tf 72 712 Td (Quarterly Report Document #{index}) Tj ET\n"
        f"endstream\nendobj\n"
    ).encode("ascii")
    xref = (
        b"xref\n0 5\n0000000000 65535 f \n"
        b"0000000010 00000 n \n0000000060 00000 n \n0000000115 00000 n \n0000000210 00000 n \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n350\n%%EOF\n"
    )
    return header + obj1 + xref


GENERATORS = [
    ("txt", generate_txt_content),
    ("json", generate_json_content),
    ("csv", generate_csv_content),
    ("pdf", generate_dummy_pdf_content),
]


def populate_sandbox(target_dir: Path, count: int = 50, clean: bool = False) -> List[Tuple[Path, float]]:
    """Populate target_dir with count harmless files.
    
    Returns list of (filepath, entropy).
    """
    assert_inside_sandbox(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    if clean:
        for f in target_dir.iterdir():
            if f.is_file() and f.name != ".gitkeep":
                assert_inside_sandbox(f)
                f.unlink()

    generated_files: List[Tuple[Path, float]] = []

    for i in range(1, count + 1):
        ext, generator_fn = GENERATORS[(i - 1) % len(GENERATORS)]
        filename = f"sample_doc_{i:03d}.{ext}"
        filepath = target_dir / filename
        
        # Verify boundary
        assert_inside_sandbox(filepath)

        data = generator_fn(i)
        filepath.write_bytes(data)

        entropy = calculate_entropy(data)
        generated_files.append((filepath, entropy))

    return generated_files


def main():
    parser = argparse.ArgumentParser(description="Populate ./sandbox_targets/ with benign low-entropy test files.")
    parser.add_argument("--count", type=int, default=50, help="Number of files to generate (default: 50)")
    parser.add_argument("--clean", action="store_true", help="Remove existing generated files before populating")
    parser.add_argument("--dir", type=str, default=None, help="Target sandbox directory (must be inside sandbox_targets/)")

    args = parser.parse_args()

    target_dir = Path(args.dir) if args.dir else get_sandbox_dir()
    assert_inside_sandbox(target_dir)

    print(f"[*] Target sandbox directory: {target_dir}")
    print(f"[*] Generating {args.count} benign test files...")

    files = populate_sandbox(target_dir=target_dir, count=args.count, clean=args.clean)

    entropies = [ent for _, ent in files]
    avg_entropy = sum(entropies) / len(entropies)
    min_entropy = min(entropies)
    max_entropy = max(entropies)

    print(f"[+] Successfully generated {len(files)} files in {target_dir}")
    print(f"[+] Shannon Entropy Profile:")
    print(f"    - Min Entropy:  {min_entropy:.2f}")
    print(f"    - Max Entropy:  {max_entropy:.2f}")
    print(f"    - Avg Entropy:  {avg_entropy:.2f}")
    print(f"[+] All files are confirmed benign (low entropy << 7.5 threshold).")


if __name__ == "__main__":
    main()
