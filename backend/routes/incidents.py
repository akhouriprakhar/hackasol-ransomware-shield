"""Incident & Telemetry Query Routes for AegisRansom-X (TASK-5.1).

Exposes:
- GET /api/incidents
- GET /api/incidents/{incident_id}
- GET /api/telemetry
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.schemas import IncidentAlert, TelemetryEvent

router = APIRouter(tags=["incidents"])


def get_pipeline():
    """Dependency injection placeholder; overridden in main.py."""
    from backend.main import pipeline
    return pipeline


@router.get("/api/incidents", response_model=List[IncidentAlert])
async def list_incidents(
    limit: int = Query(default=50, ge=1, le=200),
    pipeline=Depends(get_pipeline),
):
    """Fetch recent security incidents sorted newest first."""
    return pipeline.database.get_recent_incidents(limit=limit)


@router.get("/api/incidents/{incident_id}", response_model=IncidentAlert)
async def get_incident(
    incident_id: str,
    pipeline=Depends(get_pipeline),
):
    """Fetch specific incident by ID."""
    incident = pipeline.database.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return incident


@router.get("/api/telemetry", response_model=List[TelemetryEvent])
async def list_telemetry(
    limit: int = Query(default=100, ge=1, le=500),
    pipeline=Depends(get_pipeline),
):
    """Fetch recent filesystem telemetry events."""
    return pipeline.database.get_recent_telemetry(limit=limit)


@router.get("/api/incidents/{incident_id}/copilot")
async def get_incident_copilot(
    incident_id: str,
    pipeline=Depends(get_pipeline),
):
    """Fetch or generate Tier-2 AI Copilot briefing for an incident."""
    if incident_id.lower() == "latest":
        incident = pipeline._latest_incident or (
            pipeline.database.get_recent_incidents(1)[0]
            if pipeline.database.get_recent_incidents(1)
            else None
        )
    else:
        incident = pipeline.database.get_incident(incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="No incident found matching query")

    cached = pipeline.copilot.get_cached_narrative(incident.incident_id)
    if cached:
        return cached

    # Generate fallback/briefing asynchronously
    return await pipeline.copilot.analyze_incident_async(incident=incident)

