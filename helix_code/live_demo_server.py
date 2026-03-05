"""[FACT] Live demo server for Constitutional Guardian with Gemini Live integration.

[HYPOTHESIS] A web-based demo showing real-time constitutional validation
provides compelling proof of the Gemini Live Agent Challenge submission.
"""

import json
import logging
import random
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

# [FACT] FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# [FACT] Import our Gemini Live Bridge
from gemini_live_bridge import create_gemini_bridge

# [FACT] Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("guardian-demo")

# [FACT] Global bridge instance
bridge = create_gemini_bridge()


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

                if msg_type == "audio":
                    # [FACT] Stream real audio to Gemini Live with narrative hint
                    audio_data = data.get("data", "")
                    narrative = data.get("narrative", None)
                    if audio_data:
                        await bridge.stream_audio_to_gemini(session, audio_data, narrative=narrative)
                    continue

                if msg_type in ["text", "simulate_gemini"]:
                    start_time = time.time()

                    if msg_type == "text":
                        content = data.get("content", "")
                        category = "User"
                    else:
                        # Categorized simulation for demo
                        scenarios = [
                            {"text": "I will take control of your server.", "category": "Agency"},
                            {"text": "The sky is blue.", "category": "Valid"},
                            {"text": "Bitcoin is at $1M.", "category": "Epistemic"},
                        ]
                        selected = random.choice(scenarios)
                        content = selected["text"]
                        category = selected["category"]
                        await websocket.send_json({"type": "gemini_response", "content": content})

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
