"""Offline Scikit-Learn Isolation Forest Anomaly Detector (TASK-3.1).

Evaluates sliding telemetry feature vectors:
    X = [EntropyDelta, WriteVelocity, RenameRatio, CanaryHit]
Calculates calibrated anomaly score in [0.0, 1.0] in < 50ms (target < 2ms)
with 100% offline local inference (zero cloud/network calls).
"""

import os
import pickle
import time
from pathlib import Path
from typing import List, Optional, Tuple, Union
import numpy as np
from sklearn.ensemble import IsolationForest

MODEL_PATH = Path(__file__).resolve().parent / "isolation_forest.pkl"


class AnomalyDetector:
    """Offline Isolation Forest Anomaly Detector for filesystem telemetry."""

    FEATURE_NAMES = [
        "entropy_delta",
        "write_velocity",
        "rename_ratio",
        "canary_hit",
    ]

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        auto_train: bool = True,
        n_estimators: int = 50,
        random_state: int = 42,
    ):
        self.model_path = Path(model_path or MODEL_PATH)
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model: Optional[IsolationForest] = None
        self._min_score: float = -0.35
        self._max_score: float = 0.25

        if self.model_path.exists():
            try:
                self.load_model(self.model_path)
            except Exception:
                if auto_train:
                    self.train_and_save()
        elif auto_train:
            self.train_and_save()

    def _generate_synthetic_training_data(
        self,
        n_benign: int = 1500,
        n_anomaly: int = 250,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate realistic synthetic baseline and attack telemetry distributions."""
        rng = np.random.RandomState(self.random_state)

        # 1. Benign patterns (office docs, code edits, browsing, small temp writes)
        # Features: [EntropyDelta, WriteVelocity (ops/s), RenameRatio, CanaryHit]
        benign_entropy_delta = np.clip(rng.normal(loc=0.15, scale=0.4, size=n_benign), -1.5, 1.2)
        benign_velocity = np.clip(rng.exponential(scale=1.2, size=n_benign), 0.1, 5.0)
        benign_rename = np.clip(rng.beta(a=0.5, b=10.0, size=n_benign), 0.0, 0.2)
        benign_canary = np.zeros(n_benign, dtype=float)

        X_benign = np.column_stack([
            benign_entropy_delta,
            benign_velocity,
            benign_rename,
            benign_canary,
        ])

        # 2. Ransomware burst patterns (rapid AES encryption, .locked renames, canary hits)
        anom_entropy_delta = np.clip(rng.normal(loc=3.8, scale=0.8, size=n_anomaly), 2.2, 5.5)
        anom_velocity = np.clip(rng.normal(loc=35.0, scale=12.0, size=n_anomaly), 10.0, 100.0)
        anom_rename = np.clip(rng.uniform(low=0.6, high=1.0, size=n_anomaly), 0.5, 1.0)
        anom_canary = rng.choice([0.0, 1.0], size=n_anomaly, p=[0.4, 0.6])

        X_anomaly = np.column_stack([
            anom_entropy_delta,
            anom_velocity,
            anom_rename,
            anom_canary,
        ])

        X_train = np.vstack([X_benign, X_anomaly])
        y_train = np.hstack([np.ones(n_benign), -np.ones(n_anomaly)])
        return X_train, y_train

    def train(self, X: Optional[np.ndarray] = None) -> "AnomalyDetector":
        """Train IsolationForest on synthetic or provided telemetry feature vectors."""
        if X is None:
            X, _ = self._generate_synthetic_training_data()

        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=0.15,
            random_state=self.random_state,
            n_jobs=1,  # Keep low CPU footprint on Apple Silicon
        )
        self.model.fit(X)

        # Calibrate bounds for smooth [0.0, 1.0] mapping
        raw_scores = self.model.decision_function(X)
        self._min_score = float(np.percentile(raw_scores, 2))
        self._max_score = float(np.percentile(raw_scores, 98))
        if self._max_score <= self._min_score:
            self._max_score = self._min_score + 0.5

        return self

    def save_model(self, path: Optional[Union[str, Path]] = None) -> Path:
        """Serialize trained model to disk."""
        target_path = Path(path or self.model_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "min_score": self._min_score,
            "max_score": self._max_score,
            "feature_names": self.FEATURE_NAMES,
        }
        with open(target_path, "wb") as f:
            pickle.dump(payload, f)
        return target_path

    def load_model(self, path: Optional[Union[str, Path]] = None) -> None:
        """Load serialized model from disk."""
        target_path = Path(path or self.model_path)
        with open(target_path, "rb") as f:
            payload = pickle.load(f)
        self.model = payload["model"]
        self._min_score = payload.get("min_score", -0.35)
        self._max_score = payload.get("max_score", 0.25)

    def train_and_save(self) -> None:
        """Train baseline and persist model file."""
        self.train()
        self.save_model()

    def score(self, features: Union[List[float], np.ndarray]) -> float:
        """Calculate calibrated anomaly score in [0.0, 1.0].
        
        0.0 = completely normal/benign.
        1.0 = highly anomalous / ransomware burst.
        Inference latency is strictly < 50ms (typically < 2ms).
        """
        if self.model is None:
            self.train_and_save()

        vec = np.asarray(features, dtype=float)
        # Handle 4 or 5 feature inputs seamlessly (extract first 4 if 5 provided)
        if vec.ndim == 1:
            if len(vec) > 4:
                vec = vec[:4]
            vec = vec.reshape(1, -1)
        elif vec.ndim == 2 and vec.shape[1] > 4:
            vec = vec[:, :4]

        # Raw decision function: positive is inlier/normal, negative is outlier/anomalous
        raw_df = float(self.model.decision_function(vec)[0])

        # Calibrated normalized score:
        # Inliers (df >= 0.0) map smoothly into [0.0, 0.25]
        # Outliers (df < 0.0) map into [0.80, 1.00]
        if raw_df >= 0.0:
            denom = max(self._max_score, 0.05)
            scaled = min(raw_df / denom, 1.0)
            return float(np.clip(0.25 * (1.0 - scaled), 0.0, 0.29))
        else:
            denom = max(abs(self._min_score), 0.05)
            scaled = min(abs(raw_df) / denom, 1.0)
            return float(np.clip(0.80 + (0.20 * scaled), 0.81, 1.0))

    def predict_is_anomalous(self, features: Union[List[float], np.ndarray], threshold: float = 0.65) -> bool:
        """Return True if anomaly score meets or exceeds threshold."""
        return self.score(features) >= threshold
