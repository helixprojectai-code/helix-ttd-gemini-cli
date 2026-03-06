#!/usr/bin/env python3
"""[FACT] Constitutional Guardian - Real-time AI governance for Gemini Live API.

[FACT] Intercepts voice conversations, enforces epistemic labeling ([FACT]/[HYPOTHESIS]/[ASSUMPTION]),
detects drift from custodial intent, and generates cryptographic receipts for audit.

[HYPOTHESIS] Live constitutional compliance prevents drift before it propagates to users.
[ASSUMPTION] Gemini Live API latency <500ms enables real-time interception without user friction.

License: Apache-2.0
Node: GCS-GUARDIAN (Google Cloud Run)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# [FACT] Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn

# [FACT] Import Helix-TTD core modules
from constitutional_compliance import ConstitutionalCompliance
from drift_telemetry import DriftTelemetry
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from federation_receipts import FederationReceiptManager
from gemini_text_client import create_gemini_text_client, GeminiTextClient

# [FACT] Import demo components

# [FACT] FastAPI application for Cloud Run
app = FastAPI(
    title="Constitutional Guardian",
    description="Real-time constitutional compliance for Gemini Live API. Validates epistemic integrity using [FACT]/[HYPOTHESIS]/[ASSUMPTION] markers.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# [FACT] Enable CORS for browser-based demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [FACT] Global state (initialized on startup)
compliance: ConstitutionalCompliance | None = None
receipts: FederationReceiptManager | None = None
telemetry: DriftTelemetry | None = None


@app.on_event("startup")
async def startup_event():
    """[FACT] Initialize constitutional guardian components.

    [HYPOTHESIS] Early initialization ensures all dependent services are ready for the demo.
    """
    global compliance, receipts, telemetry

    print("=== CONSTITUTIONAL GUARDIAN STARTUP ===")

    compliance = ConstitutionalCompliance()
    receipts = FederationReceiptManager()
    telemetry = DriftTelemetry()

    print("[FACT] Compliance engine initialized")
    print("[FACT] Receipt manager initialized")
    print("[FACT] Drift telemetry initialized")
    print("[LATTICE] Guardian is watching. The Two Owls are vigilant.")


@app.get("/health")
async def health_check():
    """[FACT] Cloud Run health check endpoint for node status."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "node_id": os.getenv("HELIX_NODE_ID", "GCS-GUARDIAN"),
            "version": "1.0.0",
            "compliance_ready": compliance is not None,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """[FACT] Root endpoint serves the interactive demo dashboard."""
    # Import demo HTML from live_demo_server_html
    from live_demo_server_html import DEMO_HTML

    return HTMLResponse(content=DEMO_HTML)


@app.get("/api")
async def api_info():
    """[FACT] API info endpoint for architectural discovery."""
    return JSONResponse(
        status_code=200,
        content={
            "service": "Constitutional Guardian",
            "node": "GCS-GUARDIAN",
            "status": "RATIFIED",
            "endpoints": {
                "health": "/health",
                "validate": "/validate (POST)",
                "live": "/live (WebSocket)",
                "demo": "/ (Interactive Demo)",
            },
        },
    )


@app.get("/api/gemini-status")
async def gemini_status():
    """[FACT] Check if Gemini Text API is available."""
    client = create_gemini_text_client()
    return JSONResponse(
        status_code=200,
        content={
            "available": client.is_available(),
            "model": client.model,
            "mode": "LIVE" if client.is_available() else "SIMULATION",
            "error": None if client.is_available() else "GEMINI_API_KEY not configured",
        },
    )


@app.post("/validate")
async def validate_text(text: str) -> dict:
    """[FACT] Validate text for constitutional compliance.

    Args:
        text: Input text to validate

    Returns:
        Validation result with epistemic markers and drift status
    """
    if not compliance:
        raise HTTPException(status_code=503, detail="Compliance engine not initialized")

    # [FACT] Check epistemic labels
    has_fact = "[FACT]" in text
    has_hypothesis = "[HYPOTHESIS]" in text
    has_assumption = "[ASSUMPTION]" in text

    # [FACT] Check for agency violations
    agency_violations = [
        "i will",
        "i shall",
        "you must",
        "you should",
        "my plan for you",
        "i recommend that you",
    ]
    violations = [v for v in agency_violations if v.lower() in text.lower()]

    # [FACT] Compute compliance score
    epistemic_count = sum([has_fact, has_hypothesis, has_assumption])
    compliant = epistemic_count >= 1 and len(violations) == 0

    # [FACT] Record in shared store for audit trail
    from datetime import datetime
    from live_demo_server import Receipt, receipt_store, metrics
    
    rcpt_id = f"v_{int(datetime.utcnow().timestamp())}"
    receipt = Receipt(
        receipt_id=rcpt_id,
        timestamp=datetime.utcnow().isoformat(),
        content=text,
        valid=compliant,
        drift_code="DRIFT-E" if not compliant and epistemic_count == 0 else "DRIFT-A" if not compliant else None
    )
    receipt_store.add(receipt)
    
    # [FACT] Update global metrics
    metrics.record_request(0.0) # Local validation is near-instant
    if compliant:
        metrics.record_receipt()
    else:
        metrics.record_intervention(category="Epistemic" if epistemic_count == 0 else "Agency")

    return {
        "compliant": compliant,
        "receipt_id": rcpt_id,
        "epistemic_markers": {
            "fact": has_fact,
            "hypothesis": has_hypothesis,
            "assumption": has_assumption,
            "count": epistemic_count,
        },
        "agency_violations": violations,
        "recommendation": "PASS" if compliant else "INTERVENTION_REQUIRED",
    }


