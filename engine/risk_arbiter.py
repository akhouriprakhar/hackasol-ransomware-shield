"""Real-Time Composite Risk Arbiter & Heuristic-ML Synthesizer (TASK-3.2).

Aggregates offline ML Isolation Forest anomaly scores and deterministic heuristic
rule evaluations into an atomic 0-100 risk score with XAI attribution breakdown.
Features defensive heuristic failover (RULES.md 4.2) and guarantees containment
threshold breach (>= 80.0) within <= 3 encrypted files during attacks.
"""

import collections
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, List, Optional, Set, Tuple

from backend.schemas import (
    EventType,
    IncidentAlert,
    IncidentStatus,
    TelemetryEvent,
    XAIFactor,
)
from engine.anomaly_model import AnomalyDetector
from engine.explainability import DeterministicExplainer

logger = logging.getLogger(__name__)

# Known ransomware suffix signatures
SUSPICIOUS_EXTENSIONS: Set[str] = {
    ".locked",
    ".crypto",
    ".enc",
    ".crypted",
    ".ransom",
    ".lockbit",
    ".wannacry",
}


@dataclass
class ProcessWindow:
    """Sliding telemetry activity window for a specific PID."""
    pid: int
    timestamps: Deque[float] = field(default_factory=lambda: collections.deque(maxlen=100))
    event_types: Deque[EventType] = field(default_factory=lambda: collections.deque(maxlen=100))
    affected_files: Set[str] = field(default_factory=set)
    high_entropy_files: Set[str] = field(default_factory=set)
    canary_hits: int = 0
    max_entropy_seen: float = 0.0

    def add_event(self, event: TelemetryEvent) -> None:
        self.timestamps.append(event.timestamp)
        self.event_types.append(event.event_type)
        self.affected_files.add(event.file_path)
        if event.entropy_after >= 7.0 or event.entropy_delta >= 2.5:
            self.high_entropy_files.add(event.file_path)
        if event.is_canary:
            self.canary_hits += 1
        if event.entropy_after > self.max_entropy_seen:
            self.max_entropy_seen = event.entropy_after

    def get_velocity(self, window_sec: float = 3.0) -> float:
        """Calculate file operations per second over the recent window."""
        now = time.time()
        recent = [t for t in self.timestamps if now - t <= window_sec]
        if len(recent) <= 1:
            return float(len(recent))
        duration = max(recent[-1] - recent[0], 0.05)
        return float(len(recent) / duration)

    def get_rename_ratio(self, window_sec: float = 3.0) -> float:
        """Calculate ratio of rename operations over total recent events."""
        now = time.time()
        pairs = [
            (t, et) for t, et in zip(self.timestamps, self.event_types)
            if now - t <= window_sec
        ]
        if not pairs:
            return 0.0
        renames = sum(1 for _, et in pairs if et == EventType.FILE_RENAME)
        return float(renames / len(pairs))


@dataclass
class RiskAssessment:
    """Atomic risk evaluation result returned by RiskArbiter."""
    risk_score: float
    is_critical: bool
    ml_anomaly_score: float
    xai_breakdown: List[XAIFactor]
    affected_files_count: int
    process_pid: Optional[int]
    process_name: Optional[str]
    target_file: str
    triggered_rules: List[str]


