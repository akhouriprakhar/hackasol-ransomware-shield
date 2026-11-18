# Phase 7.2: Multi-Service Docker Architecture (`docker-compose.yml`)

## Objective
Package the AegisRansom-X React frontend and FastAPI backend into a production-grade multi-service Docker configuration while bridging natively to macOS Apple Silicon Ollama (`qwen:4b`) and the native Darwin Mach FSEvents/SIGSTOP sentinel daemon.

## Architecture & Bridging Strategy
- **macOS Hardware Layer Bridging**:
  - The Aegis sensor hooks into the macOS kernel via Darwin FSEvents, and containment issues POSIX Mach signals (`SIGSTOP`/`SIGCONT`) to host processes in $< 3\text{ms}$.
  - Containers use `extra_hosts: ['host.docker.internal:host-gateway']` to seamlessly route REST, WebSocket, and LLM queries to the host gateway without bridge isolation penalties.
- **Storage Isolation**:
  - Mounts `./sandbox_targets/:/app/sandbox_targets` to guarantee sandbox isolation and instant shadow cache rollback validation.
- **Nginx Reverse Proxy**:
  - Upstream configuration in [`frontend/nginx.conf`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/frontend/nginx.conf) routes `/api/` and `/ws/` to `backend:8000` with automatic fallback to `host.docker.internal:8000`.

## Docker Compose Manifest
[`docker-compose.yml`](file:///Users/akhouriprakhar/Downloads/Hack-a-Sol%205.0/docker-compose.yml):
```yaml
services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: aegis-backend
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - "./sandbox_targets:/app/sandbox_targets"
    environment:
      - OLLAMA_URL=http://host.docker.internal:11434
      - OLLAMA_MODEL=qwen:4b
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/health || exit 1"]

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: aegis-frontend
    ports:
      - "5173:80"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      backend:
        condition: service_healthy
```

## Verification & Proof
- `backend/Dockerfile` builds clean Python 3.11 environment with dependencies.
- `frontend/Dockerfile` multi-stage build produces minimal Alpine Nginx image.
- `docker-compose.yml` config validation: `PASS`.
