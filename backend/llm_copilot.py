"""Tier-2 Post-Containment AI Copilot powered by local Ollama (gemma:2b).

Operates strictly POST-CONTAINMENT in the background without adding any latency
to the sub-20ms POSIX SIGSTOP cryo-freeze hot path.

Provides:
1. Streaming human-readable incident briefings from local Ollama (gemma:2b).
2. Instant deterministic XAI rule synthesis fallback if Ollama is offline or loading.
3. Real-time WebSocket broadcasting over /ws/alerts.
"""

import asyncio
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx

from backend.schemas import IncidentAlert, XAIFactor
from backend.ws_manager import ConnectionManager, ws_manager

logger = logging.getLogger("aegis_copilot")

OLLAMA_DEFAULT_URL = os.getenv("OLLAMA_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT", "4.0"))


class LLMCopilotService:
    """Asynchronous post-containment AI incident explainer with zero-failure fallback."""

    def __init__(
        self,
        ollama_url: str = OLLAMA_DEFAULT_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = OLLAMA_TIMEOUT_SECONDS,
        ws_conn_mgr: Optional[ConnectionManager] = None,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.ws_mgr = ws_conn_mgr or ws_manager
        # Cache for completed incident narratives: incident_id -> narrative dict
        self._incident_narratives: Dict[str, Dict[str, Any]] = {}

    def get_cached_narrative(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored briefing narrative for an incident."""
        return self._incident_narratives.get(incident_id)

    def build_structured_prompt(
        self,
        incident: IncidentAlert,
        target_file: Optional[str] = None,
        affected_files: Optional[List[str]] = None,
        canary_name: Optional[str] = None,
    ) -> str:
        """Construct structured prompt synthesizing XAI factors for Gemma 2B."""
        affected = affected_files or []
        affected_sample = ", ".join([os.path.basename(f) for f in affected[:4]]) if affected else "N/A"
        
        xai_summary = "; ".join([
            f"{f.factor} (weight: {f.weight:.2f})" for f in incident.xai_breakdown
        ]) if incident.xai_breakdown else "Canary Tripwire & Elevated Shannon Entropy"

        prompt = (
            f"You are the AegisRansom-X Tier-2 SOC Incident Analyst Copilot. "
            f"A suspicious ransomware process was just contained locally on macOS via POSIX SIGSTOP.\n\n"
            f"Incident Telemetry:\n"
            f"- Culprit PID: {incident.offending_pid}\n"
            f"- Process Name: {incident.process_name}\n"
            f"- Composite Risk Score: {incident.risk_score}/100 (CRITICAL)\n"
            f"- Detection Latency: {incident.detection_latency_ms:.2f}ms\n"
            f"- Containment State: POSIX SIGSTOP (Process frozen in memory)\n"
            f"- Canary Tripwire Hit: {canary_name or ('Yes' if any('CANARY' in f.factor.upper() for f in incident.xai_breakdown) else 'No')}\n"
            f"- Trigger File: {os.path.basename(target_file) if target_file else 'N/A'}\n"
            f"- Affected Files Sample: {affected_sample} (Total affected: {incident.files_affected_count})\n"
            f"- Explainable AI (XAI) Factors: {xai_summary}\n\n"
            f"Task: Provide a concise 2-3 sentence executive SOC briefing explaining:\n"
            f"1. Exactly what threat behavior triggered containment.\n"
            f"2. The current containment state and files saved.\n"
            f"3. Recommended analyst action (ROLLBACK_RESTORE or TERMINATE_SIGKILL).\n"
            f"Be precise, technical, and authoritative. Do not hallucinate."
        )
        return prompt

    def generate_deterministic_fallback(
        self,
        incident: IncidentAlert,
        target_file: Optional[str] = None,
        affected_files: Optional[List[str]] = None,
        canary_name: Optional[str] = None,
    ) -> str:
        """Deterministic offline rule synthesis if Ollama is unreachable (100% offline guarantee)."""
        has_canary = any(
            "CANARY" in f.factor.upper() and f.weight > 0
            for f in incident.xai_breakdown
        ) or bool(canary_name)

        has_entropy = any(
            "ENTROPY" in f.factor.upper() and f.weight > 0
            for f in incident.xai_breakdown
        )

        canary_str = f"micro-canary honeyfile '{canary_name or '!_00_passwords_vault.xlsx'}'" if has_canary else "rapid file mutation sequence"
        entropy_str = "abnormal 4KB chunk Shannon entropy surge (> 7.5)" if has_entropy else "burst write velocity"
        file_count = incident.files_affected_count

        narrative = (
            f"[OFFLINE SOC BRIEFING] Process PID {incident.offending_pid} ({incident.process_name}) was instantly cryo-frozen "
            f"via POSIX SIGSTOP in {incident.detection_latency_ms:.2f}ms after tripping {canary_str} with {entropy_str}. "
            f"Containment intervened before widespread encryption ({file_count} files impacted). "
            f"Action Required: Inspect process lineage, then execute ROLLBACK_RESTORE to revert mutations or TERMINATE_SIGKILL to eradicate the process."
        )
        return narrative

    async def stream_ollama_narrative(
        self,
        prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Stream token responses from local Ollama endpoint."""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.2,
                "top_p": 0.85,
                "num_predict": 180,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    raise httpx.HTTPStatusError(
                        f"Ollama returned HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

    async def analyze_incident_async(
        self,
        incident: IncidentAlert,
        target_file: Optional[str] = None,
        affected_files: Optional[List[str]] = None,
        canary_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Orchestrate background LLM inference or fallback without blocking the containment loop."""
        incident_id = incident.incident_id
        prompt = self.build_structured_prompt(
            incident=incident,
            target_file=target_file,
            affected_files=affected_files,
            canary_name=canary_name,
        )

        # Notify clients that copilot analysis has started
        await self.ws_mgr.broadcast_json({
            "type": "copilot",
            "incident_id": incident_id,
            "status": "analyzing",
            "model": self.model,
            "done": False,
            "chunk": "",
            "narrative": "",
            "fallback": False,
        })

        collected_narrative = []
        fallback_used = False

        try:
            # Stream tokens from local Ollama
            async for token in self.stream_ollama_narrative(prompt):
                collected_narrative.append(token)
                # Broadcast intermediate streaming chunk
                await self.ws_mgr.broadcast_json({
                    "type": "copilot",
                    "incident_id": incident_id,
                    "status": "streaming",
                    "model": self.model,
                    "done": False,
                    "chunk": token,
                    "narrative": "".join(collected_narrative),
                    "fallback": False,
                })

            full_text = "".join(collected_narrative).strip()
            if not full_text:
                raise ValueError("Empty response from Ollama")

        except Exception as exc:
            logger.info(
                "Local Ollama (%s) unavailable or error (%s); cleanly activating deterministic XAI fallback.",
                self.model,
                exc,
            )
            fallback_used = True
            full_text = self.generate_deterministic_fallback(
                incident=incident,
                target_file=target_file,
                affected_files=affected_files,
                canary_name=canary_name,
            )

        # Final record and broadcast
        result = {
            "type": "copilot",
            "incident_id": incident_id,
            "status": "completed",
            "model": "deterministic_xai" if fallback_used else self.model,
            "done": True,
            "chunk": "",
            "narrative": full_text,
            "fallback": fallback_used,
            "timestamp": incident.timestamp,
        }

        self._incident_narratives[incident_id] = result
        await self.ws_mgr.broadcast_json(result)
        logger.info(
            "Copilot incident briefing generated for %s (fallback=%s)",
            incident_id,
            fallback_used,
        )
        return result
