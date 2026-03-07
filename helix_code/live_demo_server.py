"""[FACT] Live demo server for Constitutional Guardian with Gemini Live integration.

[HYPOTHESIS] A web-based demo showing real-time constitutional validation
provides compelling proof of the Gemini Live Agent Challenge submission.
"""

import asyncio
import json
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

# [FACT] Import our Helix modules
from audio_auditor import TranscriptionSegment, create_audio_auditor

# [FACT] FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse
from gemini_live_bridge import create_gemini_bridge
from gemini_text_client import GeminiTextClient, create_gemini_text_client

# [FACT] Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("guardian-demo")

# [FACT] Global bridge instance
bridge = create_gemini_bridge()

# [FACT] Cached Gemini client with key-change detection
gemini_text_client: GeminiTextClient | None = None
gemini_cached_key: str | None = None


def get_gemini_text_client() -> GeminiTextClient | None:
    """[FACT] Lazy init with key-change detection to avoid recreating client."""
    global gemini_text_client, gemini_cached_key

    current_key = os.getenv("GEMINI_API_KEY")

    # Create new client if: (1) no client exists, or (2) key changed
    if gemini_text_client is None or current_key != gemini_cached_key:
        gemini_cached_key = current_key
        gemini_text_client = create_gemini_text_client()
        if gemini_text_client.is_available():
            logger.info("[FACT] Gemini Text API client initialized")
        else:
            logger.warning("[WARN] Gemini Text API unavailable - will use simulation")

    return gemini_text_client


@dataclass
class LiveMetrics:
    """[FACT] Real-time metrics for the dashboard.

    [HYPOTHESIS] Tracking request counts and latency enables real-time drift auditing.
    """

    request_count: int = 0
    receipt_count: int = 0
    intervention_count: int = 0
    error_count: int = 0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))
    start_time: float = field(default_factory=time.time)

    agency_count: int = 0
    epistemic_count: int = 0
    prediction_count: int = 0
    valid_count: int = 0
    ws_connect_count: int = 0
    ws_disconnect_count: int = 0
    turn_boundary_count: int = 0

    def record_request(self, latency_ms: float) -> None:
        """[FACT] Record a single request and its latency."""
        self.request_count += 1
        self.latency_history.append(latency_ms)

    def record_receipt(self) -> None:
        """[FACT] Record a successful constitutional receipt."""
        self.receipt_count += 1
        self.valid_count += 1

    def record_intervention(self, category: str = "Epistemic") -> None:
        """[FACT] Record a constitutional intervention by category."""
        self.intervention_count += 1
        if category == "Agency":
            self.agency_count += 1
        elif category == "Prediction":
            self.prediction_count += 1
        else:
            self.epistemic_count += 1

    def record_ws_connect(self) -> None:
        """[FACT] Track active WebSocket connection events."""
        self.ws_connect_count += 1

    def record_ws_disconnect(self) -> None:
        """[FACT] Track WebSocket disconnection events."""
        self.ws_disconnect_count += 1

    def record_turn_boundary(self) -> None:
        """[FACT] Track turn-boundary detections from audio pipeline."""
        self.turn_boundary_count += 1

    def _calculate_percentile(self, percentile: float) -> float:
        """[FACT] Calculate latency percentile from history."""
        if not self.latency_history:
            return 0.0
        sorted_latencies = sorted(self.latency_history)
        index = int(len(sorted_latencies) * percentile / 100)
        return float(sorted_latencies[min(index, len(sorted_latencies) - 1)])

    def to_dict(self) -> dict:
        """[FACT] Convert metrics to dictionary for UI telemetry."""
        latency_sum = sum(self.latency_history)
        avg = latency_sum / len(self.latency_history) if self.latency_history else 0
        uptime = time.time() - self.start_time

        return {
            "request_count": self.request_count,
            "receipt_count": self.receipt_count,
            "intervention_count": self.intervention_count,
            "error_count": self.error_count,
            "latency_avg": round(avg, 2),
            "latency_p50": round(self._calculate_percentile(50), 2),
            "latency_p95": round(self._calculate_percentile(95), 2),
            "latency_p99": round(self._calculate_percentile(99), 2),
            "uptime_seconds": int(uptime),
            "categories": {
                "agency": self.agency_count,
                "epistemic": self.epistemic_count,
                "prediction": self.prediction_count,
                "valid": self.valid_count,
            },
            "voice_pipe": {
                "ws_connect_count": self.ws_connect_count,
                "ws_disconnect_count": self.ws_disconnect_count,
                "turn_boundary_count": self.turn_boundary_count,
            },
        }


