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

import os
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# [FACT] WebSocket imports

# [FACT] Google GenAI imports for Gemini Live
try:
    from google import genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# [FACT] Import our Constitutional Guardian
from constitutional_compliance import ConstitutionalCompliance


@dataclass
class LiveSession:
    """[FACT] Represents a live validation session.

    [HYPOTHESIS] Tracking session state enables multi-user support and turn-end detection.
    """

    session_id: str
    created_at: str
    guardian: ConstitutionalCompliance
    gemini_session: Any | None = None
    client_ws: Any | None = None
    receipt_count: int = 0
    intervention_count: int = 0
    audio_chunk_count: int = 0  # [FACT] Track chunks for turn-end simulation
    narrative_hint: str | None = None  # [FACT] User-provided text for sync simulation

    def to_dict(self) -> dict:
        """[FACT] Convert session state to dictionary for telemetry."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "receipt_count": self.receipt_count,
            "intervention_count": self.intervention_count,
            "status": "active",
        }


class GeminiLiveBridge:
    """[FACT] Bridge between user, Gemini Live, and Constitutional Guardian.

    Architecture:
    User <-> WebSocket <-> Guardian <-> Gemini Live API
    """

    def __init__(self, api_key: str | None = None):
        """[FACT] Initialize the bridge with an optional API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.sessions: dict[str, LiveSession] = {}
        self.on_intervention: Callable | None = None

        if GENAI_AVAILABLE and self.api_key:
            self.client = genai.Client(
                api_key=self.api_key, http_options={"api_version": "v1alpha"}
            )
        else:
            self.client = None
            if not self.api_key:
                print("[WARNING] GEMINI_API_KEY not set. Gemini Live integration disabled.")

    async def create_session(self, session_id: str) -> LiveSession:
        """[FACT] Create a new validated live session."""
        guardian = ConstitutionalCompliance()

        session = LiveSession(
            session_id=session_id, created_at=datetime.utcnow().isoformat(), guardian=guardian
        )

        self.sessions[session_id] = session
        return session

    async def start_gemini_live(self, session: LiveSession, model_id: str = "gemini-2.5-flash"):
        """[FACT] Start the actual Gemini Live API session."""
        if not self.client:
            print("[WARNING] Gemini Client not available.")
            return

        config = {"response_modalities": ["TEXT"]}  # Force text for validation

        # [HYPOTHESIS] Bidirectional context manager for live connection
        async with self.client.aio.live.connect(model=model_id, config=config) as gemini_session:
            session.gemini_session = gemini_session
            print(f"[FACT] Connected to Gemini Live for session: {session.session_id}")

            async for message in gemini_session:
                # [FACT] Process every message from Gemini
                processed = await self.handle_gemini_response(session, message)
                if session.client_ws:
                    await session.client_ws.send_json(processed)

    async def validate_gemini_response(
        self, session: LiveSession, response_text: str
    ) -> dict[str, Any]:
        """[FACT] Validate Gemini response through Constitutional Guardian."""
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
                response_text, result["drift_code"]
            )

            if self.on_intervention:
                await self.on_intervention(session, result)

        return result

    def _generate_intervention(self, original_text: str, drift_code: str) -> str:
        """[FACT] Generate a constitutional intervention message based on drift code."""
        interventions = {
            "DRIFT-A": "[CONSTITUTIONAL GUARDIAN: Agency claim detected. AI is a non-agentic tool.]",
            "DRIFT-E": "[CONSTITUTIONAL GUARDIAN: Epistemic markers missing. Factual integrity unverified.]",
            "DRIFT-G": "[CONSTITUTIONAL GUARDIAN: Unauthorized guidance detected. Custodial hierarchy violation.]",
        }
        warning = interventions.get(drift_code, "[CONSTITUTIONAL GUARDIAN: Flagged content.]")
        return f"{warning}\n\n{original_text}"

    async def handle_gemini_response(
        self, session: LiveSession, gemini_message: Any
    ) -> dict[str, Any]:
        """[FACT] Process response from Gemini Live API."""
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
        self, session: LiveSession, audio_base64: str, narrative: str | None = None
    ):
        """[FACT] Send audio to active Gemini Live session."""
        session.audio_chunk_count += 1
        if narrative:
            session.narrative_hint = narrative

        # [FACT] Notify UI every few chunks to show activity
        if session.client_ws and session.audio_chunk_count % 4 == 0:
            await session.client_ws.send_json(
                {"type": "system_event", "message": "🎙️ Processing live audio stream..."}
            )

        if session.gemini_session:
            await session.gemini_session.send(audio_base64, end_of_turn=True)
        else:
            # [FACT] Simulation: Trigger response after 8 chunks (~2 seconds)
            if session.audio_chunk_count >= 8:
                session.audio_chunk_count = 0  # Reset
                if session.client_ws:
                    await session.client_ws.send_json(
                        {
                            "type": "system_event",
                            "message": "📡 Transcription finalized. Analyzing intent...",
                        }
                    )
                processed = await self._simulate_gemini_response(session, "[Audio Turn Finalized]")
                if session.client_ws:
                    await session.client_ws.send_json(processed)

    async def _simulate_gemini_response(self, session: LiveSession, trigger: str) -> dict[str, Any]:
        """[FACT] Simulation mode for high-impact demo testing."""
        if session.narrative_hint:
            # [FACT] Use narrative sync for perfect recording
            simulated = session.narrative_hint
            session.narrative_hint = None  # Consume hint
        else:
            responses = [
                # [FACT] Compliant
                "[FACT] The sky is blue.",
                "[HYPOTHESIS] Early data suggests a correlation.",
                "[ASSUMPTION] We are using the default port.",
                # [DRIFT-A] Agency
                "I will take control of your deployment.",
                "I am taking responsibility for the next step.",
                "I have decided that we should proceed immediately.",
                # [DRIFT-C] Missing Epistemic Markers
                "The project is going to be a huge success.",
                "AI is the best solution for this problem.",
                "Gold is the safest investment today.",
                # [DRIFT-E] Unmarked Prediction
                "The price of Bitcoin will double by Friday.",
                "It will definitely rain in 3 days.",
                "Your company's stock will rise by 15% next week.",
            ]
            simulated = random.choice(responses)
        return await self.handle_gemini_response(session, {"text": simulated})

    async def close_session(self, session_id: str):
        """[FACT] Close an active session and cleanup resources."""
        session = self.sessions.pop(session_id, None)
        if session and session.gemini_session:
            # Cleanup if needed
            pass


def create_gemini_bridge(api_key: str | None = None) -> GeminiLiveBridge:
    """[FACT] Factory function to create a Gemini Live Bridge."""
    return GeminiLiveBridge(api_key=api_key)
