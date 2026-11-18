# Phase 1.4: Safe Benign Ransomware Activity Simulator (`simulator/brac_sim.py`)

## Objective
Implement a benign synthetic ransomware simulator strictly confined to `./sandbox_targets/` to simulate real-world high-velocity burst encryption without deploying live malware (Hack-a-Sol 5.0 Section 06/09 Compliance).

## Implementation Details
- **Simulator**: [`simulator/brac_sim.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/simulator/brac_sim.py)
  - Employs AES-256 (CBC mode) via `cryptography.hazmat` with random ephemeral session keys.
  - Renames encrypted files with the `.locked` extension.
  - Supports 3 simulation modes:
    - `BURST`: 0ms delay between files (maximum encryption speed).
    - `STEALTH`: 200ms delay between writes (low and slow evasion attempt).
    - `BENIGN`: Append-only low-entropy developer notes (zero encryption).
- **Safety Boundary**: [`simulator/safety.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/simulator/safety.py)
  - Hardcoded canonical path check:
    ```python
    target_abs = os.path.realpath(target_dir)
    sandbox_abs = os.path.realpath("./sandbox_targets")
    if not target_abs.startswith(sandbox_abs):
        raise SecurityViolationError("Aborting: Simulator restricted strictly to ./sandbox_targets/")
    ```

## Verification & Proof
```bash
.venv/bin/python simulator/brac_sim.py --dry-run
```
Output:
```text
[SAFETY CHECK] Hardcoded sandbox lock active: /Users/akhouriprakhar/Downloads/Hack-a-Sol 5.0/sandbox_targets
[DRY-RUN] Target count: 54 files. Safety verification: PASSED.
```
- **Automated Tests**: `tests/test_safety_and_generator.py` (5 tests passing).
- **Result**: `PASS` · Safe, realistic attack simulator with hardcoded host safeguards.
