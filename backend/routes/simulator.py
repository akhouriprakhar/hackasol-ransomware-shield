"""Simulator Control Routes for AegisRansom-X (TASK-1.4 / TASK-5.1).

Exposes POST /api/simulator/start and POST /api/simulator/reset.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException

from backend.schemas import SimulatorStartRequest

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


def get_pipeline():
    """Dependency injection placeholder; overridden in main.py."""
    from backend.main import pipeline
    return pipeline


@router.post("/start")
async def start_simulator(
    req: SimulatorStartRequest = SimulatorStartRequest(),
    pipeline=Depends(get_pipeline),
) -> Dict[str, Any]:
    """Launch benign ransomware simulator inside sandbox_targets in burst/normal/stealth mode."""
    valid_modes = {"burst", "normal", "stealth", "benign"}
    if req.mode.lower() not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid simulation mode: '{req.mode}'. Must be one of {valid_modes}",
        )
    return pipeline.start_simulator(req)


@router.post("/reset")
async def reset_simulator(pipeline=Depends(get_pipeline)) -> Dict[str, Any]:
    """Reset sandbox_targets with fresh 50 benign files + micro-canary honeyfiles."""
    return pipeline.reset_sandbox()


@router.get("/files")
async def get_sandbox_files(pipeline=Depends(get_pipeline)):
    """Return inventory of files in sandbox_targets for live disk visualization."""
    return pipeline.get_sandbox_files()

