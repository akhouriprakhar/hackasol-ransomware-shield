"""Unit tests for Offline Isolation Forest Anomaly Detector (TASK-3.1)."""

import time
import numpy as np
import pytest
from engine.anomaly_model import AnomalyDetector


def test_anomaly_model_initialization_and_latency():
    """Verify offline initialization and sub-50ms inference latency."""
    detector = AnomalyDetector(auto_train=True, n_estimators=30)
    assert detector.model is not None

    # Measure inference latency over 50 iterations
    latencies = []
    sample_vec = [0.1, 1.0, 0.0, 0.0]
    for _ in range(50):
        t0 = time.perf_counter()
        score = detector.score(sample_vec)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(dt_ms)

    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    # Mandated KPI: Inference must be < 50ms (average target < 5ms)
    assert max_latency < 50.0, f"Max inference latency {max_latency:.2f}ms exceeded 50ms!"
    assert avg_latency < 10.0, f"Average inference latency {avg_latency:.2f}ms too high!"


def test_anomaly_scoring_separation():
    """Verify normal file edits score < 0.3 and encrypted bursts score > 0.8."""
    detector = AnomalyDetector()

    # 1. Benign office/code file edit: small delta, slow velocity, no renames, no canary
    benign_vectors = [
        [0.05, 0.5, 0.0, 0.0],
        [0.20, 1.2, 0.0, 0.0],
        [-0.10, 0.8, 0.0, 0.0],
        [0.15, 2.0, 0.05, 0.0],
    ]
    for vec in benign_vectors:
        score = detector.score(vec)
        assert score < 0.30, f"Benign vector {vec} scored {score:.3f} >= 0.30"
        assert not detector.predict_is_anomalous(vec, threshold=0.65)

    # 2. Ransomware burst: high entropy jump, rapid velocity, mass rename, canary hit
    ransom_vectors = [
        [4.2, 35.0, 0.9, 1.0],
        [3.9, 45.0, 1.0, 0.0],
        [4.5, 60.0, 0.8, 1.0],
    ]
    for vec in ransom_vectors:
        score = detector.score(vec)
        assert score > 0.80, f"Ransom vector {vec} scored {score:.3f} <= 0.80"
        assert detector.predict_is_anomalous(vec, threshold=0.65)


def test_flexible_vector_shapes():
    """Verify detector handles 4-element, 5-element, and numpy array inputs seamlessly."""
    detector = AnomalyDetector()

    # 4-element list
    s1 = detector.score([0.1, 1.0, 0.0, 0.0])
    assert 0.0 <= s1 <= 1.0

    # 5-element list (including extra non-standard extension flag)
    s2 = detector.score([0.1, 1.0, 0.0, 0.0, 1.0])
    assert 0.0 <= s2 <= 1.0

    # 2D numpy array
    s3 = detector.score(np.array([[4.0, 30.0, 0.9, 1.0]]))
    assert s3 > 0.8


def test_model_serialization(tmp_path):
    """Verify model can be saved to disk and loaded without retraining."""
    model_file = tmp_path / "test_iso_forest.pkl"
    detector1 = AnomalyDetector(model_path=model_file, auto_train=True)
    score1 = detector1.score([4.0, 30.0, 0.8, 1.0])

    detector2 = AnomalyDetector(model_path=model_file, auto_train=False)
    score2 = detector2.score([4.0, 30.0, 0.8, 1.0])

    assert abs(score1 - score2) < 1e-4
