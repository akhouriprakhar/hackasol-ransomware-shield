"""AegisRansom-X FastAPI Backend Server & WebSocket Broadcast Hub (TASK-5.1 / TASK-5.2).

Provides:
1. WebSocket /ws/telemetry and /ws/alerts streaming real-time telemetry and incident alerts.
2. POST /api/simulator/start & POST /api/simulator/reset.
3. POST /api/incidents/{incident_id}/action (RESUME_SIGCONT, TERMINATE_SIGKILL, ROLLBACK_RESTORE).
4. GET /api/health & GET /api/v1/health returning active watcher status, ML model status, and protected PIDs.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.pipeline import AegisPipeline
from backend.routes import actions, incidents, simulator
from backend.ws_manager import ws_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aegis_backend")

# Global pipeline instance
pipeline = AegisPipeline()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan hook managing pipeline start, event loop binding, and shutdown."""
    loop = asyncio.get_running_loop()
    pipeline.set_event_loop(loop)
    pipeline.start()
    logger.info("AegisRansom-X backend initialized and pipeline active.")
    try:
        yield
    finally:
        pipeline.stop()
        logger.info("AegisRansom-X backend shut down cleanly.")


app = FastAPI(
    title="AegisRansom-X SOC Core",
    description="macOS Ransomware Pre-Encryption Containment & Offline ML Detection Hub",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for React Vite dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular routers
app.include_router(simulator.router)
app.include_router(actions.router)
app.include_router(incidents.router)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root status ping."""
    return {
        "service": "AegisRansom-X Core SOC Server",
        "status": "ONLINE",
        "runtime": "macOS Darwin ARM64",
    }


@app.get("/api/health")
@app.get("/api/v1/health")
async def health_check() -> Dict[str, Any]:
    """Health check returning active watcher status, loaded ML model status, and protected PIDs."""
    return pipeline.get_health_status()


# --- Real-Time WebSocket Streaming Endpoints ---


@app.websocket("/ws/telemetry")
async def ws_telemetry_endpoint(websocket: WebSocket):
    """Primary telemetry stream broadcasting TelemetryEvents and IncidentAlerts."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive receive loop
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.debug("WebSocket exception on /ws/telemetry: %s", e)
        await ws_manager.disconnect(websocket)


@app.websocket("/ws/alerts")
async def ws_alerts_endpoint(websocket: WebSocket):
    """Dedicated /ws/alerts channel streaming incident alerts & telemetry."""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.debug("WebSocket exception on /ws/alerts: %s", e)
        await ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
