# Phase 1.3: Sandbox Workspace & Benign File Generator

## Objective
Generate a realistic corporate directory structure populated with typical business documents having natural low-entropy profiles ($3.0 - 5.0$) to establish the baseline for ransomware detection.

## Implementation Details
- **Target Directory**: [`./sandbox_targets/`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/sandbox_targets/)
- **Generator Script**: [`simulator/sample_generator.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/simulator/sample_generator.py)
  - Creates 50 business files across standard extensions:
    - 20 text documents (`.txt`): Corporate policies, quarterly reviews, employee guidelines
    - 10 JSON records (`.json`): Customer records, configuration manifests
    - 10 CSV tables (`.csv`): Payroll entries, sales transactions
    - 10 mock PDF buffers (`.pdf`): Formatted document headers and report text
  - Computes baseline Shannon entropy: Mean baseline $H(X) \approx 3.42$

## Verification & Proof
```bash
.venv/bin/python simulator/sample_generator.py
```
Output:
```text
Generated 50 sample files in ./sandbox_targets. Average Shannon Entropy: 3.45 / 8.00
```
- **Result**: `PASS` · 50 diverse business documents ready for telemetry monitoring.
