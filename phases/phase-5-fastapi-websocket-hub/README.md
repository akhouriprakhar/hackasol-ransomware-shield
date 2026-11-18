# Phase 5: FastAPI Server & Real-Time WebSocket Hub

> **PHASE STATUS**: `COMPLETED & VERIFIED`  
> **SCOPE**: Asynchronous FastAPI server, SQLite WAL mode persistence, dual WebSocket streaming channels, and analyst remediation REST endpoints.

---

## Executive Summary

Phase 5 delivers the communications and coordination backbone for AegisRansom-X. Built on FastAPI and Uvicorn, it hosts the `/ws/telemetry` and `/ws/alerts` WebSocket streaming channels, maintains an audit ledger in SQLite WAL mode, and provides REST endpoints for simulation triggering, APFS rollback, and POSIX signal dispatch.

---

## Sub-Phase Breakdown

1. [**Phase 5.1: FastAPI Server & SQLite WAL Mode Audit Ledger**](./phase-5.1-fastapi-sqlite.md)
   - Application lifespan manager and non-blocking event loop binding.
   - SQLite WAL (Write-Ahead Logging) database tracking incidents, events, and XAI factor weights.
2. [**Phase 5.2: Real-Time WebSocket Streaming Hub**](./phase-5.2-websocket-stream.md)
   - Channels: `/ws/telemetry`, `/ws/alerts`, `/ws/copilot`.
   - Sends instant initial `HEALTH_STATUS` snapshot upon handshake.
   - Thread-safe non-blocking broadcast with $< 50\text{ms}$ fan-out latency.
3. [**Phase 5.3: Analyst Control REST Endpoints**](./phase-5.3-action-endpoints.md)
   - `POST /api/simulate/start`: Triggers safe attack simulator in burst/stealth/benign mode.
   - `POST /api/process/{pid}/rollback`: Executes 1-Click APFS shadow cache restore.
   - `POST /api/process/{pid}/signal`: Dispatches `SIGCONT` or `SIGKILL`.
   - `GET /api/simulator/files`: Returns status of all 54 sandbox targets.

---

## Verification Evidence
- Live server healthy on `http://127.0.0.1:8000`.
- All endpoints tested via `curl` returning HTTP 200 JSON payloads.
- WebSocket ping/pong verified in `< 5ms`.
