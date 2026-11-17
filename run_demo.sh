#!/usr/bin/env bash
# ==============================================================================
# AegisRansom-X // Unified Demo Launcher Script (3-Minute Live Stage Demo)
# Launches FastAPI backend + React Vite Micro-SOC dashboard with clean traps.
# ==============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Colors for terminal styling
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
AMBER='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "====================================================================="
echo "   🛡️  AEGISRANSOM-X // MICRO-SOC AUTONOMOUS DEFENSE PLATFORM        "
echo "   Target: macOS Apple Silicon | 100% Offline Local ML | POSIX SIGSTOP"
echo "====================================================================="
echo -e "${NC}"

# 1. Resolve Python executable
PYTHON_BIN="python3"
if [ -d "$ROOT_DIR/.venv" ] && [ -x "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
    UVICORN_BIN="$ROOT_DIR/.venv/bin/uvicorn"
else
    UVICORN_BIN="uvicorn"
fi

echo -e "[*] Using Python: ${CYAN}$PYTHON_BIN${NC}"

# 2. Check Node & npm
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}[!] Error: Node.js and npm are required to run the frontend.${NC}"
    exit 1
fi
echo -e "[*] Using Node: ${CYAN}$(node --version)${NC} | npm: ${CYAN}$(npm --version)${NC}"

# 3. Ensure frontend dependencies are installed
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
    echo -e "[*] Installing frontend dependencies in ./frontend..."
    (cd "$ROOT_DIR/frontend" && npm install --silent)
fi

# 4. Graceful termination handler
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo -e "\n${AMBER}[*] Shutting down AegisRansom-X platform cleanly...${NC}"
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "  - Stopping Vite frontend (PID: $FRONTEND_PID)..."
        kill -SIGTERM "$FRONTEND_PID" 2>/dev/null || true
    fi
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "  - Stopping FastAPI backend (PID: $BACKEND_PID)..."
        kill -SIGTERM "$BACKEND_PID" 2>/dev/null || true
    fi
    # Also clean up any lingering brac_sim processes in sandbox
    pkill -f "simulator/brac_sim.py" 2>/dev/null || true
    echo -e "${GREEN}[✔] Shutdown complete. All processes halted.${NC}"
}
trap cleanup SIGINT SIGTERM EXIT

# 5. Start FastAPI backend
echo -e "[*] Starting FastAPI Backend on ${BOLD}http://127.0.0.1:8000${NC}..."
"$UVICORN_BIN" backend.main:app --host 127.0.0.1 --port 8000 --log-level warning &
BACKEND_PID=$!

# Wait for backend healthcheck
MAX_RETRIES=20
COUNT=0
echo -n "[*] Waiting for backend readiness..."
while ! curl -s http://127.0.0.1:8000/api/health >/dev/null 2>&1; do
    sleep 0.3
    echo -n "."
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
        echo -e "\n${RED}[!] Timed out waiting for FastAPI backend to start.${NC}"
        exit 1
    fi
done
echo -e " ${GREEN}[READY]${NC}"

# 6. Reset sandbox targets with 50 files + 4 canaries for demo readiness
echo -e "[*] Priming sandbox with 50 benign files and 4 micro-canaries..."
curl -s -X POST http://127.0.0.1:8000/api/simulator/reset >/dev/null 2>&1 || true

# 7. Start Vite frontend
echo -e "[*] Starting Vite React SOC Dashboard on ${BOLD}http://127.0.0.1:5173${NC}..."
(cd "$ROOT_DIR/frontend" && npm run dev -- --host 127.0.0.1 --port 5173) &
FRONTEND_PID=$!

sleep 1.2

echo -e "\n${GREEN}${BOLD}====================================================================="
echo "   🚀 AEGISRANSOM-X ACTIVE & OPERATIONAL FOR LIVE JURY DEMO"
echo "=====================================================================${NC}"
echo -e "   🖥️  ${BOLD}SOC Dashboard UI:${NC}    ${CYAN}http://127.0.0.1:5173${NC}"
echo -e "   🔌 ${BOLD}FastAPI Backend:${NC}     ${CYAN}http://127.0.0.1:8000${NC}"
echo -e "   📖 ${BOLD}Swagger API Docs:${NC}    ${CYAN}http://127.0.0.1:8000/docs${NC}"
echo -e "   🩺 ${BOLD}Health Endpoint:${NC}     ${CYAN}http://127.0.0.1:8000/api/health${NC}"
echo -e "   📡 ${BOLD}WebSocket Alerts:${NC}    ${CYAN}ws://127.0.0.1:8000/ws/alerts${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${BOLD}3-Minute Demo Playbook:${NC}"
echo -e " 1. Open ${CYAN}http://127.0.0.1:5173${NC} in your browser."
echo -e " 2. Show the top KPI strip: MTTD < 20ms, MTTC < 5ms, Blast Radius 0/54."
echo -e " 3. Click ${BOLD}'Benign Activity'${NC}: Observe normal entropy ~3.5 and zero alert."
echo -e " 4. Click ${BOLD}'Attack (Burst)'${NC}: Watch entropy spike to 7.9, immediate POSIX SIGSTOP freeze, blast radius <= 2."
echo -e " 5. Inspect the Explainable AI (XAI) feature attribution breakdown."
echo -e " 6. Click ${BOLD}'1-Click Rollback'${NC}: Watch instantaneous shadow recovery (0 loss)!"
echo -e "\nPress [Ctrl+C] to stop all services.\n"

# Wait for children
wait "$BACKEND_PID" "$FRONTEND_PID"
