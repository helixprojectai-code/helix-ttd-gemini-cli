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
from dataclasses import asdict, dataclass, field
from datetime import datetime
from http.cookies import SimpleCookie
from pathlib import Path
from tempfile import gettempdir
from typing import Any, cast
from urllib.parse import parse_qs
from uuid import uuid4

# [FACT] Import our Helix modules
from audio_auditor import TranscriptionSegment, create_audio_auditor

# [FACT] FastAPI and WebSocket imports
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import HTMLResponse, RedirectResponse
from gemini_live_bridge import create_gemini_bridge
from gemini_text_client import GeminiTextClient, create_gemini_text_client

try:
    from gcp_integrations import CloudStorageReceipts
    from request_limits import SlidingWindowRateLimiter
    from secret_resolver import (
        gemini_secret_cache_key,
        resolve_admin_token,
        resolve_audio_audit_token,
    )
except ImportError:  # pragma: no cover
    from .gcp_integrations import CloudStorageReceipts
    from .request_limits import SlidingWindowRateLimiter
    from .secret_resolver import (
        gemini_secret_cache_key,
        resolve_admin_token,
        resolve_audio_audit_token,
    )

# [FACT] Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("guardian-demo")

# [FACT] Global bridge instance
bridge = create_gemini_bridge()
audio_ingress_rate_limiter: SlidingWindowRateLimiter = SlidingWindowRateLimiter()

# [FACT] Cached Gemini client with key-change detection
gemini_text_client: GeminiTextClient | None = None
gemini_cached_key: str | None = None