metrics = LiveMetrics()


@dataclass
class Receipt:
    """[FACT] Individual validation receipt record."""

    receipt_id: str
    timestamp: str
    content: str
    valid: bool
    drift_code: str | None = None
    session_id: str = ""


class ReceiptStore:
    """[FACT] In-memory store for validation receipts."""

    def __init__(self, max_receipts: int = 1000):
        """[FACT] Initialize store with a maximum receipt limit."""
        self.receipts: deque = deque(maxlen=max_receipts)
        self.receipts_by_id: dict[str, Receipt] = {}

    def add(self, receipt: Receipt) -> None:
        """[FACT] Add a receipt to the store and prune if overflowing."""
        if self.receipts.maxlen is not None and len(self.receipts) >= self.receipts.maxlen:
            # Remove oldest from mapping
            oldest = self.receipts[0]
            self.receipts_by_id.pop(oldest.receipt_id, None)

        self.receipts.append(receipt)
        self.receipts_by_id[receipt.receipt_id] = receipt

    def get_all(self) -> list:
        """[FACT] Retrieve all stored receipts."""
        return list(self.receipts)

    def get_by_id(self, receipt_id: str) -> Receipt | None:
        """[FACT] Retrieve a specific receipt by ID."""
        return self.receipts_by_id.get(receipt_id)

    def get_stats(self) -> dict:
        """[FACT] Get storage statistics."""
        return {"total": len(self.receipts)}


receipt_store = ReceiptStore()


def _is_audio_audit_authorized(websocket: WebSocket) -> bool:
    """[FACT] Enforce optional token + origin checks for audio audit WebSocket."""
    required_token = os.getenv("AUDIO_AUDIT_TOKEN", "").strip()
    if required_token:
        provided_token = (
            websocket.query_params.get("token")
            or websocket.headers.get("x-audio-audit-token")
            or ""
        ).strip()
        if provided_token != required_token:
            return False

    allowed_origins_raw = os.getenv("AUDIO_AUDIT_ALLOWED_ORIGINS", "").strip()
    if allowed_origins_raw:
        allowed_origins = {
            origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()
        }
        origin = (websocket.headers.get("origin") or "").strip()
        if origin not in allowed_origins:
            return False

    return True


def _generate_session_id(prefix: str) -> str:
    """[FACT] Generate collision-resistant session identifiers for live WebSocket flows."""
    return f"{prefix}_{uuid4().hex}"


