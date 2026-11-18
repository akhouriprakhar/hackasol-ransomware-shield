# ==============================================================================
# AegisRansom-X FastAPI Backend Container
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and agent/engine modules
COPY backend/ ./backend/
COPY engine/ ./engine/
COPY agent/ ./agent/
COPY simulator/ ./simulator/

# Set environment defaults
ENV PYTHONUNBUFFERED=1 \
    OLLAMA_URL="http://host.docker.internal:11434" \
    OLLAMA_MODEL="qwen:4b" \
    SANDBOX_PATH="./sandbox_targets"

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
