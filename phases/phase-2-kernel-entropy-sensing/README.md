# Phase 2: macOS Endpoint Sensing & Chunked Shannon Entropy

> **PHASE STATUS**: `COMPLETED & VERIFIED`  
> **SCOPE**: Sub-2ms 4KB Shannon entropy calculus, micro-canary honeyfiles, and Apple Silicon FSEvents watcher.

---

## Executive Summary

Phase 2 builds the real-time endpoint telemetry sensor for AegisRansom-X. It implements sub-2ms Shannon entropy evaluation on 4KB file slices, deploys early alphabetical canary honeyfiles, and binds to the macOS Apple Silicon Darwin kernel through the native `FSEvents` event loop.

---

## Sub-Phase Breakdown

1. [**Phase 2.1: 4KB Chunk Shannon Entropy Calculator**](./phase-2.1-shannon-entropy.md)
   - Math: Fast byte-frequency calculus on 4KB head and tail buffers.
   - Latency: $< 1.8\text{ms}$ calculation speed (vs. $> 50\text{ms}$ full file reads).
   - Cutoff: $H(X) \ge 7.50$ flag for encrypted high-entropy buffers.
2. [**Phase 2.2: Micro-Canary Honeyfile Manager**](./phase-2.2-micro-canaries.md)
   - Provisioned alphabetical tripwires: `!_00_passwords.xlsx`, `_aa_financials.pdf`, `!_00_credentials.txt`, `_aa_corporate_keys.json`.
   - Tamper Detection: Modification or rename immediately raises a high-priority interrupt flag.
3. [**Phase 2.3: macOS Filesystem Listener (FSEvents)**](./phase-2.3-fsevents-watcher.md)
   - Hooked `watchdog` to native macOS `FSEvents` daemon.
   - Non-blocking thread-safe event queue dispatching telemetry in $< 20\text{ms}$.

---

## Verification Evidence
- `pytest tests/test_entropy.py` (4 tests passing, benchmark $< 1.8\text{ms}$).
- `pytest tests/test_canary_manager.py` (5 tests passing).
- `pytest tests/test_watcher.py` (5 tests passing).
