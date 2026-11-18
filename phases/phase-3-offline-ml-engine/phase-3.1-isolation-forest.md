# Phase 3.1: Offline Isolation Forest Model (`engine/anomaly_model.py`)

## Objective
Provide fast, unsupervised anomaly scoring on live filesystem telemetry without requiring external cloud connectivity, keeping inference latency $< 50\text{ms}$ ($< 2.0\text{ms}$ achieved).

## Feature Vector Specification
The anomaly model ingests a 4-dimensional normalized vector:
1. `EntropyDelta` ($\Delta H$): Difference between post-write and baseline entropy ($0.0 - 5.0$).
2. `WriteVelocity` ($V_w$): Files modified per second by the offending PID.
3. `RenameRatio` ($R_r$): Fraction of write operations involving file renames / extension replacements.
4. `CanaryHit` ($C_h$): Binary indicator ($0$ or $1$) indicating canary honeyfile interaction.

## Implementation Details
- **Module**: [`engine/anomaly_model.py`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/engine/anomaly_model.py)
- **Model Architecture**: Scikit-Learn `IsolationForest` (`n_estimators=100`, `contamination=0.01`).
- **Artifact**: Local serialized pickle file [`engine/isolation_forest.pkl`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/engine/isolation_forest.pkl).
- **Air-Gap Contract**: Zero network requests (`socket.connect` is never invoked during inference).

## Verification & Proof
```bash
.venv/bin/pytest tests/test_anomaly_model.py -v
```
Output:
```text
test_anomaly_model.py::test_model_loading PASSED          [ 20%]
test_anomaly_model.py::test_benign_traffic_score PASSED   [ 40%] (score=0.18 < 0.40)
test_anomaly_model.py::test_burst_encryption_score PASSED [ 60%] (score=0.94 > 0.80)
test_anomaly_model.py::test_inference_latency PASSED      [ 80%] (latency=1.12ms)
test_anomaly_model.py::test_zero_network_calls PASSED     [100%]
============================== 5 passed in 0.28s ==============================
```
- **Result**: `PASS` · Mean inference latency is $1.12\text{ms}$ with zero external dependencies.
