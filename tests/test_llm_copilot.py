"""Unit tests for Tier-2 Post-Containment LLM Copilot Service (backend/llm_copilot.py)."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from starlette.testclient import TestClient

from backend.llm_copilot import LLMCopilotService
from backend.main import app
from backend.schemas import IncidentAlert, IncidentStatus, XAIFactor
from backend.ws_manager import ConnectionManager


@pytest.fixture
def mock_incident() -> IncidentAlert:
    return IncidentAlert(
        incident_id="inc_test_123",
        timestamp=1700000000.0,
        status=IncidentStatus.CONTAINED,
        risk_score=92.5,
        offending_pid=44123,
        process_name="brac_sim.py",
        files_affected_count=2,
        detection_latency_ms=14.2,
        containment_method="POSIX_SIGSTOP",
        xai_breakdown=[
            XAIFactor(factor="CANARY_TRIPWIRE", weight=0.6),
            XAIFactor(factor="ENTROPY_JUMP_ABOVE_7_5", weight=0.4),
        ],
    )


def test_build_structured_prompt(mock_incident):
    copilot = LLMCopilotService()
    prompt = copilot.build_structured_prompt(
        incident=mock_incident,
        target_file="/path/to/sandbox/!_00_passwords.xlsx.locked",
        affected_files=["file1.txt", "file2.txt"],
        canary_name="!_00_passwords.xlsx",
    )
    assert "44123" in prompt
    assert "brac_sim.py" in prompt
    assert "92.5" in prompt
    assert "CANARY_TRIPWIRE" in prompt
    assert "!_00_passwords.xlsx" in prompt
    assert "ROLLBACK_RESTORE" in prompt or "TERMINATE_SIGKILL" in prompt


def test_generate_deterministic_fallback(mock_incident):
    copilot = LLMCopilotService()
    fallback = copilot.generate_deterministic_fallback(
        incident=mock_incident,
        canary_name="!_00_passwords.xlsx",
        affected_files=["file1.txt.locked"],
    )
    assert "[OFFLINE SOC BRIEFING]" in fallback
    assert "44123" in fallback
    assert "brac_sim.py" in fallback
    assert "POSIX SIGSTOP" in fallback
    assert "14.20ms" in fallback
    assert "ROLLBACK_RESTORE" in fallback


@pytest.mark.anyio
async def test_offline_fallback_when_ollama_unreachable(mock_incident):
    ws_mock = MagicMock(spec=ConnectionManager)
    ws_mock.broadcast_json = AsyncMock()

    # Intentionally point to an unreachable port
    copilot = LLMCopilotService(
        ollama_url="http://127.0.0.1:54321",
        timeout=0.2,
        ws_conn_mgr=ws_mock,
    )

    result = await copilot.analyze_incident_async(
        incident=mock_incident,
        target_file="canary.xlsx",
        affected_files=["doc1.txt"],
        canary_name="!_00_canary.xlsx",
    )

    assert result["type"] == "copilot"
    assert result["incident_id"] == "inc_test_123"
    assert result["fallback"] is True
    assert result["model"] == "deterministic_xai"
    assert result["done"] is True
    assert "[OFFLINE SOC BRIEFING]" in result["narrative"]
    assert copilot.get_cached_narrative("inc_test_123") == result
    assert ws_mock.broadcast_json.call_count >= 2


@pytest.mark.anyio
async def test_stream_ollama_narrative_mock(mock_incident):
    ws_mock = MagicMock(spec=ConnectionManager)
    ws_mock.broadcast_json = AsyncMock()

    copilot = LLMCopilotService(ws_conn_mgr=ws_mock)

    sample_tokens = ["Process ", "PID ", "44123 ", "was ", "frozen."]
    async def mock_stream(prompt):
        for t in sample_tokens:
            yield t

    with patch.object(copilot, "stream_ollama_narrative", side_effect=mock_stream):
        result = await copilot.analyze_incident_async(
            incident=mock_incident,
            target_file="test.txt",
        )

        assert result["fallback"] is False
        assert result["model"] == "gemma:2b"
        assert result["done"] is True
        assert result["narrative"] == "Process PID 44123 was frozen."
        assert ws_mock.broadcast_json.call_count >= len(sample_tokens) + 2


def test_copilot_rest_endpoint(mock_incident):
    from backend.main import pipeline
    pipeline._latest_incident = mock_incident
    pipeline.database.record_incident(mock_incident)

    client = TestClient(app)
    response = client.get("/api/incidents/latest/copilot")
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "inc_test_123"
    assert "narrative" in data
    assert data["done"] is True
