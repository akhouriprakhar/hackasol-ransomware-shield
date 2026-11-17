"""Unit tests for Composite Risk Arbiter & Deterministic XAI (TASK-3.2)."""

import time
import pytest
from backend.schemas import EventType, TelemetryEvent
from engine.anomaly_model import AnomalyDetector
from engine.explainability import DeterministicExplainer
from engine.risk_arbiter import RiskArbiter


def test_deterministic_explainer_breakdown():
    """Verify XAI attribution factors are deterministic and sum to 1.0."""
    factors = DeterministicExplainer.explain(
        is_canary=True,
        entropy_after=7.92,
        entropy_delta=4.4,
        write_velocity=30.0,
        rename_ratio=0.8,
        is_suspicious_ext=True,
        ml_score=0.91,
        top_k=3,
    )
    assert len(factors) == 3
    assert factors[0].factor == "CANARY_TRIPWIRE"
    total_weight = sum(f.weight for f in factors)
    assert abs(total_weight - 1.0) < 0.05, f"Factors sum {total_weight} != 1.0"


def test_benign_telemetry_low_risk():
    """Verify regular file modifications yield risk score < 30.0."""
    arbiter = RiskArbiter()

    event = TelemetryEvent(
        event_id="evt_benign_01",
        timestamp=time.time(),
        event_type=EventType.FILE_MODIFY,
        file_path="/tmp/test_workspace/document.txt",
        entropy_before=3.2,
        entropy_after=3.4,
        entropy_delta=0.2,
        pid=99991,
        process_name="code_editor",
        is_canary=False,
    )

    assessment = arbiter.evaluate_event(event)
    assert assessment.risk_score < 30.0
    assert not assessment.is_critical
    assert "CANARY_TRIPWIRE" not in assessment.triggered_rules


def test_canary_tripwire_critical_escalation():
    """Verify touching a micro-canary immediately breaches critical threshold >= 80.0."""
    arbiter = RiskArbiter()

    event = TelemetryEvent(
        event_id="evt_canary_01",
        timestamp=time.time(),
        event_type=EventType.FILE_MODIFY,
        file_path="/tmp/test_workspace/!_00_passwords.xlsx",
        entropy_before=3.5,
        entropy_after=4.1,
        entropy_delta=0.6,
        pid=88881,
        process_name="suspicious_proc",
        is_canary=True,
    )

    assessment = arbiter.evaluate_event(event)
    assert assessment.risk_score >= 80.0
    assert assessment.is_critical
    assert "CANARY_TRIPWIRE" in assessment.triggered_rules

    # Verify incident alert generation
    alert = arbiter.create_incident_alert(assessment, detection_latency_ms=12.5)
    assert alert.risk_score >= 80.0
    assert alert.offending_pid == 88881
    assert alert.status.value == "CONTAINED"
    assert len(alert.xai_breakdown) > 0


def test_encrypted_burst_breaches_80_within_3_files():
    """DoD: Verify risk score reaches >= 80 within <= 3 encrypted files."""
    arbiter = RiskArbiter()
    pid = 77771

    # Simulate 3 sequential encrypted file events with entropy > 7.5 and .locked rename
    events = [
        TelemetryEvent(
            event_id=f"evt_burst_{i}",
            timestamp=time.time() + (i * 0.05),
            event_type=EventType.FILE_RENAME,
            file_path=f"/sandbox_targets/file_{i}.txt.locked",
            entropy_before=3.4,
            entropy_after=7.92,
            entropy_delta=4.52,
            pid=pid,
            process_name="brac_sim",
            is_canary=False,
        )
        for i in range(1, 4)
    ]

    critical_reached = False
    files_to_breach = 0

    for i, event in enumerate(events, start=1):
        assessment = arbiter.evaluate_event(event)
        if assessment.is_critical:
            critical_reached = True
            files_to_breach = i
            break

    assert critical_reached, "Risk score failed to cross 80.0 threshold"
    assert files_to_breach <= 3, f"Threshold breach took {files_to_breach} files (limit: <= 3)"


def test_heuristic_failover_when_ml_fails(monkeypatch):
    """Verify RULES.md 4.2 failover to heuristics if ML detector throws exception."""
    arbiter = RiskArbiter()

    # Mock anomaly_detector.score to raise Exception
    def broken_score(*args, **kwargs):
        raise RuntimeError("Simulated ML engine crash")

    monkeypatch.setattr(arbiter.anomaly_detector, "score", broken_score)

    # Telemetry with high entropy surge should still trigger heuristic protection
    event = TelemetryEvent(
        event_id="evt_failover_01",
        timestamp=time.time(),
        event_type=EventType.FILE_RENAME,
        file_path="/sandbox_targets/financials.pdf.locked",
        entropy_before=3.1,
        entropy_after=7.95,
        entropy_delta=4.85,
        pid=66661,
        process_name="crypto_worker",
        is_canary=False,
    )

    assessment = arbiter.evaluate_event(event)
    assert assessment.ml_anomaly_score == 0.0
    # Heuristic scoring: high entropy (+40) + surge (+30) + suspicious ext (+25) = 95.0
    assert assessment.risk_score >= 80.0
    assert assessment.is_critical
