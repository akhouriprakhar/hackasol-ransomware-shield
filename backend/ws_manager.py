"""WebSocket Alert & Telemetry Broadcaster for AegisRansom-X (TASK-5.2).

Streams live TelemetryEvent and IncidentAlert payloads to connected SOC clients
with thread-safe non-blocking broadcast and connection lifecycle management.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Set, Union
from fastapi import WebSocket, WebSocketDisconnect

from backend.schemas import IncidentAlert, TelemetryEvent

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts telemetry / alerts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket client."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info("WebSocket client connected. Active clients: %d", len(self.active_connections))

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected client."""
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info("WebSocket client disconnected. Active clients: %d", len(self.active_connections))

    @property
    def client_count(self) -> int:
        return len(self.active_connections)

    async def broadcast_json(self, payload: Dict[str, Any]) -> None:
        """Broadcast JSON dictionary to all connected clients."""
        if not self.active_connections:
            return

        dead_connections: List[WebSocket] = []
        message_str = json.dumps(payload)

        async with self._lock:
            clients = list(self.active_connections)

        for connection in clients:
            try:
                await connection.send_text(message_str)
            except (WebSocketDisconnect, RuntimeError, ConnectionResetError) as e:
                logger.debug("Client socket dead during send: %s", e)
                dead_connections.append(connection)
            except Exception as e:
                logger.warning("Unexpected error broadcasting to client: %s", e)
                dead_connections.append(connection)

        if dead_connections:
            async with self._lock:
                for dead in dead_connections:
                    self.active_connections.discard(dead)

    async def broadcast_telemetry(self, event: TelemetryEvent) -> None:
        """Broadcast live TelemetryEvent payload to clients."""
        payload = event.model_dump()
        payload["type"] = "telemetry"
        await self.broadcast_json(payload)

    async def broadcast_incident(self, incident: IncidentAlert) -> None:
        """Broadcast live IncidentAlert payload to clients."""
        payload = incident.model_dump()
        payload["type"] = "incident"
        await self.broadcast_json(payload)

    async def broadcast_copilot(self, payload: Dict[str, Any]) -> None:
        """Broadcast Tier-2 Copilot narrative chunk or completed briefing."""
        data = dict(payload)
        data["type"] = "copilot"
        await self.broadcast_json(data)



# Global singleton broadcaster instance
ws_manager = ConnectionManager()
