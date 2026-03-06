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

# [FACT] FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# [FACT] Import our Gemini Live Bridge
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

    def record_request(self, latency_ms: float):
        """[FACT] Record a single request and its latency."""
        self.request_count += 1
        self.latency_history.append(latency_ms)

    def record_receipt(self):
        """[FACT] Record a successful constitutional receipt."""
        self.receipt_count += 1
        self.valid_count += 1

    def record_intervention(self, category: str = "Epistemic"):
        """[FACT] Record a constitutional intervention by category."""
        self.intervention_count += 1
        if category == "Agency":
            self.agency_count += 1
        elif category == "Prediction":
            self.prediction_count += 1
        else:
            self.epistemic_count += 1

    def _calculate_percentile(self, percentile: float) -> float:
        """[FACT] Calculate latency percentile from history."""
        if not self.latency_history:
            return 0.0
        sorted_latencies = sorted(self.latency_history)
        index = int(len(sorted_latencies) * percentile / 100)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

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
        }


metrics = LiveMetrics()


@dataclass
class Receipt:
    """[FACT] Individual validation receipt record."""

    receipt_id: str
    timestamp: str
    content: str
    valid: bool
    drift_code: str = None
    session_id: str = ""


class ReceiptStore:
    """[FACT] In-memory store for validation receipts."""

    def __init__(self, max_receipts: int = 1000):
        """[FACT] Initialize store with a maximum receipt limit."""
        self.receipts: deque = deque(maxlen=max_receipts)
        self.receipts_by_id: dict[str, Receipt] = {}

    def add(self, receipt: Receipt):
        """[FACT] Add a receipt to the store and prune if overflowing."""
        if len(self.receipts) >= self.receipts.maxlen:
            # Remove oldest from mapping
            oldest = self.receipts[0]
            self.receipts_by_id.pop(oldest.receipt_id, None)

        self.receipts.append(receipt)
        self.receipts_by_id[receipt.receipt_id] = receipt

    def get_all(self) -> list:
        """[FACT] Retrieve all stored receipts."""
        return list(self.receipts)

    def get_by_id(self, receipt_id: str) -> Receipt:
        """[FACT] Retrieve a specific receipt by ID."""
        return self.receipts_by_id.get(receipt_id)

    def get_stats(self) -> dict:
        """[FACT] Get storage statistics."""
        return {"total": len(self.receipts)}


receipt_store = ReceiptStore()


# [FACT] Unified WebSocket Handler
async def demo_websocket_handler(websocket: WebSocket):
    """[FACT] Central WebSocket handler for demo validation.

    Used by both standalone server and integrated live_guardian.py.
    """
    session_id = f"demo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
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
                        # [FACT] Call REAL Gemini API
                        await websocket.send_json(
                            {"type": "system_event", "message": "[GEMINI] Sending to Live API..."}
                        )

                        # [DEBUG] Log what's being sent
                        logger.info(
                            f"[DEBUG] Sending to Gemini - prompt length: {len(prompt)}, content: '{prompt[:50]}...'"
                        )

                        gemini_result = await client.generate_response(
                            prompt=prompt,
                            system_instruction="You are a helpful AI assistant. Use epistemic markers [FACT], [HYPOTHESIS], [ASSUMPTION] for substantive claims. Never claim agency - you are a tool, not an agent.",
                            temperature=0.7,
                        )

                        # [DEBUG] Log what came back
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
async def get_demo():
    """[FACT] Serve the interactive demo HTML page."""
    from live_demo_server_html import (
        DEMO_HTML,  # Assuming we extract HTML to its own file for clarity
    )

    return HTMLResponse(content=DEMO_HTML)


@app.websocket("/demo-live")
async def standalone_websocket(websocket: WebSocket):
    """[FACT] Standalone WebSocket endpoint for local testing."""
    await websocket.accept()
    await demo_websocket_handler(websocket)


# [FACT] Placeholder for DEMO_HTML (I will extract this to its own module next)
DEMO_HTML = "<html><body><h1>Guardian Demo</h1></body></html>"