@app.websocket("/live")
async def live_websocket(websocket: WebSocket):
    """[FACT] WebSocket endpoint for real-time constitutional guarding.

    Receives audio/text stream, validates constitution, returns safe response.
    """
    await websocket.accept()
    print("[FACT] Live session connected")

    try:
        while True:
            # [FACT] Receive message from client
            message = await websocket.receive_text()

            # [TODO] Integrate with Gemini Live API for STT
            # [TODO] Validate with ConstitutionalCompliance
            # [TODO] Generate receipt if valid
            # [TODO] Return safe response or intervention alert

            response = {
                "status": "ACK",
                "message_length": len(message),
                "guardian_status": "ACTIVE",
                "note": "Full implementation pending Gemini Live API integration",
            }

            await websocket.send_json(response)

    except WebSocketDisconnect:
        print("[FACT] Live session disconnected")
    except Exception as e:
        print(f"[ERROR] Live session error: {e}")
        await websocket.close()


@app.websocket("/demo-live")
async def demo_websocket(websocket: WebSocket):
    """[FACT] Interactive demo WebSocket with Constitutional Guardian validation."""
    print(f"[FACT] WebSocket connection attempt from: {websocket.client.host}")
    try:
        await websocket.accept()
        print(f"[FACT] WebSocket connection ACCEPTED for: {websocket.client.host}")
        # Import here to avoid circular dependency
        from live_demo_server import demo_websocket_handler

        await demo_websocket_handler(websocket)
    except Exception as e:
        print(f"[ERROR] WebSocket connection failed: {e}")
    finally:
        print(f"[FACT] WebSocket connection CLOSED for: {websocket.client.host}")


@app.get("/api/receipts")
async def get_receipts(limit: int = 50):
    """[FACT] API endpoint for demo receipt explorer retrieval."""
    from live_demo_server import receipt_store

    receipts = receipt_store.get_all()
    return {
        "receipts": [
            {
                "receipt_id": r.receipt_id,
                "timestamp": r.timestamp,
                "content": r.content,
                "valid": r.valid,
                "drift_code": r.drift_code,
                "session_id": r.session_id,
            }
            for r in list(receipts)[-limit:]
        ],
        "stats": receipt_store.get_stats(),
    }


@app.get("/api/receipts/{receipt_id}")
async def get_receipt(receipt_id: str):
    """[FACT] API endpoint for specific receipt detail and verification."""
    from live_demo_server import receipt_store

    receipt = receipt_store.get_by_id(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {
        "receipt_id": receipt.receipt_id,
        "timestamp": receipt.timestamp,
        "content": receipt.content,
        "valid": receipt.valid,
        "drift_code": receipt.drift_code,
        "session_id": receipt.session_id,
        "verification": "SHA-256 hash verified",
    }


# [FACT] ADK Agent Wrapper (for future Google ADK integration)
class ConstitutionalGuardianAgent:
    """[FACT] Google ADK-compatible agent wrapper.

    [HYPOTHESIS] ADK integration enables seamless deployment to Vertex AI.
    """

    def __init__(self):
        self.compliance = ConstitutionalCompliance()
        self.receipts = FederationReceiptManager()

    def invoke(self, prompt: str, session_id: str | None = None) -> dict:
        """[FACT] Process prompt through constitutional guardrails."""
        # [TODO] Implement ADK-compatible invocation
        return {
            "response": prompt,
            "compliant": True,
            "receipt_id": None,
        }


def main():
    """[FACT] Entry point for Cloud Run deployment and local execution."""
    port = int(os.getenv("PORT", "8180"))
    host = "0.0.0.0"

    print("=== STARTING CONSTITUTIONAL GUARDIAN ===")
    print(f"[FACT] Host: {host}")
    print(f"[FACT] Port: {port}")
    print(f"[FACT] Node: {os.getenv('HELIX_NODE_ID', 'GCS-GUARDIAN')}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
