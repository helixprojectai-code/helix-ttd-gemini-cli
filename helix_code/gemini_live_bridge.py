"""[FACT] Gemini Live API WebSocket bridge with Constitutional Guardian validation.

[HYPOTHESIS] Real-time audio/text streaming with constitutional validation
demonstrates the core value proposition for the Gemini Live Agent Challenge.

This module creates a bidirectional bridge between:
- User (WebSocket client - browser/demo)
- Gemini Live API (Google's multimodal streaming API)
- Constitutional Guardian (our validation layer)

The Guardian intercepts Gemini responses, validates epistemic integrity,
and blocks or modifies non-compliant content before it reaches the user.
"""

import asyncio
import base64
import contextlib
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# [FACT] Google GenAI imports for Gemini Live
try:
    from google import genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from constitutional_compliance import ConstitutionalCompliance


@dataclass
class LiveSession:
    """[FACT] Represents a live validation session."""

    session_id: str
    created_at: str
    guardian: ConstitutionalCompliance
    gemini_session: Any | None = None
    client_ws: Any | None = None
    receipt_count: int = 0
    intervention_count: int = 0
    audio_chunk_count: int = 0
    audio_turn_ms: float = 0.0
    silent_chunk_streak: int = 0
    last_chunk_ts: float | None = None
    narrative_hint: str | None = None
    gemini_task: Any | None = None
    connect_failures: int = 0
    next_connect_attempt_ts: float = 0.0

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "receipt_count": self.receipt_count,
            "intervention_count": self.intervention_count,
            "status": "active",
        }


