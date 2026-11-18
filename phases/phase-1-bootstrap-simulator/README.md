# Phase 1: Environment Bootstrap & Safe Ransomware Simulator

> **PHASE STATUS**: `COMPLETED & VERIFIED`  
> **SCOPE**: Base workspace, virtual environment, sandboxed target generation, and benign ransomware simulator.

---

## Executive Summary

Phase 1 establishes the clean-room foundation for AegisRansom-X. It implements the isolated development environment, builds the synthetic business file generator, and constructs the safe benign ransomware simulator (`simulator/brac_sim.py`) strictly conforming to Hack-a-Sol 5.0 Rulebook Section 06/09 (Zero Live Malware, 100% hardcoded sandbox boundary).

---

## Sub-Phase Breakdown

1. [**Phase 1.1: Git Repository Initialization & Hygiene**](./phase-1.1-git-init.md)
   - Git repository initialized on `main` branch.
   - Hardened `.gitignore` protecting `.venv`, `__pycache__`, `node_modules`, `.DS_Store`, and temporary `.locked` files.
2. [**Phase 1.2: Python Virtual Environment & Dependency Lock**](./phase-1.2-virtual-env.md)
   - Python 3.9+ `.venv` setup with pinned `requirements.txt`.
   - Verified imports: `watchdog`, `psutil`, `scikit-learn`, `numpy`, `fastapi`, `uvicorn`, `pydantic`, `pytest`.
3. [**Phase 1.3: Sandbox Workspace & Benign File Generator**](./phase-1.3-sandbox-generator.md)
   - Created `./sandbox_targets/` workspace.
   - Built `simulator/sample_generator.py` populating 50 low-entropy sample files (`.txt`, `.json`, `.csv`, `.pdf` buffers, baseline $H(X) \approx 3.42$).
4. [**Phase 1.4: Safe Benign Ransomware Activity Simulator**](./phase-1.4-ransomware-sim.md)
   - Built `simulator/brac_sim.py` and `simulator/safety.py`.
   - AES-256 in-memory key generation and `.locked` mutation engine.
   - Hardcoded path interlock: strictly aborts if execution targets any path outside `./sandbox_targets/`.

---

## Verification Evidence
- `pytest tests/test_safety_and_generator.py` passing cleanly (100%).
- Dry-run validation confirms non-sandbox targets are strictly rejected with `SecurityViolationError`.
