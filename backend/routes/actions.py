"""Analyst Action Routes for AegisRansom-X (TASK-5.3).

Exposes:
- POST /api/incidents/{incident_id}/action
- POST /api/v1/actions
Supporting RESUME_SIGCONT, TERMINATE_SIGKILL, and ROLLBACK_RESTORE.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException

from backend.schemas import ActionRequest, AnalystAction, IncidentActionRequest

router = APIRouter(tags=["actions"])


def get_pipeline():
    """Dependency injection placeholder; overridden in main.py."""
    from backend.main import pipeline
    return pipeline


@router.post("/api/incidents/{incident_id}/action")
async def execute_incident_action(
    incident_id: str,
    req: IncidentActionRequest,
    pipeline=Depends(get_pipeline),
) -> Dict[str, Any]:
    """Execute analyst action on an incident: RESUME_SIGCONT, TERMINATE_SIGKILL, or ROLLBACK_RESTORE."""
    result = pipeline.execute_action(incident_id=incident_id, action=req.action)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.post("/api/v1/actions")
async def execute_action_v1(
    req: ActionRequest,
    pipeline=Depends(get_pipeline),
) -> Dict[str, Any]:
    """Analyst action dispatch conforming to ARCHITECTURE.md Section 3.3."""
    result = pipeline.execute_action(incident_id=req.incident_id, action=req.action)
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