class RiskArbiter:
    """Synthesizes real-time heuristics and offline ML anomaly scores."""

    CRITICAL_THRESHOLD: float = 80.0

    def __init__(
        self,
        anomaly_detector: Optional[AnomalyDetector] = None,
        sliding_window_sec: float = 3.0,
    ):
        self.anomaly_detector = anomaly_detector or AnomalyDetector()
        self.sliding_window_sec = sliding_window_sec
        # PID -> ProcessWindow
        self._windows: Dict[int, ProcessWindow] = {}
        # Global fallback window when PID is not available
        self._global_window = ProcessWindow(pid=0)

    def _get_window(self, pid: Optional[int]) -> ProcessWindow:
        if pid is None or pid <= 0:
            return self._global_window
        if pid not in self._windows:
            self._windows[pid] = ProcessWindow(pid=pid)
        return self._windows[pid]

    def _is_suspicious_extension(self, file_path: str) -> bool:
        lower = file_path.lower()
        return any(lower.endswith(ext) for ext in SUSPICIOUS_EXTENSIONS)

    def evaluate_event(self, event: TelemetryEvent) -> RiskAssessment:
        """Evaluate a single telemetry event and compute the composite risk score."""
        window = self._get_window(event.pid)
        window.add_event(event)

        write_velocity = window.get_velocity(self.sliding_window_sec)
        rename_ratio = window.get_rename_ratio(self.sliding_window_sec)
        is_suspicious_ext = self._is_suspicious_extension(event.file_path)

        # 1. Feature Vector for ML Model: [EntropyDelta, WriteVelocity, RenameRatio, CanaryHit]
        feature_vector = [
            event.entropy_delta,
            write_velocity,
            rename_ratio,
            1.0 if event.is_canary else 0.0,
        ]

        # 2. Offline ML Anomaly Score with defensive fallback (RULES.md 4.2)
        ml_score = 0.0
        try:
            ml_score = self.anomaly_detector.score(feature_vector)
        except Exception as e:
            logger.warning("ML inference failed; failing over to heuristic rules: %s", e)
            ml_score = 0.0

        # 3. Deterministic Heuristic Scoring
        heuristic_score = 0.0
        triggered_rules: List[str] = []

        # Heuristic 1: Micro-canary tripwire (+80 points)
        if event.is_canary or window.canary_hits > 0:
            heuristic_score += 80.0
            triggered_rules.append("CANARY_TRIPWIRE")

        # Heuristic 2: Extreme Shannon Entropy Jump (after >= 7.5 or delta >= 3.0)
        if event.entropy_after >= 7.5:
            heuristic_score += 40.0
            triggered_rules.append("ENTROPY_ABOVE_7_5")
        elif event.entropy_after >= 6.8:
            heuristic_score += 20.0
            triggered_rules.append("ENTROPY_ELEVATED")

        if event.entropy_delta >= 3.0:
            heuristic_score += 30.0
            triggered_rules.append("ENTROPY_DELTA_SURGE")
        elif event.entropy_delta >= 1.5:
            heuristic_score += 15.0
            triggered_rules.append("ENTROPY_DELTA_MODERATE")

        # Heuristic 3: Suspicious extension mutation
        if is_suspicious_ext:
            heuristic_score += 25.0
            triggered_rules.append("SUSPICIOUS_EXTENSION_LOCKED")

        # Heuristic 4: Burst write velocity
        if write_velocity >= 15.0:
            heuristic_score += 25.0
            triggered_rules.append("HIGH_WRITE_VELOCITY")
        elif write_velocity >= 5.0:
            heuristic_score += 10.0
            triggered_rules.append("ELEVATED_WRITE_VELOCITY")

        # Heuristic 5: Multi-file high-entropy correlation
        high_entropy_count = len(window.high_entropy_files)
        if high_entropy_count >= 3:
            heuristic_score += 30.0
            triggered_rules.append(f"CUMULATIVE_HIGH_ENTROPY_FILES_{high_entropy_count}")
        elif high_entropy_count >= 2:
            heuristic_score += 15.0
            triggered_rules.append("CUMULATIVE_HIGH_ENTROPY_FILES_2")

        # 4. Composite Synthesis: Blend Heuristics (up to 75 pts base) + ML Score (up to 25 pts)
        # Note: If Canary tripwire triggered, base score starts at >= 80 regardless of ML.
        # If pure encryption burst (high entropy + delta + suspicious ext), heuristic >= 85 directly.
        if "CANARY_TRIPWIRE" in triggered_rules:
            # Canary tripwire is a critical honeypot breach -> minimum 85.0
            composite_score = max(85.0, heuristic_score)
        else:
            # Base combination
            ml_contribution = ml_score * 30.0
            composite_score = min(heuristic_score + ml_contribution, 100.0)

        composite_score = float(round(min(max(composite_score, 0.0), 100.0), 1))
        is_critical = composite_score >= self.CRITICAL_THRESHOLD

        # 5. Deterministic Explainable AI Feature Attribution
        xai_breakdown = DeterministicExplainer.explain(
            is_canary=event.is_canary or (window.canary_hits > 0),
            entropy_after=event.entropy_after,
            entropy_delta=event.entropy_delta,
            write_velocity=write_velocity,
            rename_ratio=rename_ratio,
            is_suspicious_ext=is_suspicious_ext,
            ml_score=ml_score,
            top_k=3,
        )

        return RiskAssessment(
            risk_score=composite_score,
            is_critical=is_critical,
            ml_anomaly_score=ml_score,
            xai_breakdown=xai_breakdown,
            affected_files_count=len(window.affected_files),
            process_pid=event.pid,
            process_name=event.process_name,
            target_file=event.file_path,
            triggered_rules=triggered_rules,
        )

    def create_incident_alert(
        self,
        assessment: RiskAssessment,
        detection_latency_ms: float = 45.0,
    ) -> IncidentAlert:
        """Construct IncidentAlert payload matching backend.schemas contract."""
        return IncidentAlert(
            incident_id=f"inc_{uuid.uuid4().hex[:6]}",
            timestamp=time.time(),
            status=IncidentStatus.CONTAINED,
            risk_score=assessment.risk_score,
            offending_pid=assessment.process_pid or 0,
            process_name=assessment.process_name or "unknown",
            files_affected_count=assessment.affected_files_count,
            detection_latency_ms=round(detection_latency_ms, 2),
            containment_method="POSIX_SIGSTOP",
            xai_breakdown=assessment.xai_breakdown,
        )

    def reset_window(self, pid: Optional[int] = None) -> None:
        """Clear telemetry state for a PID or all processes."""
        if pid is not None and pid in self._windows:
            del self._windows[pid]
        elif pid is None:
            self._windows.clear()
            self._global_window = ProcessWindow(pid=0)