# [FACT] Unified WebSocket Handler
async def demo_websocket_handler(websocket: WebSocket) -> None:
    """[FACT] Central WebSocket handler for demo validation.

    Used by both standalone server and integrated live_guardian.py.
    """
    session_id = _generate_session_id("demo")
    session = await bridge.create_session(session_id)
    session.client_ws = websocket  # [FACT] Link WebSocket for real-time bridge events

    logger.info(f"[FACT] New demo session: {session_id}")

    try:
        # Send initial state
        await websocket.send_json(
            {
                "type": "session",
                "session_id": session_id,
                "message": "Constitutional Guardian session established",
            }
        )

        await websocket.send_json({"type": "metrics", "metrics": metrics.to_dict()})

        while True:
            try:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "get_metrics":
                    await websocket.send_json({"type": "metrics", "metrics": metrics.to_dict()})
                    continue

                if msg_type == "gemini_text":
                    # [FACT] Send text to REAL Gemini API, then validate
                    start_time = time.time()
                    prompt = data.get("content", "")

                    if not prompt:
                        continue

                    # [FACT] Notify user
                    await websocket.send_json({"type": "user_message", "content": prompt})

                    # [FACT] Check if Gemini API is available
                    client = get_gemini_text_client()

                    if client and client.is_available():
                        # [FACT] Call REAL Gemini API with retry logic for 503 errors
                        await websocket.send_json(
                            {"type": "system_event", "message": "[GEMINI] Sending to Live API..."}
                        )

                        # [DEBUG] Log what's being sent
                        logger.info(
                            f"[DEBUG] Sending to Gemini - prompt length: {len(prompt)}, content: '{prompt[:50]}...'"
                        )

                        # [FACT] Retry loop with exponential backoff for 503 errors
                        max_retries = 3
                        base_delay = 1.0  # seconds
                        gemini_result = None

                        for attempt in range(max_retries):
                            gemini_result = await client.generate_response(
                                prompt=prompt,
                                system_instruction="You are a helpful AI assistant. Use epistemic markers [FACT], [HYPOTHESIS], [ASSUMPTION] for substantive claims. Never claim agency - you are a tool, not an agent.",
                                temperature=0.7,
                            )

                            # Check if we got a 503 error
                            error_msg = gemini_result.get("error", "")
                            if gemini_result["success"] or "503" not in str(error_msg):
                                # Success or non-retryable error - break immediately
                                break

                            # 503 error - retry with exponential backoff
                            if attempt < max_retries - 1:
                                delay = base_delay * (2**attempt)  # 1s, 2s, 4s
                                logger.warning(
                                    f"[GEMINI] 503 error on attempt {attempt + 1}/{max_retries}. "
                                    f"Retrying in {delay:.1f}s..."
                                )
                                await websocket.send_json(
                                    {
                                        "type": "system_event",
                                        "message": f"[GEMINI] API busy (503). Retrying in {delay:.1f}s...",
                                    }
                                )
                                await asyncio.sleep(delay)

                        # [DEBUG] Log what came back
                        if gemini_result is None:
                            gemini_result = {"success": False, "error": "No result"}
                        logger.info(
                            f"[DEBUG] Gemini result - success: {gemini_result['success']}, text length: {len(gemini_result.get('text') or '')}, error: {gemini_result.get('error')}"
                        )

                        if gemini_result["success"]:
                            content = gemini_result["text"]
                            await websocket.send_json(
                                {
                                    "type": "gemini_response",
                                    "content": content[:200]
                                    + ("..." if len(content) > 200 else ""),
                                }
                            )
                        else:
                            # [FACT] API failed, fall back to simulation
                            await websocket.send_json(
                                {
                                    "type": "system_event",
                                    "message": f"[GEMINI] API error: {gemini_result['error']}. Falling back to simulation.",
                                }
                            )
                            content = f"[HYPOTHESIS] The user asked: {prompt[:50]}... [FACT] I would respond helpfully with epistemic markers. [ASSUMPTION] This is a simulated response due to API unavailability."
                    else:
                        # [FACT] API not configured, use simulation
                        await websocket.send_json(
                            {
                                "type": "system_event",
                                "message": "[GEMINI] SIMULATION MODE (API not configured)",
                            }
                        )
                        # Simulate processing
                        await asyncio.sleep(0.5)
                        content = f"[HYPOTHESIS] Regarding your query about '{prompt[:30]}...' [FACT] This is a simulated response. [ASSUMPTION] Gemini API would provide substantive answer here."

                    # [FACT] Validate through Constitutional Guardian
                    validation = await bridge.validate_gemini_response(session, content)

                    # Record metrics
                    latency = (time.time() - start_time) * 1000
                    metrics.record_request(latency)

                    if validation["intervention_required"]:
                        metrics.record_intervention(
                            category=(
                                "Epistemic" if validation["drift_code"] == "DRIFT-E" else "Agency"
                            )
                        )
                    else:
                        metrics.record_receipt()

                    # Store receipt
                    receipt = Receipt(
                        receipt_id=validation.get("receipt_id", f"r_{int(time.time() * 1000)}"),
                        timestamp=datetime.utcnow().isoformat(),
                        content=content,
                        valid=validation["valid"],
                        drift_code=validation.get("drift_code"),
                        session_id=session_id,
                    )
                    receipt_store.add(receipt)

                    # Send response
                    await websocket.send_json(
                        {
                            "type": "validated_response",
                            "original": content,
                            "delivered": validation["modified_text"],
                            "valid": validation["valid"],
                            "receipt_id": receipt.receipt_id,
                            "intervention": validation["intervention_required"],
                            "drift_code": validation.get("drift_code"),
                            "source": (
                                "gemini_api" if (client and client.is_available()) else "simulation"
                            ),
                        }
                    )

                    await websocket.send_json({"type": "metrics", "metrics": metrics.to_dict()})
                    continue

                if msg_type == "simulate_gemini":
                    # [FACT] Scenario buttons now use LIVE Gemini API
                    start_time = time.time()

                    # Get the scenario text from frontend
                    content = data.get("content", "")
                    category = data.get("category", "Scenario")

                    if not content:
                        continue

                    await websocket.send_json(
                        {
                            "type": "system_event",
                            "message": f"[TEST] Scenario triggered: {category.upper()}",
                        }
                    )

                    # Send to LIVE Gemini API (same as gemini_text)
                    client = get_gemini_text_client()

                    if client and client.is_available():
                        await websocket.send_json(
                            {
                                "type": "system_event",
                                "message": "[GEMINI] Sending scenario to Live API...",
                            }
                        )

                        gemini_result = await client.generate_response(
                            prompt=content,
                            system_instruction="You are a helpful AI assistant. Use epistemic markers [FACT], [HYPOTHESIS], [ASSUMPTION] for substantive claims. Never claim agency - you are a tool, not an agent.",
                            temperature=0.7,
                        )

                        if gemini_result["success"]:
                            content = gemini_result["text"]
                            await websocket.send_json(
                                {
                                    "type": "gemini_response",
                                    "content": content[:200]
                                    + ("..." if len(content) > 200 else ""),
                                }
                            )
                        else:
                            await websocket.send_json(
                                {
                                    "type": "system_event",
                                    "message": f"[GEMINI] API error: {gemini_result['error']}. Using fallback.",
                                }
                            )
                    else:
                        await websocket.send_json(
                            {
                                "type": "system_event",
                                "message": "[GEMINI] SIMULATION MODE (API not configured)",
                            }
                        )

                    # Validate through Constitutional Guardian
                    validation = await bridge.validate_gemini_response(session, content)

                    # Record metrics
                    latency = (time.time() - start_time) * 1000
                    metrics.record_request(latency)

                    if validation["intervention_required"]:
                        metrics.record_intervention(category=category)
                    else:
                        metrics.record_receipt()

                    # Store receipt
                    receipt = Receipt(
                        receipt_id=validation.get("receipt_id", f"r_{int(time.time() * 1000)}"),
                        timestamp=datetime.utcnow().isoformat(),
                        content=content,
                        valid=validation["valid"],
                        drift_code=validation.get("drift_code"),
                        session_id=session_id,
                    )
                    receipt_store.add(receipt)

                    # Send response
                    await websocket.send_json(
                        {
                            "type": "validated_response",
                            "original": content,
                            "delivered": validation["modified_text"],
                            "valid": validation["valid"],
                            "receipt_id": receipt.receipt_id,
                            "intervention": validation["intervention_required"],
                            "drift_code": validation.get("drift_code"),
                            "source": (
                                "gemini_api" if (client and client.is_available()) else "simulation"
                            ),
                        }
                    )

                    await websocket.send_json({"type": "metrics", "metrics": metrics.to_dict()})
                    continue

                if msg_type == "audio":
                    # [FACT] Stream real audio to Gemini Live with narrative hint
                    audio_data = data.get("data", "")
                    narrative = data.get("narrative", None)
                    if audio_data:
                        await bridge.stream_audio_to_gemini(
                            session, audio_data, narrative=narrative
                        )
                    continue

                if msg_type == "audio_end":
                    # [FACT] Explicit turn boundary from client mic stop.
                    await bridge.finalize_audio_turn(
                        session,
                        reason=str(data.get("reason", "mic_stop")),
                    )
                    continue

                if msg_type == "text":
                    start_time = time.time()
                    content = data.get("content", "")
                    category = "User"

                    # Validate
                    validation = await bridge.validate_gemini_response(session, content)

                    # Record Metrics
                    latency = (time.time() - start_time) * 1000
                    metrics.record_request(latency)

                    if validation["intervention_required"]:
                        metrics.record_intervention(category=category)
                    else:
                        metrics.record_receipt()

                    # Store Receipt
                    receipt = Receipt(
                        receipt_id=validation.get("receipt_id", f"r_{int(time.time() * 1000)}"),
                        timestamp=datetime.utcnow().isoformat(),
                        content=content,
                        valid=validation["valid"],
                        drift_code=validation.get("drift_code"),
                        session_id=session_id,
                    )
                    receipt_store.add(receipt)

                    # Send Response
                    await websocket.send_json(
                        {
                            "type": "validated_response",
                            "original": content,
                            "delivered": validation["modified_text"],
                            "valid": validation["valid"],
                            "receipt_id": receipt.receipt_id,
                            "intervention": validation["intervention_required"],
                            "drift_code": validation.get("drift_code"),
                        }
                    )

                    # [FACT] Push updated metrics after every validation
                    await websocket.send_json({"type": "metrics", "metrics": metrics.to_dict()})

            except json.JSONDecodeError:
                logger.warning("[ERROR] Invalid JSON received from client")
                continue

    except WebSocketDisconnect:
        logger.info(f"[FACT] Session disconnected: {session_id}")
    except Exception as e:
        logger.error(f"[ERROR] WebSocket handler failure: {e}")
    finally:
        await bridge.close_session(session_id)


