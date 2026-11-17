"""SQLite WAL Mode Audit Ledger for AegisRansom-X (TASK-5.1).

Stores telemetry events and contained security incidents locally with
WAL (Write-Ahead Logging) mode for concurrent high-velocity writes.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.schemas import (
    EventType,
    IncidentAlert,
    IncidentStatus,
    TelemetryEvent,
    XAIFactor,
)

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "aegis_audit.db"


class AuditLedger:
    """Thread-safe SQLite audit ledger with WAL mode."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection with WAL mode enabled."""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def init_db(self) -> None:
        """Initialize database tables and indexes."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    entropy_before REAL NOT NULL,
                    entropy_after REAL NOT NULL,
                    entropy_delta REAL NOT NULL,
                    pid INTEGER,
                    process_name TEXT,
                    is_canary INTEGER NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    status TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    offending_pid INTEGER NOT NULL,
                    process_name TEXT NOT NULL,
                    files_affected_count INTEGER NOT NULL,
                    detection_latency_ms REAL NOT NULL,
                    containment_method TEXT NOT NULL,
                    xai_breakdown TEXT NOT NULL
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_events (timestamp DESC);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents (timestamp DESC);"
            )
            conn.commit()

    def record_telemetry_event(self, event: TelemetryEvent) -> None:
        """Persist a single TelemetryEvent."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO telemetry_events (
                        event_id, timestamp, event_type, file_path,
                        entropy_before, entropy_after, entropy_delta,
                        pid, process_name, is_canary
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        event.event_id,
                        event.timestamp,
                        event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
                        event.file_path,
                        event.entropy_before,
                        event.entropy_after,
                        event.entropy_delta,
                        event.pid,
                        event.process_name,
                        1 if event.is_canary else 0,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error("Failed to persist telemetry event %s: %s", event.event_id, e)

    def record_incident(self, incident: IncidentAlert) -> None:
        """Persist a Security Incident."""
        try:
            xai_json = json.dumps([f.model_dump() for f in incident.xai_breakdown])
            status_val = incident.status.value if hasattr(incident.status, "value") else str(incident.status)
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO incidents (
                        incident_id, timestamp, status, risk_score,
                        offending_pid, process_name, files_affected_count,
                        detection_latency_ms, containment_method, xai_breakdown
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        incident.incident_id,
                        incident.timestamp,
                        status_val,
                        incident.risk_score,
                        incident.offending_pid,
                        incident.process_name,
                        incident.files_affected_count,
                        incident.detection_latency_ms,
                        incident.containment_method,
                        xai_json,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error("Failed to persist incident %s: %s", incident.incident_id, e)

    def update_incident_status(self, incident_id: str, new_status: IncidentStatus) -> bool:
        """Update incident status (e.g. RELEASED, RESTORED, TERMINATED)."""
        status_val = new_status.value if hasattr(new_status, "value") else str(new_status)
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "UPDATE incidents SET status = ? WHERE incident_id = ?;",
                    (status_val, incident_id),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            logger.error("Failed to update status for incident %s: %s", incident_id, e)
            return False

    def get_incident(self, incident_id: str) -> Optional[IncidentAlert]:
        """Fetch incident by ID."""
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT * FROM incidents WHERE incident_id = ?;",
                    (incident_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                factors_raw = json.loads(row["xai_breakdown"])
                factors = [XAIFactor(**f) for f in factors_raw]
                return IncidentAlert(
                    incident_id=row["incident_id"],
                    timestamp=row["timestamp"],
                    status=IncidentStatus(row["status"]),
                    risk_score=row["risk_score"],
                    offending_pid=row["offending_pid"],
                    process_name=row["process_name"],
                    files_affected_count=row["files_affected_count"],
                    detection_latency_ms=row["detection_latency_ms"],
                    containment_method=row["containment_method"],
                    xai_breakdown=factors,
                )
        except Exception as e:
            logger.error("Failed to fetch incident %s: %s", incident_id, e)
            return None

    def get_recent_incidents(self, limit: int = 50) -> List[IncidentAlert]:
        """Fetch recent incidents sorted newest first."""
        results: List[IncidentAlert] = []
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?;",
                    (limit,),
                )
                for row in cur.fetchall():
                    factors_raw = json.loads(row["xai_breakdown"])
                    factors = [XAIFactor(**f) for f in factors_raw]
                    results.append(
                        IncidentAlert(
                            incident_id=row["incident_id"],
                            timestamp=row["timestamp"],
                            status=IncidentStatus(row["status"]),
                            risk_score=row["risk_score"],
                            offending_pid=row["offending_pid"],
                            process_name=row["process_name"],
                            files_affected_count=row["files_affected_count"],
                            detection_latency_ms=row["detection_latency_ms"],
                            containment_method=row["containment_method"],
                            xai_breakdown=factors,
                        )
                    )
        except Exception as e:
            logger.error("Failed to fetch recent incidents: %s", e)
        return results

    def get_recent_telemetry(self, limit: int = 100) -> List[TelemetryEvent]:
        """Fetch recent telemetry events sorted newest first."""
        results: List[TelemetryEvent] = []
        try:
            with self._get_connection() as conn:
                cur = conn.execute(
                    "SELECT * FROM telemetry_events ORDER BY timestamp DESC LIMIT ?;",
                    (limit,),
                )
                for row in cur.fetchall():
                    results.append(
                        TelemetryEvent(
                            event_id=row["event_id"],
                            timestamp=row["timestamp"],
                            event_type=EventType(row["event_type"]),
                            file_path=row["file_path"],
                            entropy_before=row["entropy_before"],
                            entropy_after=row["entropy_after"],
                            entropy_delta=row["entropy_delta"],
                            pid=row["pid"],
                            process_name=row["process_name"],
                            is_canary=bool(row["is_canary"]),
                        )
                    )
        except Exception as e:
            logger.error("Failed to fetch recent telemetry: %s", e)
        return results

    def clear_all(self) -> None:
        """Purge all stored events and incidents (for testing/reset)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM telemetry_events;")
            conn.execute("DELETE FROM incidents;")
            conn.commit()
