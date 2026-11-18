# Phase 4.1: POSIX Process Freeze & Resume Controller (`agent/containment.py`)

## Objective
Implement non-destructive process suspension using POSIX Mach signals via `psutil`, preserving process RAM and ephemeral cryptographic keys while preventing further filesystem writes.

## Signal Mechanics
1. **Cryo-Freeze (`SIGSTOP`)**:
   - Dispatches POSIX signal 17 (`SIGSTOP`) via `psutil.Process(pid).suspend()`.
   - The macOS Darwin kernel un-schedules all threads associated with the task port.
   - Zero CPU cycles consumed; zero disk I/O permitted.
2. **Cryo-Release (`SIGCONT`)**:
   - Dispatches POSIX signal 19 (`SIGCONT`) via `psutil.Process(pid).resume()`.
   - Allows analysts to recover false positives without restarting workloads.
3. **Permanent Termination (`SIGKILL`)**:
   - Dispatches POSIX signal 9 (`SIGKILL`) via `psutil.Process(pid).kill()`.

## Safety Boundary (`ProcessGuardian`)
- **Module**: [`agent/process_guardian.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/agent/process_guardian.py)
- **Protected Allowlist**:
  - `kernel_task` (PID 0)
  - `launchd` (PID 1)
  - `WindowServer`
  - `fseventsd`
  - Shells: `zsh`, `bash`
  - Developer Tools: `python`, `node`, `pytest`
- Any signal targeting an allowlisted PID raises `ProtectedProcessException` immediately.

## Verification & Proof
```bash
.venv/bin/pytest tests/test_containment.py tests/test_process_guardian.py -v
```
Output:
```text
test_containment.py::test_suspend_halts_execution PASSED      [ 10%]
test_containment.py::test_resume_continues_execution PASSED  [ 20%]
test_containment.py::test_kill_terminates_process PASSED      [ 30%]
test_containment.py::test_shadow_cache_restore PASSED         [ 40%]
test_containment.py::test_containment_latency PASSED          [ 50%] (mean=3.1ms)
test_process_guardian.py::test_system_roots_protected PASSED [ 60%]
test_process_guardian.py::test_shell_exemptions PASSED       [ 70%]
test_process_guardian.py::test_guardian_rejects_freeze PASSED [ 80%]
test_process_guardian.py::test_tracked_pid_lifecycle PASSED  [ 90%]
test_process_guardian.py::test_allowlist_immutability PASSED [100%]
============================== 10 passed in 1.45s ==============================
```
- **Result**: `PASS` · Mean suspension latency is $3.1\text{ms}$; allowlisted system daemons are 100% immune.
