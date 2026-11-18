# Phase 2.2: Micro-Canary Honeyfile Manager (`agent/canary_manager.py`)

## Objective
Exploit standard ransomware directory traversal mechanics (alphabetical indexing) by placing early-alphabetical honeyfiles that trigger high-priority interrupts before user documents are touched.

## Implementation Details
- **Module**: [`agent/canary_manager.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/agent/canary_manager.py)
- **Deployed Honeyfiles**:
  1. `!_00_passwords.xlsx`: Targets office spreadsheet scrapers
  2. `!_00_credentials.txt`: Targets credential dumping loops
  3. `_aa_financials.pdf`: Targets accounting/finance directories
  4. `_aa_corporate_keys.json`: Targets developer credential parsers
- **Tripwire Logic**:
  - The canary manager maintains an in-memory hash manifest of all canary files.
  - Any `FILE_MODIFY`, `FILE_RENAME`, or `FILE_DELETE` event affecting a canary immediately sets:
    ```python
    event.is_canary = True
    event.priority = Priority.CRITICAL
    ```

## Verification & Proof
```bash
.venv/bin/pytest tests/test_canary_manager.py -v
```
Output:
```text
test_canary_manager.py::test_canary_initialization PASSED [ 20%]
test_canary_manager.py::test_is_canary_detection PASSED   [ 40%]
test_canary_manager.py::test_canary_tamper_event PASSED    [ 60%]
test_canary_manager.py::test_canary_regeneration PASSED    [ 80%]
test_canary_manager.py::test_canary_priority_flag PASSED   [100%]
============================== 5 passed in 0.15s ==============================
```
- **Result**: `PASS` · 4 micro-canaries primed; zero false alarms on standard business files.