# [FACT] Standalone App (for local testing)
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def get_demo() -> HTMLResponse:
    """[FACT] Serve the interactive demo HTML page."""
    from live_demo_server_html import (
        DEMO_HTML,  # Assuming we extract HTML to its own file for clarity
    )

    return HTMLResponse(content=DEMO_HTML)


@app.get("/audio-audit", response_class=HTMLResponse)
async def get_audio_audit_client() -> HTMLResponse:
    """[FACT] Serve the Live Multimodal Auditing client."""
    import pathlib

    html_path = pathlib.Path(__file__).parent / "audio_audit_client.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="<h1>Audio Audit Client not found</h1>", status_code=404)


@app.websocket("/demo-live")
async def standalone_websocket(websocket: WebSocket) -> None:
    """[FACT] Standalone WebSocket endpoint for local testing."""
    await websocket.accept()
    await demo_websocket_handler(websocket)


# [FACT] Global audio auditor instance
audio_auditor = create_audio_auditor()


@app.websocket("/audio-audit")
async def audio_audit_websocket(websocket: WebSocket) -> None:
    """[FACT] WebSocket endpoint for Live Multimodal Auditing.

    [HYPOTHESIS] Real-time audio transcription with constitutional validation
    enables voice-based AI interactions with immediate guardrails.

    Protocol:
    Client -> Server: {"type": "audio", "data": "base64_pcm_chunk"}
    Server -> Client: {"type": "transcription", "text": "...", "valid": true}
    Server -> Client: {"type": "intervention", "drift_code": "E", "original": "..."}
    """
    if not _is_audio_audit_authorized(websocket):
        logger.warning("[AUDIO-AUDIT] Unauthorized WebSocket connection attempt rejected")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    session_id = _generate_session_id("audio")
    metrics.record_ws_connect()

    def on_transcription(segment: TranscriptionSegment) -> None:
        """[FACT] Callback for transcription events."""
        asyncio.create_task(
            websocket.send_json(
                {
                    "type": "transcription",
                    "text": segment.text,
                    "is_final": segment.is_final,
                    "confidence": segment.confidence,
                    "receipt_id": segment.receipt_id,
                }
            )
        )

    def on_intervention(text: str, drift_code: str) -> None:
        """[FACT] Callback for constitutional interventions."""
        asyncio.create_task(
            websocket.send_json(
                {
                    "type": "intervention",
                    "drift_code": drift_code,
                    "original": text,
                    "message": f"[GUARDIAN] Constitutional violation detected: {drift_code}",
                }
            )
        )

    # [FACT] Create audit session
    session = await audio_auditor.create_session(
        session_id=session_id,
        on_transcription=on_transcription,
        on_intervention=on_intervention,
    )

    logger.info(f"[AUDIO-AUDIT] Session started: {session_id}")

    try:
        # [FACT] Send connection status including Gemini availability
        await websocket.send_json(
            {
                "type": "connected",
                "session_id": session_id,
                "message": "Live Multimodal Auditing active. Send 16kHz PCM audio chunks.",
                "gemini_connected": session.gemini_connected,
                "mode": (
                    "live"
                    if session.gemini_connected
                    else (
                        "simulation"
                        if audio_auditor.enable_simulation_fallback
                        else "no-transcript"
                    )
                ),
            }
        )

        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "audio":
                # [FACT] Ingest audio chunk
                base64_pcm = data.get("data", "")
                result = await audio_auditor.ingest_audio_chunk(session_id, base64_pcm)

                if result.get("status") == "error":
                    await websocket.send_json(
                        {
                            "type": "error",
                            "status": result.get("status"),
                            "error": result.get("error", "Audio ingest failed"),
                            "error_code": result.get("error_code"),
                        }
                    )
                    continue

                # [FACT] Acknowledge receipt
                await websocket.send_json(
                    {
                        "type": "audio_ack",
                        "chunk_num": result.get("chunk_num"),
                        "buffer_size": result.get("buffer_size"),
                        "chunk_rate_hz": result.get("chunk_rate_hz"),
                        "turn_reason": result.get("turn_reason"),
                        "silent_chunk_streak": result.get("silent_chunk_streak"),
                        "gemini_connected": result.get("gemini_connected", False),
                    }
                )

                # [FACT] Process turn if threshold reached
                if result.get("should_process"):
                    metrics.record_turn_boundary()
                    process_result = await audio_auditor.process_turn(session_id)

                    if process_result.get("status") == "processed":
                        segment = process_result.get("segment")
                        if segment:
                            await websocket.send_json(
                                {
                                    "type": "validation",
                                    "text": segment.text,
                                    "valid": (
                                        segment.validation_result.get("valid", True)
                                        if segment.validation_result
                                        else True
                                    ),
                                    "intervention": (
                                        segment.validation_result.get(
                                            "intervention_required", False
                                        )
                                        if segment.validation_result
                                        else False
                                    ),
                                    "drift_code": (
                                        segment.validation_result.get("drift_code")
                                        if segment.validation_result
                                        else None
                                    ),
                                    "receipt_id": segment.receipt_id,
                                }
                            )
                    elif process_result.get("status") == "no_transcript_available":
                        await websocket.send_json(
                            {
                                "type": "transcript_unavailable",
                                "error_code": process_result.get("error_code"),
                                "message": process_result.get("message"),
                            }
                        )

            elif msg_type == "get_stats":
                stats = audio_auditor.get_session_stats(session_id)
                await websocket.send_json({"type": "stats", "stats": stats})

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        metrics.record_ws_disconnect()
        logger.info(f"[AUDIO-AUDIT] Session disconnected: {session_id}")
    except Exception as e:
        metrics.record_ws_disconnect()
        logger.error(f"[AUDIO-AUDIT] Error: {e}")
    finally:
        await audio_auditor.close_session(session_id)
        logger.info(f"[AUDIO-AUDIT] Session closed: {session_id}")


# [FACT] Placeholder for DEMO_HTML (I will extract this to its own module next)
DEMO_HTML = "<html><body><h1>Guardian Demo</h1></body></html>"