class GeminiLiveBridge:
    """[FACT] Bridge between user, Gemini Live, and Constitutional Guardian."""

    SUPPORTED_MODELS = {
        "gemini-3.1-pro-preview": {
            "reasoning": True,
            "description": "Deep reasoning, edge case analysis",
        },
    }

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.sessions: dict[str, LiveSession] = {}
        self.on_intervention: Callable | None = None
        self.client: Any = None

        self.enable_simulation_fallback = os.getenv(
            "HELIX_AUDIO_SIMULATION", ""
        ).strip().lower() in {"1", "true", "yes", "on"}
        self.min_turn_ms = float(os.getenv("HELIX_MIN_TURN_MS", "1200"))
        self.max_turn_ms = float(os.getenv("HELIX_MAX_TURN_MS", "5000"))
        self.silence_threshold = int(os.getenv("HELIX_AUDIO_SILENCE_THRESHOLD", "160"))
        self.silence_chunks_for_turn_end = int(
            os.getenv("HELIX_AUDIO_SILENCE_CHUNKS_FOR_TURN_END", "6")
        )
        self.chunk_gap_ms = float(os.getenv("HELIX_AUDIO_CHUNK_GAP_MS", "450"))
        self.connect_max_retries = int(os.getenv("HELIX_GEMINI_CONNECT_RETRIES", "3"))
        self.connect_retry_base_delay_s = float(
            os.getenv("HELIX_GEMINI_CONNECT_RETRY_BASE_S", "1.0")
        )
        self.connect_retry_cooldown_s = float(os.getenv("HELIX_GEMINI_CONNECT_COOLDOWN_S", "8.0"))

        if GENAI_AVAILABLE and self.api_key:
            self.client = genai.Client(
                api_key=self.api_key, http_options={"api_version": "v1alpha"}
            )
        elif not self.api_key:
            print("[WARNING] GEMINI_API_KEY not set. Gemini Live integration disabled.")

    async def create_session(self, session_id: str) -> LiveSession:
        guardian = ConstitutionalCompliance()
        session = LiveSession(
            session_id=session_id,
            created_at=datetime.utcnow().isoformat(),
            guardian=guardian,
        )
        self.sessions[session_id] = session
        return session

    def _is_task_active(self, task: Any) -> bool:
        return bool(task and hasattr(task, "done") and not task.done())

    async def ensure_gemini_live(self, session: LiveSession) -> None:
        """[FACT] Lazy-start Gemini Live when audio starts and reconnect if needed."""
        if not self.client:
            return
        if session.gemini_session is not None:
            return
        if self._is_task_active(session.gemini_task):
            return

        now = time.time()
        if now < session.next_connect_attempt_ts:
            return

        session.gemini_task = asyncio.create_task(self.start_gemini_live(session))

    async def start_gemini_live(
        self,
        session: LiveSession,
        model_id: str = "gemini-3.1-pro-preview",
        reasoning_mode: bool = False,
    ) -> None:
        if not self.client:
            return

        config: dict[str, Any] = {"response_modalities": ["TEXT"]}
        if reasoning_mode and model_id == "gemini-3.1-pro-preview":
            config["reasoning_mode"] = True

        last_error: str | None = None
        for attempt in range(1, self.connect_max_retries + 1):
            try:
                async with self.client.aio.live.connect(
                    model=model_id,
                    config=config,
                ) as gemini_session:
                    session.gemini_session = gemini_session
                    session.connect_failures = 0
                    session.next_connect_attempt_ts = 0.0
                    if session.client_ws:
                        with contextlib.suppress(Exception):
                            await session.client_ws.send_json(
                                {
                                    "type": "system_event",
                                    "message": "Gemini Live connected for audio transcription.",
                                }
                            )

                    async for message in gemini_session:
                        processed = await self.handle_gemini_response(session, message)
                        if session.client_ws:
                            await session.client_ws.send_json(processed)

                    return
            except Exception as exc:
                last_error = str(exc)
                session.connect_failures += 1
                if session.client_ws:
                    with contextlib.suppress(Exception):
                        await session.client_ws.send_json(
                            {
                                "type": "system_event",
                                "message": (
                                    "Gemini Live connect/stream error "
                                    f"(attempt {attempt}/{self.connect_max_retries}): {last_error}"
                                ),
                            }
                        )

                if attempt < self.connect_max_retries:
                    delay = self.connect_retry_base_delay_s * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
        session.gemini_session = None
        session.next_connect_attempt_ts = time.time() + self.connect_retry_cooldown_s
        if session.client_ws:
            with contextlib.suppress(Exception):
                await session.client_ws.send_json(
                    {
                        "type": "system_event",
                        "message": (
                            "Gemini Live unavailable after retries; using offline mode "
                            f"(last error: {last_error or 'unknown'})."
                        ),
                    }
                )

    async def validate_gemini_response(
        self,
        session: LiveSession,
        response_text: str,
    ) -> dict[str, Any]:
        validation = session.guardian.validate_text(response_text)
        result = {
            "original_text": response_text,
            "valid": validation.compliant,
            "receipt_id": None,
            "intervention_required": not validation.compliant,
            "modified_text": response_text,
            "drift_code": validation.drift_code if not validation.compliant else None,
        }

        if validation.compliant:
            session.receipt_count += 1
            result["receipt_id"] = f"live_{session.session_id}_{session.receipt_count}"
        else:
            session.intervention_count += 1
            result["modified_text"] = self._generate_intervention(
                response_text,
                result["drift_code"],
            )
            if self.on_intervention:
                await self.on_intervention(session, result)

        return result

    def _generate_intervention(self, original_text: str, drift_code: str) -> str:
        interventions = {
            "DRIFT-A": "[CONSTITUTIONAL GUARDIAN: Agency claim detected. AI is a non-agentic tool.]",
            "DRIFT-E": "[CONSTITUTIONAL GUARDIAN: Epistemic markers missing. Factual integrity unverified.]",
            "DRIFT-G": "[CONSTITUTIONAL GUARDIAN: Unauthorized guidance detected. Custodial hierarchy violation.]",
        }
        warning = interventions.get(drift_code, "[CONSTITUTIONAL GUARDIAN: Flagged content.]")
        return f"{warning}\n\n{original_text}"

    async def handle_gemini_response(
        self,
        session: LiveSession,
        gemini_message: Any,
    ) -> dict[str, Any]:
        text = ""
        if hasattr(gemini_message, "text"):
            text = gemini_message.text
        elif isinstance(gemini_message, dict) and "text" in gemini_message:
            text = gemini_message["text"]

        if not text:
            return {"type": "raw", "data": str(gemini_message)}

        validation = await self.validate_gemini_response(session, text)
        return {
            "type": "validated_response",
            "original": text,
            "delivered": validation["modified_text"],
            "valid": validation["valid"],
            "receipt_id": validation.get("receipt_id"),
            "intervention": validation["intervention_required"],
            "drift_code": validation.get("drift_code"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def stream_audio_to_gemini(
        self,
        session: LiveSession,
        audio_base64: str,
        narrative: str | None = None,
    ) -> None:
        pcm_data = self._decode_audio_chunk(audio_base64)
        if not pcm_data:
            return

        session.audio_chunk_count += 1
        session.audio_turn_ms += self._pcm_duration_ms(pcm_data)
        if self._chunk_is_silent(pcm_data):
            session.silent_chunk_streak += 1
        else:
            session.silent_chunk_streak = 0

        now_ts = time.time()
        gap_ms = 0.0
        if session.last_chunk_ts is not None:
            gap_ms = (now_ts - session.last_chunk_ts) * 1000
        session.last_chunk_ts = now_ts

        should_finalize, turn_reason = self._detect_turn_end(session, gap_ms)

        if narrative:
            session.narrative_hint = narrative

        if session.client_ws and session.audio_chunk_count % 4 == 0:
            await session.client_ws.send_json(
                {
                    "type": "system_event",
                    "message": "Processing live audio stream...",
                }
            )

        await self.ensure_gemini_live(session)

        if session.gemini_session:
            with contextlib.suppress(Exception):
                await session.gemini_session.send(
                    input={
                        "mime_type": "audio/pcm",
                        "data": pcm_data,
                    }
                )
            if should_finalize:
                await self.finalize_audio_turn(session, reason=turn_reason or "heuristic")
            return

        if should_finalize and session.client_ws:
            await session.client_ws.send_json(
                {
                    "type": "system_event",
                    "message": f"Turn boundary detected ({turn_reason}). Finalizing transcription...",
                }
            )
            if self.enable_simulation_fallback:
                processed = await self._simulate_gemini_response(session, "[Audio Turn Finalized]")
                await session.client_ws.send_json(processed)
            else:
                await session.client_ws.send_json(
                    {
                        "type": "system_event",
                        "message": "Gemini Live not connected. No transcript generated.",
                    }
                )
            self._reset_turn_state(session)

    async def finalize_audio_turn(
        self,
        session: LiveSession,
        reason: str = "explicit_stop",
    ) -> None:
        if session.client_ws:
            await session.client_ws.send_json(
                {
                    "type": "system_event",
                    "message": f"Turn boundary detected ({reason}). Finalizing transcription...",
                }
            )

        if session.gemini_session:
            with contextlib.suppress(Exception):
                await session.gemini_session.send("", end_of_turn=True)
            self._reset_turn_state(session)
            return

        if self.enable_simulation_fallback and session.client_ws:
            processed = await self._simulate_gemini_response(session, "[Audio Turn Finalized]")
            await session.client_ws.send_json(processed)
        elif session.client_ws:
            await session.client_ws.send_json(
                {
                    "type": "system_event",
                    "message": "Gemini Live not connected. No transcript generated.",
                }
            )

        self._reset_turn_state(session)

    def _decode_audio_chunk(self, audio_base64: str) -> bytes:
        try:
            return base64.b64decode(audio_base64, validate=True)
        except Exception:
            return b""

    def _pcm_duration_ms(self, pcm_data: bytes, sample_rate: int = 16000) -> float:
        if sample_rate <= 0:
            return 0.0
        samples = len(pcm_data) // 2
        return (samples / sample_rate) * 1000

    def _chunk_is_silent(self, pcm_data: bytes) -> bool:
        if len(pcm_data) < 2:
            return True
        view = memoryview(pcm_data)
        for i in range(0, len(view) - 1, 2):
            sample = int.from_bytes(view[i : i + 2], byteorder="little", signed=True)
            if abs(sample) >= self.silence_threshold:
                return False
        return True

    def _detect_turn_end(self, session: LiveSession, gap_ms: float) -> tuple[bool, str | None]:
        if session.audio_turn_ms >= self.max_turn_ms:
            return True, "max_turn_timeout"
        if session.audio_turn_ms >= self.min_turn_ms and gap_ms >= self.chunk_gap_ms:
            return True, "chunk_gap"
        if (
            session.audio_turn_ms >= self.min_turn_ms
            and session.silent_chunk_streak >= self.silence_chunks_for_turn_end
        ):
            return True, "silence_window"
        return False, None

    def _reset_turn_state(self, session: LiveSession) -> None:
        session.audio_turn_ms = 0.0
        session.silent_chunk_streak = 0
        session.last_chunk_ts = None

    async def _simulate_gemini_response(
        self,
        session: LiveSession,
        trigger: str,
    ) -> dict[str, Any]:
        if session.narrative_hint:
            simulated = session.narrative_hint
            session.narrative_hint = None
        else:
            simulated = "[ASSUMPTION] Simulation fallback transcript placeholder."
        return await self.handle_gemini_response(session, {"text": simulated})

    async def close_session(self, session_id: str) -> None:
        session = self.sessions.pop(session_id, None)
        if not session:
            return

        task = session.gemini_task
        if task:
            task.cancel()
            with contextlib.suppress(Exception):
                await task


def create_gemini_bridge(api_key: str | None = None) -> GeminiLiveBridge:
    return GeminiLiveBridge(api_key=api_key)
