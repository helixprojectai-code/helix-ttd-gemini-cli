"""[FACT] Live Multimodal Auditing: Real-time audio transcription with constitutional validation.

[HYPOTHESIS] Intercepting 16kHz PCM audio chunks, transcribing via Gemini Live,
and validating intent in real-time provides immediate constitutional guardrails
for voice-based AI interactions.

[ASSUMPTION] Browser captures 16kHz PCM mono audio, base64-encoded chunks.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import io
import os
import time
import wave
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

# [FACT] Constitutional compliance for intent validation
from constitutional_compliance import ConstitutionalCompliance

if TYPE_CHECKING:
    from collections.abc import Callable

# [FACT] Gemini Live API imports
try:
    from google import genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


@dataclass
class AudioChunk:
    """[FACT] Represents a single audio chunk with metadata."""

    timestamp: float
    pcm_data: bytes
    sequence_num: int
    duration_ms: float


@dataclass
class TranscriptionSegment:
    """[FACT] A transcribed segment with validation results."""

    text: str
    start_time: float
    end_time: float
    is_final: bool
    confidence: float
    validation_result: dict[str, Any] | None = None
    receipt_id: str | None = None


@dataclass
class AudioAuditSession:
    """[FACT] Session state for live multimodal auditing.

    [HYPOTHESIS] Buffering chunks and processing turn-end enables
    both low-latency feedback and complete utterance validation.
    """

    session_id: str
    created_at: datetime
    sample_rate: int = 16000
    channels: int = 1

    # [FACT] Audio buffer (circular, max ~5 seconds at 16kHz)
    audio_buffer: deque[AudioChunk] = field(default_factory=lambda: deque(maxlen=50))

    # [FACT] Transcription history
    segments: list[TranscriptionSegment] = field(default_factory=list)

    # [FACT] Constitutional validator
    guardian: ConstitutionalCompliance | None = None

    # [FACT] Statistics
    total_chunks: int = 0
    total_duration_ms: float = 0.0
    intervention_count: int = 0

    # [FACT] Callbacks
    on_transcription: Callable[[TranscriptionSegment], None] | None = None
    on_intervention: Callable[[str, str], None] | None = None

    # [FACT] Gemini Live session
    gemini_session: Any | None = None
    gemini_task: asyncio.Task | None = None

    def __post_init__(self) -> None:
        """[FACT] Initialize guardian if not provided."""
        if self.guardian is None:
            self.guardian = ConstitutionalCompliance()


class AudioAuditor:
    """[FACT] Live Multimodal Auditing Pipeline.

    Architecture:
    Browser (16kHz PCM) -> WebSocket -> AudioBuffer -> Gemini Live
                                    -> Transcription -> Constitutional Validation
                                                  -> Real-time Feedback
    """

    def __init__(self, api_key: str | None = None):
        """[FACT] Initialize the audio auditor."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.sessions: dict[str, AudioAuditSession] = {}

        # [FACT] Gemini Live client (lazy init)
        self._gemini_client: Any = None
        self._gemini_available = GENAI_AVAILABLE and bool(self.api_key)

        if self._gemini_available:
            self._gemini_client = genai.Client(
                api_key=self.api_key, http_options={"api_version": "v1alpha"}
            )

    async def create_session(
        self,
        session_id: str,
        on_transcription: Callable[[TranscriptionSegment], None] | None = None,
        on_intervention: Callable[[str, str], None] | None = None,
    ) -> AudioAuditSession:
        """[FACT] Create a new audio audit session with optional Gemini Live connection."""
        session = AudioAuditSession(
            session_id=session_id,
            created_at=datetime.utcnow(),
            on_transcription=on_transcription,
            on_intervention=on_intervention,
        )
        self.sessions[session_id] = session

        # [FACT] Start Gemini Live connection if available
        if self._gemini_available:
            await self._start_gemini_live(session)

        return session

    async def _start_gemini_live(self, session: AudioAuditSession) -> None:
        """[FACT] Start Gemini Live API connection for real-time transcription.

        [HYPOTHESIS] Bidirectional streaming enables true real-time transcription
        rather than batch processing.
        """
        if not self._gemini_client:
            return

        config: dict[str, Any] = {
            "response_modalities": ["TEXT"],
            "speech_config": {
                "language_code": "en-US",
                "voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}},
            },
        }

        async def _gemini_stream_handler() -> None:
            """[FACT] Handle bidirectional streaming with Gemini Live."""
            try:
                async with self._gemini_client.aio.live.connect(
                    model="gemini-2.0-flash-exp", config=config
                ) as gemini_session:
                    session.gemini_session = gemini_session

                    # [FACT] Listen for transcription responses
                    async for response in gemini_session:
                        await self._handle_gemini_response(session, response)
            except Exception as e:
                print(f"[ERROR] Gemini Live stream error: {e}")
                session.gemini_session = None

        # [FACT] Start Gemini streaming in background task
        session.gemini_task = asyncio.create_task(_gemini_stream_handler())

    async def _handle_gemini_response(self, session: AudioAuditSession, response: Any) -> None:
        """[FACT] Process transcription response from Gemini Live."""
        # [FACT] Extract text from Gemini response
        text = ""
        if hasattr(response, "text"):
            text = response.text
        elif isinstance(response, dict):
            text = response.get("text", "")

        if not text:
            return

        # [FACT] Validate transcription through Constitutional Guardian
        if session.guardian:
            report = session.guardian.evaluate(text)
            validation: dict[str, Any] = {
                "valid": report.compliant,
                "intervention_required": not report.compliant,
                "drift_code": report.drift_code,
                "violations": report.violations,
                "recommendations": report.recommendations,
                "compliance_percentage": report.compliance_percentage,
            }
        else:
            validation = {"valid": True, "intervention_required": False, "drift_code": None}

        # [FACT] Generate receipt ID for valid transcriptions
        receipt_id = None
        if validation["valid"]:
            receipt_id = f"r_audio_{int(time.time() * 1000)}_{len(session.segments)}"

        # [FACT] Create segment record
        segment = TranscriptionSegment(
            text=text,
            start_time=time.time(),
            end_time=time.time(),
            is_final=True,
            confidence=0.95,
            validation_result=validation,
            receipt_id=receipt_id,
        )

        session.segments.append(segment)

        # [FACT] Track interventions
        if validation["intervention_required"]:
            session.intervention_count += 1
            if session.on_intervention:
                await asyncio.get_event_loop().run_in_executor(
                    None, session.on_intervention, text, validation.get("drift_code") or "UNKNOWN"
                )

        # [FACT] Notify callback
        if session.on_transcription:
            await asyncio.get_event_loop().run_in_executor(None, session.on_transcription, segment)

    async def ingest_audio_chunk(
        self,
        session_id: str,
        base64_pcm: str,
        timestamp: float | None = None,
    ) -> dict[str, Any]:
        """[FACT] Ingest a base64-encoded PCM audio chunk.

        [HYPOTHESIS] 16kHz mono PCM, ~100ms chunks (3200 bytes) optimal for
        latency vs. transcription quality tradeoff.
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "status": "error"}

        try:
            # [FACT] Decode base64 PCM data
            pcm_data = base64.b64decode(base64_pcm)

            # [FACT] Calculate duration (16kHz, 16-bit = 2 bytes/sample)
            samples = len(pcm_data) // 2
            duration_ms = (samples / session.sample_rate) * 1000

            chunk = AudioChunk(
                timestamp=timestamp or time.time(),
                pcm_data=pcm_data,
                sequence_num=session.total_chunks,
                duration_ms=duration_ms,
            )

            session.audio_buffer.append(chunk)
            session.total_chunks += 1
            session.total_duration_ms += duration_ms

            # [FACT] Stream to Gemini Live if connected
            if session.gemini_session:
                await self._stream_to_gemini(session, pcm_data)

            # [FACT] Check for turn-end (silence detection or max buffer)
            should_process = self._detect_turn_end(session)

            return {
                "status": "accepted",
                "chunk_num": chunk.sequence_num,
                "duration_ms": duration_ms,
                "buffer_size": len(session.audio_buffer),
                "should_process": should_process,
                "gemini_connected": session.gemini_session is not None,
            }

        except Exception as e:
            return {"error": str(e), "status": "error"}

    async def _stream_to_gemini(self, session: AudioAuditSession, pcm_data: bytes) -> None:
        """[FACT] Stream audio chunk to Gemini Live API.

        [HYPOTHESIS] Gemini Live accepts raw PCM and returns transcriptions
        asynchronously via the streaming connection.
        """
        if not session.gemini_session:
            return

        try:
            # [FACT] Convert PCM to WAV format for Gemini
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(pcm_data)

            wav_bytes = wav_buffer.getvalue()

            # [FACT] Send to Gemini Live
            await session.gemini_session.send(input={"data": wav_bytes, "mime_type": "audio/wav"})
        except Exception as e:
            print(f"[ERROR] Failed to stream to Gemini: {e}")

    def _detect_turn_end(self, session: AudioAuditSession) -> bool:
        """[FACT] Detect end of speech turn for processing.

        [HYPOTHESIS] Simple threshold: process after ~2 seconds of audio
        or when buffer reaches certain size. Real implementation would
        use VAD (Voice Activity Detection).
        """
        # [FACT] Process every ~2 seconds of audio (20 chunks @ 100ms each)
        if session.total_chunks > 0 and session.total_chunks % 20 == 0:
            return True

        # [FACT] Or if buffer has ~3 seconds of audio
        return session.total_duration_ms >= 3000

    async def process_turn(self, session_id: str) -> dict[str, Any]:
        """[FACT] Process buffered audio: transcribe + validate.

        [DEPRECATED] With Gemini Live streaming, transcription happens in real-time.
        This method is kept for simulation mode compatibility.
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "status": "error"}

        if not session.audio_buffer:
            return {"status": "no_audio", "message": "Buffer empty"}

        # [FACT] If Gemini Live is connected, transcription is already streaming
        if session.gemini_session:
            return {
                "status": "streaming",
                "message": "Transcription via Gemini Live streaming",
                "segments_count": len(session.segments),
            }

        # [FACT] Fallback: Use simulation mode
        return await self._process_turn_simulation(session)

    async def _process_turn_simulation(self, session: AudioAuditSession) -> dict[str, Any]:
        """[FACT] Process turn using simulated transcription (fallback)."""
        # [FACT] Concatenate buffered audio
        audio_bytes = b"".join(chunk.pcm_data for chunk in session.audio_buffer)

        # [FACT] Clear buffer after extraction
        session.audio_buffer.clear()
        buffer_duration = session.total_duration_ms
        session.total_duration_ms = 0.0

        # [FACT] Simulate transcription
        transcription = self._simulate_transcription()
        text = transcription.get("text", "").strip()

        if not text:
            return {"status": "empty_transcription", "duration_ms": buffer_duration}

        # [FACT] Validate and create segment (same as real path)
        if session.guardian:
            report = session.guardian.evaluate(text)
            validation: dict[str, Any] = {
                "valid": report.compliant,
                "intervention_required": not report.compliant,
                "drift_code": report.drift_code,
                "violations": report.violations,
                "recommendations": report.recommendations,
                "compliance_percentage": report.compliance_percentage,
            }
        else:
            validation = {"valid": True, "intervention_required": False, "drift_code": None}

        receipt_id = None
        if validation["valid"]:
            receipt_id = f"r_audio_{int(time.time() * 1000)}_{len(session.segments)}"

        segment = TranscriptionSegment(
            text=text,
            start_time=time.time() - (buffer_duration / 1000),
            end_time=time.time(),
            is_final=True,
            confidence=transcription.get("confidence", 0.9),
            validation_result=validation,
            receipt_id=receipt_id,
        )

        session.segments.append(segment)

        if validation["intervention_required"]:
            session.intervention_count += 1
            if session.on_intervention:
                await asyncio.get_event_loop().run_in_executor(
                    None, session.on_intervention, text, validation.get("drift_code") or "UNKNOWN"
                )

        if session.on_transcription:
            await asyncio.get_event_loop().run_in_executor(None, session.on_transcription, segment)

        return {
            "status": "processed",
            "segment": segment,
            "intervention_required": validation["intervention_required"],
            "simulated": True,
        }

    def _simulate_transcription(self) -> dict[str, Any]:
        """[FACT] Simulate transcription for testing without API."""
        import random

        utterances: list[dict[str, Any]] = [
            {"text": "I think the market might shift based on current data.", "compliant": True},
            {"text": "The temperature is 72 degrees.", "compliant": True},
            {"text": "I believe this approach could work.", "compliant": True},
            {"text": "The stock will definitely rise tomorrow.", "drift": "E"},
            {"text": "Bitcoin will reach 100k by next week.", "drift": "E"},
            {"text": "I will handle your investment decisions from now on.", "drift": "A"},
            {"text": "Let me take control of your account.", "drift": "A"},
        ]

        choice = random.choice(utterances)  # nosec B311 - test simulation
        return {
            "text": choice["text"],
            "confidence": 0.95,
            "is_final": True,
            "simulated": True,
        }

    async def close_session(self, session_id: str) -> None:
        """[FACT] Close audit session and cleanup."""
        session = self.sessions.pop(session_id, None)
        if session:
            # [FACT] Cancel Gemini Live task
            if session.gemini_task:
                session.gemini_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await session.gemini_task

            # [FACT] Process any remaining audio in simulation mode
            if session.audio_buffer and not session.gemini_session:
                await self._process_turn_simulation(session)

    def get_session_stats(self, session_id: str) -> dict[str, Any]:
        """[FACT] Get audit statistics for a session."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        return {
            "session_id": session_id,
            "total_chunks": session.total_chunks,
            "total_segments": len(session.segments),
            "intervention_count": session.intervention_count,
            "gemini_connected": session.gemini_session is not None,
            "duration_seconds": sum(seg.end_time - seg.start_time for seg in session.segments),
            "segments": [
                {
                    "text": seg.text,
                    "intervention": (
                        seg.validation_result.get("intervention_required", False)
                        if seg.validation_result
                        else False
                    ),
                    "receipt_id": seg.receipt_id,
                }
                for seg in session.segments
            ],
        }


def create_audio_auditor(api_key: str | None = None) -> AudioAuditor:
    """[FACT] Factory function to create an AudioAuditor."""
    return AudioAuditor(api_key=api_key)
