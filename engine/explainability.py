"""Deterministic Explainable AI (XAI) Feature Attribution (TASK-3.2).

Computes deterministic, local feature attribution weights without any LLM
dependencies. Output strictly conforms to backend.schemas.XAIFactor contract
and ARCHITECTURE.md specifications (< 5ms computation latency).
"""

from typing import Dict, List, Optional
from backend.schemas import XAIFactor


class DeterministicExplainer:
    """Calculates deterministic explainability signal contributions and weights."""

    # Base factor priority scores when triggered
    FACTOR_CANARY = "CANARY_TRIPWIRE"
    FACTOR_ENTROPY_ABOVE_7_5 = "ENTROPY_JUMP_ABOVE_7_5"
    FACTOR_ENTROPY_DELTA = "ENTROPY_DELTA_HIGH"
    FACTOR_WRITE_VELOCITY = "WRITE_VELOCITY"
    FACTOR_SUSPICIOUS_EXT = "SUSPICIOUS_EXTENSION"
    FACTOR_ML_ANOMALY = "ML_ISOLATION_FOREST_ANOMALY"
    FACTOR_RAPID_RENAME = "RAPID_RENAME_BURST"

    @classmethod
    def explain(
        cls,
        is_canary: bool = False,
        entropy_after: float = 0.0,
        entropy_delta: float = 0.0,
        write_velocity: float = 0.0,
        rename_ratio: float = 0.0,
        is_suspicious_ext: bool = False,
        ml_score: float = 0.0,
        top_k: int = 3,
    ) -> List[XAIFactor]:
        """Generate normalized feature attribution factors ranked by weight.
        
        Args:
            is_canary: True if honeyfile canary was touched.
            entropy_after: Post-event 4KB Shannon entropy [0.0 - 8.0].
            entropy_delta: Entropy shift (after - before).
            write_velocity: File operations per second.
            rename_ratio: Ratio or frequency of file rename mutations.
            is_suspicious_ext: True if file was renamed to ransomware suffix (.locked, etc.).
            ml_score: Isolation Forest anomaly score [0.0 - 1.0].
            top_k: Number of top factors to return (defaults to 3).
            
        Returns:
            List of XAIFactor instances with weights normalized to sum to 1.0.
        """
        raw_weights: Dict[str, float] = {}

        # 1. Canary hit (highest severity honeypot trigger)
        if is_canary:
            raw_weights[cls.FACTOR_CANARY] = 0.85

        # 2. Entropy above critical threshold (7.5)
        if entropy_after >= 7.5:
            # Scale from 7.5 to 8.0 -> 0.40 to 0.70
            excess = min(entropy_after - 7.5, 0.5) / 0.5
            raw_weights[cls.FACTOR_ENTROPY_ABOVE_7_5] = 0.45 + (0.25 * excess)
        elif entropy_delta >= 2.0:
            raw_weights[cls.FACTOR_ENTROPY_DELTA] = min(0.50, 0.20 + (entropy_delta / 8.0))

        # 3. Suspicious extension (.locked, etc.)
        if is_suspicious_ext:
            raw_weights[cls.FACTOR_SUSPICIOUS_EXT] = 0.40

        # 4. Write Velocity (rapid burst)
        if write_velocity >= 5.0:
            # Scale between 5.0 and 50.0 ops/sec
            vel_scaled = min(write_velocity / 50.0, 1.0)
            raw_weights[cls.FACTOR_WRITE_VELOCITY] = 0.15 + (0.35 * vel_scaled)

        # 5. Rapid rename burst
        if rename_ratio >= 0.3:
            raw_weights[cls.FACTOR_RAPID_RENAME] = 0.15 + (0.30 * min(rename_ratio, 1.0))

        # 6. ML Isolation Forest Anomaly
        if ml_score >= 0.5:
            raw_weights[cls.FACTOR_ML_ANOMALY] = 0.10 + (0.40 * ml_score)

        # Fallback if no specific threshold triggered (e.g. benign activity)
        if not raw_weights:
            if ml_score > 0.0:
                raw_weights[cls.FACTOR_ML_ANOMALY] = ml_score
            else:
                raw_weights["BASELINE_NORMAL_ACTIVITY"] = 1.0

        # Sort descending by raw contribution
        sorted_factors = sorted(raw_weights.items(), key=lambda item: item[1], reverse=True)
        top_factors = sorted_factors[:top_k]

        total_weight = sum(w for _, w in top_factors)
        if total_weight <= 0.0:
            total_weight = 1.0

        factors = [
            XAIFactor(
                factor=factor_name,
                weight=round(weight / total_weight, 2),
            )
            for factor_name, weight in top_factors
        ]

        # Re-normalize to guarantee exact sum of 1.00 for clean UI presentation
        weights_sum = sum(f.weight for f in factors)
        if factors and weights_sum != 1.0 and abs(weights_sum - 1.0) < 0.05:
            # Adjust the highest weight by the residual rounding diff
            diff = round(1.0 - weights_sum, 2)
            factors[0] = XAIFactor(
                factor=factors[0].factor,
                weight=round(factors[0].weight + diff, 2),
            )

        return factors