def _env_int(name: str, default: int) -> int:
    """[FACT] Parse integer deployment knobs with safe fallback behavior."""
    try:
        return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    """[FACT] Parse float deployment knobs with safe fallback behavior."""
    try:
        return float(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _websocket_client_identity(websocket: WebSocket) -> str:
    """[FACT] Derive a stable client identity for WebSocket throttling."""
    forwarded_for = (websocket.headers.get("x-forwarded-for") or "").strip()
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if websocket.client and websocket.client.host:
        return cast(str, websocket.client.host)
    return "unknown"


def _audio_ingress_rate_limit_settings() -> tuple[int, float]:
    """[FACT] Bound new audio ingress connections per client in a short window."""
    return (
        _env_int("HELIX_AUDIO_INGRESS_MAX_CONNECTIONS", 12),
        _env_float("HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS", 60.0),
    )


def _check_audio_ingress_rate_limit(websocket: WebSocket) -> tuple[bool, float]:
    """[FACT] Return whether a client may open another audio ingress WebSocket now."""
    limit, window_seconds = _audio_ingress_rate_limit_settings()
    allowed, retry_after = audio_ingress_rate_limiter.allow(
        key=f"audio:{_websocket_client_identity(websocket)}",
        limit=limit,
        window_seconds=window_seconds,
    )
    return bool(allowed), float(retry_after)


def get_gemini_text_client() -> GeminiTextClient | None:
    """[FACT] Lazy init with key-change detection to avoid recreating client."""
    global gemini_text_client, gemini_cached_key

    current_key = gemini_secret_cache_key(refresh=True)

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
    operator_rate_limit_count: int = 0
    auth_rate_limit_count: int = 0
    audio_rate_limit_count: int = 0
    operator_auth_failure_count: int = 0
    websocket_auth_failure_count: int = 0
    model_armor_request_count: int = 0
    model_armor_block_count: int = 0
    model_armor_fail_open_count: int = 0
    model_armor_fail_closed_count: int = 0
    model_armor_findings: dict[str, int] = field(default_factory=dict)

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

    def record_rate_limit(self, scope: str) -> None:
        """[FACT] Track ingress and operator throttling outcomes by scope."""
        if scope == "auth":
            self.auth_rate_limit_count += 1
        elif scope == "audio":
            self.audio_rate_limit_count += 1
        else:
            self.operator_rate_limit_count += 1

    def record_auth_failure(self, scope: str) -> None:
        """[FACT] Track rejected admin auth attempts across HTTP and WebSocket surfaces."""
        if scope == "websocket":
            self.websocket_auth_failure_count += 1
        else:
            self.operator_auth_failure_count += 1

    def record_model_armor_payload(self, payload: dict[str, Any] | None) -> None:
        """[FACT] Track normalized Model Armor outcomes emitted by Gemini text flows."""
        if not payload:
            return
        for direction in ("input", "output"):
            result = payload.get(direction)
            if not isinstance(result, dict):
                continue
            self.model_armor_request_count += 1
            if result.get("blocked"):
                self.model_armor_block_count += 1
            action = str(result.get("action", ""))
            if action == "error_allow":
                self.model_armor_fail_open_count += 1
            elif action == "error_block":
                self.model_armor_fail_closed_count += 1
            findings = result.get("findings", [])
            if isinstance(findings, list):
                for finding in findings:
                    if isinstance(finding, dict):
                        category = str(finding.get("category", "unknown"))
                        self.model_armor_findings[category] = (
                            self.model_armor_findings.get(category, 0) + 1
                        )

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
            "security_events": {
                "operator_rate_limit_count": self.operator_rate_limit_count,
                "auth_rate_limit_count": self.auth_rate_limit_count,
                "audio_rate_limit_count": self.audio_rate_limit_count,
                "operator_auth_failure_count": self.operator_auth_failure_count,
                "websocket_auth_failure_count": self.websocket_auth_failure_count,
            },
            "model_armor": {
                "request_count": self.model_armor_request_count,
                "block_count": self.model_armor_block_count,
                "fail_open_count": self.model_armor_fail_open_count,
                "fail_closed_count": self.model_armor_fail_closed_count,
                "findings": dict(sorted(self.model_armor_findings.items())),
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
    model_armor: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """[FACT] Serialize receipt for durable storage backends."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Receipt":
        """[FACT] Rehydrate receipt payloads from durable storage."""
        return cls(
            receipt_id=str(payload.get("receipt_id", "")),
            timestamp=str(payload.get("timestamp", "")),
            content=str(payload.get("content", "")),
            valid=bool(payload.get("valid", False)),
            drift_code=payload.get("drift_code"),
            session_id=str(payload.get("session_id", "")),
            model_armor=payload.get("model_armor"),
        )


def _default_local_receipt_path() -> Path:
    """[FACT] Resolve cross-platform local receipt ledger path."""
    configured_path = (os.getenv("HELIX_RECEIPT_STORE_PATH", "") or "").strip()
    if configured_path:
        return Path(configured_path)
    return Path(gettempdir()) / "helix-guardian" / "receipt-store.jsonl"


class LocalReceiptLedger:
    """[FACT] Append-only local JSONL ledger for receipt durability."""

    def __init__(self, path: Path):
        self.path = path

    def append(self, receipt: Receipt) -> None:
        """[FACT] Persist a single receipt to the local ledger."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt.to_dict(), ensure_ascii=True) + "\n")

    def load_recent(self, limit: int) -> list[Receipt]:
        """[FACT] Load the newest persisted receipts from the local ledger."""
        if not self.path.exists():
            return []

        with self.path.open(encoding="utf-8") as handle:
            lines = deque((line.strip() for line in handle if line.strip()), maxlen=max(limit, 1))

        return [Receipt.from_dict(json.loads(line)) for line in lines]

    def get_by_id(self, receipt_id: str) -> Receipt | None:
        """[FACT] Search the local ledger for a specific receipt identifier."""
        if not self.path.exists():
            return None

        with self.path.open(encoding="utf-8") as handle:
            lines = [line.strip() for line in handle if line.strip()]

        for line in reversed(lines):
            payload = json.loads(line)
            if payload.get("receipt_id") == receipt_id:
                return Receipt.from_dict(payload)

        return None


class ReceiptPersistenceManager:
    """[FACT] Coordinate optional durable receipt backends for runtime restore and archival."""

    def __init__(self, mode: str | None = None):
        configured_mode = (
            str(mode or os.getenv("HELIX_RECEIPT_PERSISTENCE", "auto") or "auto").strip().lower()
        )
        self.mode = configured_mode or "auto"
        self.local_ledger: LocalReceiptLedger | None = None
        self.gcs_archive: CloudStorageReceipts | None = None

        gcs_bucket = (os.getenv("GCS_RECEIPT_BUCKET", "") or "").strip()
        if self.mode in {"auto", "gcs", "dual"} and gcs_bucket:
            archive = CloudStorageReceipts(gcs_bucket)
            if archive.client:
                self.gcs_archive = archive
            else:
                logger.warning(
                    "[WARN] GCS receipt archive configured but unavailable; continuing without GCS"
                )

        local_enabled = self.mode in {"local", "dual"} or (
            self.mode == "auto"
            and (
                bool((os.getenv("HELIX_RECEIPT_STORE_PATH", "") or "").strip())
                or self.gcs_archive is not None
            )
        )
        if local_enabled:
            self.local_ledger = LocalReceiptLedger(_default_local_receipt_path())

    @property
    def backend_name(self) -> str:
        """[FACT] Human-readable backend summary for operator diagnostics."""
        if self.local_ledger and self.gcs_archive:
            return "gcs+local"
        if self.gcs_archive:
            return "gcs"
        if self.local_ledger:
            return "local"
        return "memory"

    def is_enabled(self) -> bool:
        """[FACT] True when any durable backend is active."""
        return self.local_ledger is not None or self.gcs_archive is not None

    def append(self, receipt: Receipt) -> None:
        """[FACT] Persist receipt to all configured durable backends."""
        if self.local_ledger is not None:
            self.local_ledger.append(receipt)

        if self.gcs_archive is not None:
            self.gcs_archive.store_receipt(receipt.receipt_id, receipt.to_dict())

    def load_recent(self, limit: int) -> list[Receipt]:
        """[FACT] Restore the newest receipts from the highest-durability backend available."""
        if self.gcs_archive is not None:
            payloads = self.gcs_archive.list_receipts(limit=limit)
            return [Receipt.from_dict(payload) for payload in payloads]

        if self.local_ledger is not None:
            return self.local_ledger.load_recent(limit)

        return []

    def get_by_id(self, receipt_id: str) -> Receipt | None:
        """[FACT] Resolve a receipt from durable storage when not in memory."""
        if self.local_ledger is not None:
            receipt = self.local_ledger.get_by_id(receipt_id)
            if receipt is not None:
                return receipt

        if self.gcs_archive is not None:
            payload = self.gcs_archive.retrieve_receipt(receipt_id)
            if payload is not None:
                return Receipt.from_dict(payload)

        return None

    def stats(self) -> dict[str, Any]:
        """[FACT] Return persistence diagnostics for runtime and audit surfaces."""
        return {
            "enabled": self.is_enabled(),
            "backend": self.backend_name,
            "mode": self.mode,
            "local_path": (str(self.local_ledger.path) if self.local_ledger is not None else None),
            "gcs_bucket": (self.gcs_archive.bucket_name if self.gcs_archive is not None else None),
        }


class ReceiptStore:
    """[FACT] Receipt store with optional durable persistence backends."""

    def __init__(
        self,
        max_receipts: int = 1000,
        persistence: ReceiptPersistenceManager | None = None,
    ):
        """[FACT] Initialize store with memory cache and optional durable backing store."""
        self.receipts: deque[Receipt] = deque(maxlen=max_receipts)
        self.receipts_by_id: dict[str, Receipt] = {}
        self.persistence = persistence or ReceiptPersistenceManager()
        self._restore_recent_receipts()

    def _cache_receipt(self, receipt: Receipt) -> None:
        """[FACT] Cache receipt in memory and prune the oldest mapping on overflow."""
        if self.receipts.maxlen is not None and len(self.receipts) >= self.receipts.maxlen:
            oldest = self.receipts[0]
            self.receipts_by_id.pop(oldest.receipt_id, None)

        self.receipts.append(receipt)
        self.receipts_by_id[receipt.receipt_id] = receipt

    def _restore_recent_receipts(self) -> None:
        """[FACT] Hydrate memory cache from durable storage on startup."""
        if not self.persistence.is_enabled():
            return

        limit = self.receipts.maxlen or 1000
        for receipt in self.persistence.load_recent(limit):
            self._cache_receipt(receipt)

    def add(self, receipt: Receipt) -> None:
        """[FACT] Add a receipt to memory and durable storage."""
        self._cache_receipt(receipt)
        if self.persistence.is_enabled():
            self.persistence.append(receipt)

    def get_all(self) -> list[Receipt]:
        """[FACT] Retrieve all stored receipts."""
        return list(self.receipts)

    def get_by_id(self, receipt_id: str) -> Receipt | None:
        """[FACT] Retrieve a specific receipt by ID, falling back to persistence if needed."""
        cached = self.receipts_by_id.get(receipt_id)
        if cached is not None:
            return cached

        if self.persistence.is_enabled():
            restored = self.persistence.get_by_id(receipt_id)
            if restored is not None:
                self._cache_receipt(restored)
                return restored

        return None

    def get_stats(self) -> dict[str, Any]:
        """[FACT] Get storage statistics and persistence backend details."""
        stats = {"total": len(self.receipts)}
        stats.update(self.persistence.stats())
        return stats


receipt_store = ReceiptStore()


def _intervention_category_from_drift(drift_code: str | None) -> str:
    """[FACT] Map drift codes into the existing operator intervention categories."""
    if drift_code == "DRIFT-A":
        return "Agency"
    if drift_code == "DRIFT-P":
        return "Prediction"
    return "Epistemic"


async def _record_live_validated_response(session: Any, payload: dict[str, Any]) -> None:
    """[FACT] Persist live-bridge validated responses into shared metrics and receipt stores."""
    if payload.get("type") != "validated_response":
        return

    metrics.record_request(0.0)
    metrics.record_model_armor_payload(payload.get("model_armor"))

    if payload.get("intervention"):
        metrics.record_intervention(_intervention_category_from_drift(payload.get("drift_code")))
    else:
        metrics.record_receipt()

    receipt_id = str(
        payload.get("receipt_id") or f"live_{session.session_id}_{int(time.time() * 1000)}"
    )
    payload["receipt_id"] = receipt_id
    receipt_store.add(
        Receipt(
            receipt_id=receipt_id,
            timestamp=str(payload.get("timestamp") or datetime.utcnow().isoformat()),
            content=str(payload.get("original") or ""),
            valid=bool(payload.get("valid", False)),
            drift_code=payload.get("drift_code"),
            session_id=str(getattr(session, "session_id", "")),
            model_armor=(
                payload.get("model_armor") if isinstance(payload.get("model_armor"), dict) else None
            ),
        )
    )


bridge.on_validated_response = _record_live_validated_response

ADMIN_COOKIE_NAME = "helix_admin_session"


def _env_flag(name: str) -> bool:
    """[FACT] Parse a deployment flag using conservative truthy values."""
    return (os.getenv(name, "") or "").strip().lower() in {"1", "true", "yes", "on"}


def _extract_cookie_token(raw_cookie: str | None, cookie_name: str) -> str:
    """[FACT] Parse a named cookie value from request or WebSocket headers."""
    if not raw_cookie:
        return ""

    parsed = SimpleCookie()
    parsed.load(raw_cookie)
    morsel = parsed.get(cookie_name)
    if morsel is None:
        return ""
    return morsel.value.strip()


def _configured_admin_token() -> str:
    """[FACT] Resolve standalone admin auth through the shared secret resolver."""
    return resolve_admin_token(refresh=True) or ""


def _extract_admin_token_from_headers(headers: Any) -> str:
    """[FACT] Resolve admin auth from bearer header, custom header, or cookie."""
    auth_header = (headers.get("authorization") or "").strip()
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    header_token = (headers.get("x-helix-admin-token") or "").strip()
    if header_token:
        return header_token

    return _extract_cookie_token(headers.get("cookie"), ADMIN_COOKIE_NAME)


def _admin_auth_enabled() -> bool:
    """[FACT] Standalone app requires admin auth when configured or explicitly enforced."""
    return bool(_configured_admin_token()) or _env_flag("HELIX_ENFORCE_ADMIN_TOKEN")


def _guard_standalone_page(request: Request, next_path: str) -> str | HTMLResponse:
    """[FACT] Require admin access for standalone HTML pages when enabled."""
    if not _admin_auth_enabled():
        return ""

    required_token = _configured_admin_token()
    if not required_token:
        metrics.record_auth_failure("operator")
        return HTMLResponse(content="Admin token is required but not configured", status_code=503)

    provided_token = _extract_admin_token_from_headers(request.headers)
    if provided_token != required_token:
        if provided_token:
            metrics.record_auth_failure("operator")
        return _standalone_admin_login_page(next_path)
    return provided_token


def _set_admin_session_cookie(
    response: HTMLResponse | RedirectResponse, request: Request, token: str
) -> None:
    """[FACT] Persist standalone admin auth in an HttpOnly cookie for browser flows."""
    if not token:
        return

    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=request.url.scheme == "https",
        max_age=8 * 60 * 60,
        path="/",
    )


def _standalone_admin_login_page(next_path: str) -> HTMLResponse:
    """[FACT] Minimal login form for protected standalone demo surfaces."""
    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='utf-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <title>Admin Access Required</title>
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; display: flex; min-height: 100vh; align-items: center; justify-content: center; }}
        .card {{ width: min(420px, 92vw); background: #111827; border: 1px solid #334155; border-radius: 14px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35); }}
        input {{ width: 100%; box-sizing: border-box; padding: 12px; border-radius: 10px; border: 1px solid #475569; background: #020617; color: #f8fafc; margin: 12px 0 16px; }}
        button {{ width: 100%; border: none; border-radius: 10px; padding: 12px; background: #22c55e; color: #052e16; font-weight: 700; cursor: pointer; }}
      </style>
    </head>
    <body>
      <div class='card'>
        <h1>Admin Access Required</h1>
        <p>Provide the operator token to access this local demo surface.</p>
        <form method='post' action='/auth/admin'>
          <input type='hidden' name='next' value='{next_path}' />
          <input type='password' name='token' placeholder='HELIX admin token' autocomplete='current-password' />
          <button type='submit'>Unlock</button>
        </form>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=401)


def _require_admin_websocket(headers: Any) -> bool:
    """[FACT] Enforce standalone WebSocket admin auth via headers or cookie state."""
    required_token = _configured_admin_token()
    if not required_token:
        allowed = not _env_flag("HELIX_ENFORCE_ADMIN_TOKEN")
        if not allowed:
            metrics.record_auth_failure("websocket")
        return allowed

    provided_token = _extract_admin_token_from_headers(headers)
    allowed = provided_token == required_token
    if not allowed:
        if provided_token:
            metrics.record_auth_failure("websocket")
    return allowed


def _is_audio_audit_authorized(websocket: WebSocket) -> bool:
    """[FACT] Enforce optional token + origin checks for audio audit WebSocket."""
    required_token = resolve_audio_audit_token(refresh=True) or ""
    if required_token:
        provided_token = (websocket.headers.get("x-audio-audit-token") or "").strip()
        if provided_token != required_token:
            if provided_token:
                metrics.record_auth_failure("websocket")
            return False

    allowed_origins_raw = os.getenv("AUDIO_AUDIT_ALLOWED_ORIGINS", "").strip()
    if allowed_origins_raw:
        allowed_origins = {
            origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()
        }
        origin = (websocket.headers.get("origin") or "").strip()
        if origin not in allowed_origins:
            if origin:
                metrics.record_auth_failure("websocket")
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
                            {
                                "type": "system_event",
                                "message": "[GEMINI] Sending to Live API...",
                            }
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

                        metrics.record_model_armor_payload(gemini_result.get("model_armor"))

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
                        model_armor=(
                            gemini_result.get("model_armor")
                            if isinstance(gemini_result, dict)
                            else None
                        ),
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

                        metrics.record_model_armor_payload(gemini_result.get("model_armor"))

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
                        model_armor=(
                            gemini_result.get("model_armor")
                            if isinstance(gemini_result, dict)
                            else None
                        ),
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
async def get_demo(request: Request) -> HTMLResponse:
    """[FACT] Serve the interactive demo HTML page."""
    gate = _guard_standalone_page(request, "/")
    if isinstance(gate, HTMLResponse):
        return gate

    from live_demo_server_html import (
        DEMO_HTML,  # Assuming we extract HTML to its own file for clarity
    )

    response = HTMLResponse(content=DEMO_HTML)
    _set_admin_session_cookie(response, request, gate)
    return response


@app.get("/audio-audit", response_class=HTMLResponse)
async def get_audio_audit_client(request: Request) -> HTMLResponse:
    """[FACT] Serve the Live Multimodal Auditing client."""
    gate = _guard_standalone_page(request, "/audio-audit")
    if isinstance(gate, HTMLResponse):
        return gate

    import pathlib

    html_path = pathlib.Path(__file__).parent / "audio_audit_client.html"
    if html_path.exists():
        response = HTMLResponse(content=html_path.read_text())
        _set_admin_session_cookie(response, request, gate)
        return response
    return HTMLResponse(content="<h1>Audio Audit Client not found</h1>", status_code=404)


@app.post("/auth/admin")
async def admin_login(request: Request) -> RedirectResponse:
    """[FACT] Exchange an operator token for an HttpOnly admin session cookie."""
    body = (await request.body()).decode("utf-8")
    form = parse_qs(body, keep_blank_values=True)
    token = str(form.get("token", [""])[0]).strip()
    next_path = str(form.get("next", ["/"])[0]).strip() or "/"

    required_token = _configured_admin_token()
    if not required_token:
        raise HTTPException(status_code=503, detail="Admin token is not configured")
    if token != required_token:
        raise HTTPException(status_code=401, detail="Admin token required")
    if not next_path.startswith("/"):
        next_path = "/"

    response = RedirectResponse(url=next_path, status_code=303)
    _set_admin_session_cookie(response, request, token)
    return response


@app.websocket("/demo-live")
async def standalone_websocket(websocket: WebSocket) -> None:
    """[FACT] Standalone WebSocket endpoint for local testing."""
    if _admin_auth_enabled() and not _require_admin_websocket(websocket.headers):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
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
    if _admin_auth_enabled() and not _require_admin_websocket(websocket.headers):
        logger.warning("[AUDIO-AUDIT] Standalone admin auth rejected")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if not _is_audio_audit_authorized(websocket):
        logger.warning("[AUDIO-AUDIT] Unauthorized WebSocket connection attempt rejected")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    allowed, retry_after = _check_audio_ingress_rate_limit(websocket)
    if not allowed:
        metrics.record_rate_limit("audio")
        logger.warning(
            "[AUDIO-AUDIT] Rate-limited WebSocket connection rejected (retry_after=%ss)",
            max(1, int(retry_after) or 1),
        )
        await websocket.close(code=status.WS_1013_TRY_AGAIN_LATER)
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
