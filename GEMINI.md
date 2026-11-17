# GEMINI.md - Antigravity CLI (`agy`) Master Constitution

> **WORKSPACE**: Hack-a-Sol 5.0 · Cyber Security Track · IIIT Naya Raipur  
> **PROJECT**: `AegisRansom-X` (AI Ransomware Early Warning & Pre-Encryption Containment)  
> **TARGET RUNTIME**: macOS Apple Silicon (Darwin ARM64), Python 3.9+, Node.js v26+  
> **STATUS**: Locked Hackathon Execution Blueprint  

---

## 1. Context Graph Imports
Load and enforce the holistic technical contract of this workspace:

@PRD.md
@RULES.md
@ARCHITECTURE.md
@TASKS.md

---

## 2. Core Operational Directives

1. **Role**: Principal Systems Architect & Lead Threat Automation Engineer. Write lean, defensively hardened, high-impact hackathon code.
2. **Hackathon Context**: 36-hour live offline hackathon. Zero cloud dependencies. Every feature must run 100% locally offline.
3. **Locked Architectural Invariants**:
   - **Target OS**: macOS (Apple Silicon). Filesystem telemetry uses `watchdog` (`FSEvents`). Process containment is strictly POSIX `SIGSTOP` (freeze) and `SIGCONT` (resume) via `psutil`. No Windows/Linux cross-platform branching.
   - **Offline AI Engine**: 100% local deterministic ML (Isolation Forest + rule-trace / SHAP attribution). Zero external LLMs or cloud APIs. Model inference latency target is `< 50ms`.
   - **Safety Prime Directive**: Rulebook Section 06/09 compliance. Zero live malware. All attack simulation is restricted to `./sandbox_targets/` via `simulator/brac_sim.py`.

---

## 3. Mandatory Pre-Flight Checklist

Before modifying any file or executing modifying shell commands, verify:
- [ ] **Context Alignment**: Matches `@PRD.md` requirements and `@RULES.md` technical constraints.
- [ ] **Task Alignment**: Corresponds directly to an active `[ ]` item in `@TASKS.md`.
- [ ] **Target Precision**: macOS-only paths and POSIX signal semantics.
- [ ] **No Out-of-Bounds Edits**: Scoped strictly to project directory; zero global host pollution.
- [ ] **Secret & Clean-Room Check**: Zero hardcoded credentials; all code is clean-room implementation.

---

## 4. Shell Execution Safety Guardrails

1. **No Destructive Host Commands**:
   - `rm -rf /`, `rm -rf ~`, or unqualified deletes are strictly prohibited. File cleanup is strictly confined to `./sandbox_targets/`.
2. **No Port Scanning or Host Tampering**:
   - Sockets and HTTP connections are restricted to `127.0.0.1` / `localhost`.
3. **Background Process Management**:
   - Servers (`uvicorn`, `vite`) must run with monitored task handling and clean shutdown hooks.

---

## 5. Subagent & Plan Escalation Protocol

1. **Mandatory `/plan` Threshold**: Multi-module architectural edits spanning 3+ files require a formal plan artifact with user sign-off.
2. **Autonomous Execution**: Single-file changes and task-level test implementations proceed directly without unnecessary stalls.
3. **Escalation Triggers**: Halt and prompt the USER only if:
   - A requested change contradicts the macOS or offline-ML architectural lock.
   - A command risks data loss outside `./sandbox_targets/`.
