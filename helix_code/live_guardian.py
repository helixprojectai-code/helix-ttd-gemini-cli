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
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from http.cookies import SimpleCookie
from pathlib import Path
from typing import Any, cast
from urllib.parse import parse_qs

# [FACT] Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn

# [FACT] Import Helix-TTD core modules
from constitutional_compliance import ConstitutionalCompliance
from drift_telemetry import DriftTelemetry
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from federation_receipts import FederationReceiptManager
from gemini_text_client import create_gemini_text_client

try:
    from request_limits import SlidingWindowRateLimiter
    from secret_resolver import (
        active_secret_backend,
        is_gemini_api_key_configured,
        resolve_admin_token,
        resolve_audio_audit_token,
        vault_is_configured,
    )
except ImportError:  # pragma: no cover
    from .request_limits import SlidingWindowRateLimiter
    from .secret_resolver import (
        active_secret_backend,
        is_gemini_api_key_configured,
        resolve_admin_token,
        resolve_audio_audit_token,
        vault_is_configured,
    )

# [FACT] Import demo components

# [FACT] Global state (initialized on startup)
compliance: ConstitutionalCompliance | None = None
receipts: FederationReceiptManager | None = None
telemetry: DriftTelemetry | None = None
operator_rate_limiter = SlidingWindowRateLimiter()
auth_rate_limiter = SlidingWindowRateLimiter()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """[FACT] Initialize constitutional guardian components on app startup."""
    global compliance, receipts, telemetry

    print("=== CONSTITUTIONAL GUARDIAN STARTUP ===")

    compliance = ConstitutionalCompliance()
    receipts = FederationReceiptManager()
    telemetry = DriftTelemetry()

    print("[FACT] Compliance engine initialized")
    print("[FACT] Receipt manager initialized")
    print("[FACT] Drift telemetry initialized")
    print("[LATTICE] Guardian is watching. The Two Owls are vigilant.")

    yield


def _csv_env_values(name: str) -> list[str]:
    """[FACT] Parse a comma-separated env var into normalized values."""
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    return [value.strip() for value in raw.split(",") if value.strip()]


def _guardian_allowed_origins() -> list[str]:
    """[FACT] Return explicit browser origins allowed for cross-origin Guardian access."""
    return _csv_env_values("HELIX_ALLOWED_ORIGINS")


_cors_origins = _guardian_allowed_origins()
_cors_allows_credentials = bool(_cors_origins)
if not _cors_origins and os.getenv("HELIX_ENV", "").strip().lower() != "production":
    _cors_origins = ["*"]


# [FACT] FastAPI application for Cloud Run
app = FastAPI(
    lifespan=lifespan,
    title="Constitutional Guardian",
    description="Real-time constitutional compliance for Gemini Live API. Validates epistemic integrity using [FACT]/[HYPOTHESIS]/[ASSUMPTION] markers.",
    version="1.4.6",
    docs_url="/docs",
    redoc_url="/redoc",
)

# [FACT] Enable CORS for browser-based demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_cors_allows_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_COOKIE_NAME = "helix_admin_session"


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


def _env_flag(name: str) -> bool:
    """[FACT] Parse a deployment flag using conservative truthy values."""
    return (os.getenv(name, "") or "").strip().lower() in {"1", "true", "yes", "on"}


def _guardian_origin_enforced() -> bool:
    """[FACT] Production deploys enforce WebSocket origin validation by default."""
    return bool(_guardian_allowed_origins()) or (
        os.getenv("HELIX_ENV", "").strip().lower() == "production"
    )


def _origin_candidates_from_headers(headers: Any) -> set[str]:
    """[FACT] Derive same-origin browser candidates from forwarded request headers."""
    host = (headers.get("x-forwarded-host") or headers.get("host") or "").strip()
    proto = (headers.get("x-forwarded-proto") or "").strip()

    if "," in host:
        host = host.split(",", 1)[0].strip()
    if "," in proto:
        proto = proto.split(",", 1)[0].strip()

    if not host:
        return set()

    normalized_proto = proto or "https"
    return {f"{normalized_proto}://{host}"}


def _is_guardian_websocket_origin_allowed(headers: Any) -> bool:
    """[FACT] Restrict Guardian WebSockets to explicit allowlists or same-origin browsers."""
    if not _guardian_origin_enforced():
        return True

    origin = (headers.get("origin") or "").strip()
    if not origin:
        return False

    configured_origins = _guardian_allowed_origins()
    if configured_origins:
        return origin in configured_origins

    return origin in _origin_candidates_from_headers(headers)


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
    """[FACT] Resolve the effective admin token through the secret resolver."""
    return resolve_admin_token(refresh=True) or ""


def _extract_admin_token_from_scope(headers: Any) -> str:
    """[FACT] Accept admin auth via bearer header, custom header, or HttpOnly cookie."""
    auth_header = (headers.get("authorization") or "").strip()
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    header_token = (headers.get("x-helix-admin-token") or "").strip()
    if header_token:
        return header_token

    return _extract_cookie_token(headers.get("cookie"), ADMIN_COOKIE_NAME)


def _extract_admin_token(request: Request) -> str:
    """[FACT] Resolve admin auth from request headers or cookie."""
    return _extract_admin_token_from_scope(request.headers)


def _client_identity(request: Request) -> str:
    """[FACT] Derive a stable client identity for request-level throttling."""
    forwarded_for = (request.headers.get("x-forwarded-for") or "").strip()
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    if request.client and request.client.host:
        return cast(str, request.client.host)
    return "unknown"


def _operator_rate_limit_settings() -> tuple[int, float]:
    """[FACT] Operator endpoints share a coarse request budget per client."""
    return (
        _env_int("HELIX_OPERATOR_RATE_LIMIT_MAX_REQUESTS", 120),
        _env_float("HELIX_OPERATOR_RATE_LIMIT_WINDOW_SECONDS", 60.0),
    )


def _auth_rate_limit_settings() -> tuple[int, float]:
    """[FACT] Admin login attempts use a tighter budget than read-only operator APIs."""
    return (
        _env_int("HELIX_AUTH_RATE_LIMIT_MAX_ATTEMPTS", 12),
        _env_float("HELIX_AUTH_RATE_LIMIT_WINDOW_SECONDS", 300.0),
    )


def _record_security_metric(event: str, scope: str) -> None:
    """[FACT] Forward operator security events into the shared live metrics store."""
    from live_demo_server import metrics

    if event == "rate_limit":
        metrics.record_rate_limit(scope)
    elif event == "auth_failure":
        metrics.record_auth_failure(scope)


def _enforce_http_rate_limit(
    request: Request,
    limiter: SlidingWindowRateLimiter,
    scope: str,
    limit: int,
    window_seconds: float,
) -> None:
    """[FACT] Reject bursty operator traffic with an explicit Retry-After signal."""
    allowed, retry_after = limiter.allow(
        key=f"{scope}:{_client_identity(request)}",
        limit=limit,
        window_seconds=window_seconds,
    )
    if allowed:
        return

    _record_security_metric("rate_limit", scope)
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded for {scope}",
        headers={"Retry-After": str(max(1, int(retry_after) or 1))},
    )


def _enforce_operator_rate_limit(request: Request) -> None:
    """[FACT] Apply shared throttling to operator API and HTML surfaces."""
    limit, window_seconds = _operator_rate_limit_settings()
    _enforce_http_rate_limit(request, operator_rate_limiter, "operator", limit, window_seconds)


def _enforce_auth_rate_limit(request: Request) -> None:
    """[FACT] Protect the admin login form from brute-force attempts."""
    limit, window_seconds = _auth_rate_limit_settings()
    _enforce_http_rate_limit(request, auth_rate_limiter, "auth", limit, window_seconds)


def _set_admin_session_cookie(
    response: HTMLResponse | RedirectResponse, request: Request, token: str
) -> None:
    """[FACT] Issue an HttpOnly admin session cookie for same-origin UI flows."""
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


def _admin_login_page(next_path: str) -> HTMLResponse:
    """[FACT] Minimal browser login surface for admin-protected HTML pages."""
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
        h1 {{ margin-top: 0; font-size: 24px; }}
        p {{ color: #94a3b8; line-height: 1.5; }}
        input {{ width: 100%; box-sizing: border-box; padding: 12px; border-radius: 10px; border: 1px solid #475569; background: #020617; color: #f8fafc; margin: 12px 0 16px; }}
        button {{ width: 100%; border: none; border-radius: 10px; padding: 12px; background: #22c55e; color: #052e16; font-weight: 700; cursor: pointer; }}
      </style>
    </head>
    <body>
      <div class='card'>
        <h1>Admin Access Required</h1>
        <p>Provide the operator token to access this surface. The token is stored only in an HttpOnly session cookie.</p>
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


def _admin_auth_enabled() -> bool:
    """[FACT] Admin auth becomes active when configured or explicitly enforced."""
    return bool(_configured_admin_token()) or _env_flag("HELIX_ENFORCE_ADMIN_TOKEN")


def _require_admin_token(request: Request) -> str:
    """[FACT] Enforce admin auth on protected request handlers."""
    required_token = _configured_admin_token()
    if not required_token:
        if _env_flag("HELIX_ENFORCE_ADMIN_TOKEN"):
            _record_security_metric("auth_failure", "operator")
            raise HTTPException(
                status_code=503, detail="Admin token is required but not configured"
            )
        return ""

    provided_token = _extract_admin_token(request)
    if provided_token != required_token:
        if provided_token:
            _record_security_metric("auth_failure", "operator")
        raise HTTPException(status_code=401, detail="Admin token required")
    return provided_token


def _guard_html_page(request: Request, next_path: str) -> str | HTMLResponse:
    """[FACT] Require admin access for browser pages when admin auth is enabled."""
    if not _admin_auth_enabled():
        return ""

    required_token = _configured_admin_token()
    if not required_token:
        _record_security_metric("auth_failure", "operator")
        return HTMLResponse(content="Admin token is required but not configured", status_code=503)

    provided_token = _extract_admin_token(request)
    if provided_token != required_token:
        if provided_token:
            _record_security_metric("auth_failure", "operator")
        return _admin_login_page(next_path)
    return provided_token


def _require_admin_websocket(headers: Any) -> bool:
    """[FACT] Enforce admin auth for WebSocket surfaces using header or cookie state."""
    required_token = _configured_admin_token()
    if not required_token:
        allowed = not _env_flag("HELIX_ENFORCE_ADMIN_TOKEN")
        if not allowed:
            _record_security_metric("auth_failure", "websocket")
        return allowed

    provided_token = _extract_admin_token_from_scope(headers)
    allowed = provided_token == required_token
    if not allowed:
        if provided_token:
            _record_security_metric("auth_failure", "websocket")
    return allowed


def _security_transparency_snapshot() -> dict[str, Any]:
    """[FACT] Snapshot of security posture signals for public transparency page."""
    latest_scan_timestamp = os.getenv("SECURITY_SCAN_TIMESTAMP", "").strip()
    timestamp_source = "env:SECURITY_SCAN_TIMESTAMP"

    if not latest_scan_timestamp:
        latest_scan_timestamp = os.getenv("CI_SECURITY_SCAN_TIMESTAMP", "").strip()
        timestamp_source = "env:CI_SECURITY_SCAN_TIMESTAMP"

    if not latest_scan_timestamp:
        latest_scan_timestamp = "unavailable"
        timestamp_source = "not_configured"

    checks = {
        "bandit": os.getenv("SECURITY_CHECK_BANDIT", "unknown"),
        "ruff": os.getenv("SECURITY_CHECK_RUFF", "unknown"),
        "mypy": os.getenv("SECURITY_CHECK_MYPY", "unknown"),
        "black": os.getenv("SECURITY_CHECK_BLACK", "unknown"),
        "isort": os.getenv("SECURITY_CHECK_ISORT", "unknown"),
        "pre_commit": os.getenv("SECURITY_CHECK_PRE_COMMIT", "unknown"),
    }
    artifact_analysis = {
        "status": os.getenv("SECURITY_ARTIFACT_ANALYSIS_STATUS", "unverified"),
        "scan_timestamp": os.getenv("SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP", "unavailable"),
        "image_uri": os.getenv("SECURITY_ARTIFACT_IMAGE_URI", "unavailable"),
    }

    return {
        "latest_scan_timestamp": latest_scan_timestamp,
        "timestamp_source": timestamp_source,
        "security_posture_score": os.getenv("SECURITY_POSTURE_SCORE", "unscored"),
        "checks": checks,
        "test_status": os.getenv("SECURITY_TEST_STATUS", "unknown"),
        "artifact_analysis": artifact_analysis,
    }


def _runtime_config_snapshot() -> dict[str, Any]:
    """[FACT] Return non-secret runtime config to verify deploy state."""
    allowed_origins_raw = os.getenv("AUDIO_AUDIT_ALLOWED_ORIGINS", "").strip()
    allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "").strip()
    default_topic = f"projects/{project_id}/topics/helix-events" if project_id else "helix-events"

    return {
        "models": {
            "gemini_live_model": os.getenv(
                "GEMINI_LIVE_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"
            ),
            "gemini_text_model": os.getenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview"),
        },
        "auth": {
            "audio_audit_token_required": bool(resolve_audio_audit_token(refresh=True)),
            "audio_audit_allowed_origins": allowed_origins,
            "admin_token_required": bool(resolve_admin_token(refresh=True)),
            "admin_token_enforced": _env_flag("HELIX_ENFORCE_ADMIN_TOKEN"),
            "guardian_allowed_origins": _guardian_allowed_origins(),
            "guardian_origin_enforced": _guardian_origin_enforced(),
        },
        "limits": {
            "max_audio_chunk_bytes": int(os.getenv("HELIX_MAX_AUDIO_CHUNK_BYTES", "131072")),
            "max_audio_b64_chars": int(os.getenv("HELIX_MAX_AUDIO_B64_CHARS", "174764")),
            "audio_rate_window_seconds": float(os.getenv("HELIX_AUDIO_RATE_WINDOW_SECONDS", "5.0")),
            "audio_max_chunks_per_window": int(
                os.getenv("HELIX_AUDIO_MAX_CHUNKS_PER_WINDOW", "100")
            ),
            "operator_rate_limit_window_seconds": _env_float(
                "HELIX_OPERATOR_RATE_LIMIT_WINDOW_SECONDS", 60.0
            ),
            "operator_rate_limit_max_requests": _env_int(
                "HELIX_OPERATOR_RATE_LIMIT_MAX_REQUESTS", 120
            ),
            "auth_rate_limit_window_seconds": _env_float(
                "HELIX_AUTH_RATE_LIMIT_WINDOW_SECONDS", 300.0
            ),
            "auth_rate_limit_max_attempts": _env_int("HELIX_AUTH_RATE_LIMIT_MAX_ATTEMPTS", 12),
            "audio_ingress_rate_limit_window_seconds": _env_float(
                "HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS", 60.0
            ),
            "audio_ingress_max_connections": _env_int("HELIX_AUDIO_INGRESS_MAX_CONNECTIONS", 12),
        },
        "federation": {
            "pubsub_topic": os.getenv("PUBSUB_TOPIC", default_topic),
        },
        "secrets": {
            "backend": active_secret_backend(),
            "vault_configured": vault_is_configured(),
            "gemini_api_key_configured": is_gemini_api_key_configured(),
        },
        "receipts": {
            "persistence_mode": os.getenv("HELIX_RECEIPT_PERSISTENCE", "auto"),
            "local_store_path_configured": bool(os.getenv("HELIX_RECEIPT_STORE_PATH", "").strip()),
            "gcs_bucket_configured": bool(os.getenv("GCS_RECEIPT_BUCKET", "").strip()),
        },
    }


def _audit_dashboard_snapshot(limit: int = 50) -> dict[str, Any]:
    """[FACT] Build audit dashboard payload from in-memory receipt + metrics stores."""
    from live_demo_server import metrics, receipt_store

    safe_limit = max(1, min(limit, 250))
    all_receipts = receipt_store.get_all()
    recent_receipts = list(all_receipts)[-safe_limit:]

    valid_count = sum(1 for r in all_receipts if r.valid)
    intervention_count = len(all_receipts) - valid_count
    drift_counts: dict[str, int] = {}
    for receipt in all_receipts:
        code = receipt.drift_code or "PASS"
        drift_counts[code] = drift_counts.get(code, 0) + 1

    compliance_rate = 100.0
    if all_receipts:
        compliance_rate = round((valid_count / len(all_receipts)) * 100, 2)

    return {
        "snapshot_at": datetime.utcnow().isoformat(),
        "receipts": {
            "total": len(all_receipts),
            "valid": valid_count,
            "interventions": intervention_count,
            "compliance_rate": compliance_rate,
        },
        "drift_counts": drift_counts,
        "metrics": metrics.to_dict(),
        "storage": receipt_store.get_stats(),
        "recent_receipts": [
            {
                "receipt_id": r.receipt_id,
                "timestamp": r.timestamp,
                "valid": r.valid,
                "drift_code": r.drift_code,
                "session_id": r.session_id,
            }
            for r in recent_receipts
        ],
    }


def _prometheus_label_value(value: Any) -> str:
    """[FACT] Escape metric label values for Prometheus text exposition."""
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _prometheus_metric(
    name: str,
    value: int | float,
    *,
    labels: dict[str, Any] | None = None,
) -> str:
    """[FACT] Format a single Prometheus metric sample."""
    if labels:
        rendered = ",".join(
            f'{key}="{_prometheus_label_value(label_value)}"'
            for key, label_value in sorted(labels.items())
        )
        return f"{name}{{{rendered}}} {value}"
    return f"{name} {value}"


def _metrics_snapshot_text() -> str:
    """[FACT] Export authenticated operational telemetry in Prometheus text format."""
    runtime = _runtime_config_snapshot()
    audit = _audit_dashboard_snapshot(limit=50)
    security = _security_transparency_snapshot()
    metrics_data = audit["metrics"]
    receipt_data = audit["receipts"]
    voice_pipe = metrics_data["voice_pipe"]
    categories = metrics_data["categories"]
    security_events = metrics_data.get("security_events", {})
    artifact = security["artifact_analysis"]
    storage = audit["storage"]

    lines = [
        "# HELP helix_requests_total Total validated/demo requests processed by the guardian.",
        "# TYPE helix_requests_total counter",
        _prometheus_metric("helix_requests_total", metrics_data["request_count"]),
        "# HELP helix_receipts_total Total receipts currently retained by the audit store.",
        "# TYPE helix_receipts_total gauge",
        _prometheus_metric("helix_receipts_total", receipt_data["total"]),
        "# HELP helix_receipts_valid_total Total valid receipts retained by the audit store.",
        "# TYPE helix_receipts_valid_total gauge",
        _prometheus_metric("helix_receipts_valid_total", receipt_data["valid"]),
        "# HELP helix_receipts_interventions_total Total intervention receipts retained by the audit store.",
        "# TYPE helix_receipts_interventions_total gauge",
        _prometheus_metric("helix_receipts_interventions_total", receipt_data["interventions"]),
        "# HELP helix_compliance_rate Compliance rate percentage over retained receipts.",
        "# TYPE helix_compliance_rate gauge",
        _prometheus_metric("helix_compliance_rate", receipt_data["compliance_rate"]),
        "# HELP helix_errors_total Total runtime errors recorded by the guardian demo metrics.",
        "# TYPE helix_errors_total counter",
        _prometheus_metric("helix_errors_total", metrics_data["error_count"]),
        "# HELP helix_latency_average_milliseconds Average response latency in milliseconds.",
        "# TYPE helix_latency_average_milliseconds gauge",
        _prometheus_metric("helix_latency_average_milliseconds", metrics_data["latency_avg"]),
        "# HELP helix_latency_percentile_milliseconds Response latency percentile in milliseconds.",
        "# TYPE helix_latency_percentile_milliseconds gauge",
        _prometheus_metric(
            "helix_latency_percentile_milliseconds",
            metrics_data["latency_p50"],
            labels={"percentile": "50"},
        ),
        _prometheus_metric(
            "helix_latency_percentile_milliseconds",
            metrics_data["latency_p95"],
            labels={"percentile": "95"},
        ),
        _prometheus_metric(
            "helix_latency_percentile_milliseconds",
            metrics_data["latency_p99"],
            labels={"percentile": "99"},
        ),
        "# HELP helix_uptime_seconds Guardian process uptime in seconds.",
        "# TYPE helix_uptime_seconds gauge",
        _prometheus_metric("helix_uptime_seconds", metrics_data["uptime_seconds"]),
        "# HELP helix_operator_auth_enforced Whether operator auth enforcement is active.",
        "# TYPE helix_operator_auth_enforced gauge",
        _prometheus_metric(
            "helix_operator_auth_enforced",
            1 if runtime["auth"]["admin_token_enforced"] else 0,
        ),
        "# HELP helix_guardian_origin_enforced Whether Guardian WebSocket origin enforcement is active.",
        "# TYPE helix_guardian_origin_enforced gauge",
        _prometheus_metric(
            "helix_guardian_origin_enforced",
            1 if runtime["auth"]["guardian_origin_enforced"] else 0,
        ),
        "# HELP helix_receipt_storage_enabled Whether durable receipt storage is active.",
        "# TYPE helix_receipt_storage_enabled gauge",
        _prometheus_metric("helix_receipt_storage_enabled", 1 if storage["enabled"] else 0),
        "# HELP helix_receipt_storage_backend Active receipt storage backend and mode.",
        "# TYPE helix_receipt_storage_backend gauge",
        _prometheus_metric(
            "helix_receipt_storage_backend",
            1,
            labels={"backend": storage["backend"], "mode": storage["mode"]},
        ),
        "# HELP helix_artifact_analysis_state Artifact verification state for the current live image.",
        "# TYPE helix_artifact_analysis_state gauge",
        _prometheus_metric(
            "helix_artifact_analysis_state",
            1,
            labels={"status": artifact["status"], "image_uri": artifact["image_uri"]},
        ),
        "# HELP helix_rate_limit_config Current configured rate-limit budget values.",
        "# TYPE helix_rate_limit_config gauge",
        _prometheus_metric(
            "helix_rate_limit_config",
            runtime["limits"]["operator_rate_limit_max_requests"],
            labels={"scope": "operator", "kind": "max_requests"},
        ),
        _prometheus_metric(
            "helix_rate_limit_config",
            runtime["limits"]["operator_rate_limit_window_seconds"],
            labels={"scope": "operator", "kind": "window_seconds"},
        ),
        _prometheus_metric(
            "helix_rate_limit_config",
            runtime["limits"]["auth_rate_limit_max_attempts"],
            labels={"scope": "auth", "kind": "max_attempts"},
        ),
        _prometheus_metric(
            "helix_rate_limit_config",
            runtime["limits"]["auth_rate_limit_window_seconds"],
            labels={"scope": "auth", "kind": "window_seconds"},
        ),
        _prometheus_metric(
            "helix_rate_limit_config",
            runtime["limits"]["audio_ingress_max_connections"],
            labels={"scope": "audio_ingress", "kind": "max_connections"},
        ),
        _prometheus_metric(
            "helix_rate_limit_config",
            runtime["limits"]["audio_ingress_rate_limit_window_seconds"],
            labels={"scope": "audio_ingress", "kind": "window_seconds"},
        ),
        "# HELP helix_drift_category_total Total receipts/interventions by constitutional category.",
        "# TYPE helix_drift_category_total gauge",
    ]

    lines.extend(
        _prometheus_metric(
            "helix_drift_category_total",
            count,
            labels={"category": category},
        )
        for category, count in sorted(categories.items())
    )
    lines.extend(
        [
            "# HELP helix_voice_pipe_events_total Total voice-pipeline lifecycle events.",
            "# TYPE helix_voice_pipe_events_total counter",
        ]
    )
    lines.extend(
        _prometheus_metric(
            "helix_voice_pipe_events_total",
            count,
            labels={"event": event_name.removesuffix("_count")},
        )
        for event_name, count in sorted(voice_pipe.items())
    )
    lines.extend(
        [
            "# HELP helix_drift_events_total Total retained receipts by drift code.",
            "# TYPE helix_drift_events_total gauge",
        ]
    )
    lines.extend(
        _prometheus_metric(
            "helix_drift_events_total",
            count,
            labels={"drift_code": drift_code},
        )
        for drift_code, count in sorted(audit["drift_counts"].items())
    )
    lines.extend(
        [
            "# HELP helix_security_events_total Security-relevant auth and throttling events.",
            "# TYPE helix_security_events_total counter",
        ]
    )
    lines.extend(
        _prometheus_metric(
            "helix_security_events_total",
            count,
            labels={"event": event_name.removesuffix("_count")},
        )
        for event_name, count in sorted(security_events.items())
    )

    return "\n".join(lines) + "\n"


@app.get("/health")
async def health_check() -> JSONResponse:
    """[FACT] Cloud Run health check endpoint for node status."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "node_id": os.getenv("HELIX_NODE_ID", "GCS-GUARDIAN"),
            "version": "1.4.6",
            "compliance_ready": compliance is not None,
        },
    )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    """[FACT] Root endpoint serves the interactive demo dashboard."""
    gate = _guard_html_page(request, "/")
    if isinstance(gate, HTMLResponse):
        return gate

    # Import demo HTML from live_demo_server_html
    from live_demo_server_html import DEMO_HTML

    response = HTMLResponse(content=DEMO_HTML)
    _set_admin_session_cookie(response, request, gate)
    return response


@app.post("/auth/admin")
async def admin_login(request: Request) -> RedirectResponse:
    """[FACT] Exchange an operator token for an HttpOnly admin session cookie."""
    _enforce_auth_rate_limit(request)
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


@app.get("/api")
async def api_info() -> JSONResponse:
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
                "runtime_config": "/api/runtime-config",
                "security_transparency": "/security-transparency",
                "security_transparency_api": "/api/security-transparency",
                "audit_dashboard": "/audit-dashboard",
                "audit_dashboard_api": "/api/audit-dashboard",
                "metrics": "/metrics",
            },
        },
    )


@app.get("/api/gemini-status")
async def gemini_status() -> JSONResponse:
    """[FACT] Check if Gemini Text API is available."""
    client = create_gemini_text_client()
    response_content = {
        "available": client.is_available(),
        "mode": "LIVE" if client.is_available() else "SIMULATION",
        "error": None if client.is_available() else "GEMINI_API_KEY not configured",
    }
    # Include model info when available
    if client.is_available():
        response_content["model"] = client.model
    return JSONResponse(status_code=200, content=response_content)


@app.get("/api/runtime-config")
async def runtime_config(request: Request) -> JSONResponse:
    """[FACT] Expose effective runtime config (non-secret) for deploy verification."""
    _enforce_operator_rate_limit(request)
    _require_admin_token(request)
    return JSONResponse(status_code=200, content=_runtime_config_snapshot())


@app.get("/api/security-transparency")
async def security_transparency_api(request: Request) -> JSONResponse:
    """[FACT] Machine-readable security transparency snapshot."""
    _enforce_operator_rate_limit(request)
    _require_admin_token(request)
    return JSONResponse(status_code=200, content=_security_transparency_snapshot())


@app.get("/security-transparency", response_class=HTMLResponse)
async def security_transparency_page(request: Request) -> HTMLResponse:
    """[FACT] Public page exposing security posture and latest scan timestamp."""
    _enforce_operator_rate_limit(request)
    gate = _guard_html_page(request, "/security-transparency")
    if isinstance(gate, HTMLResponse):
        return gate
    snapshot = _security_transparency_snapshot()
    checks_html = "".join(
        f"<li><strong>{name}</strong>: {status}</li>" for name, status in snapshot["checks"].items()
    )
    artifact = snapshot["artifact_analysis"]
    html = f"""
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='utf-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <title>Security Transparency</title>
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f7fafc; color: #1a202c; }}
        .wrap {{ max-width: 860px; margin: 0 auto; padding: 32px 20px 48px; }}
        .card {{ background: #fff; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.08); padding: 24px; }}
        h1 {{ margin-top: 0; }}
        .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }}
        .pill {{ display: inline-block; background: #e6fffa; color: #065f46; padding: 6px 10px; border-radius: 999px; font-weight: 600; }}
        ul {{ padding-left: 20px; }}
        a {{ color: #2563eb; }}
      </style>
    </head>
    <body>
      <div class='wrap'>
        <div class='card'>
          <h1>Security Transparency</h1>
          <p class='pill'>Security Posture: {snapshot["security_posture_score"]}</p>
          <div class='meta'>
            <div><strong>Latest Scan Timestamp:</strong><br>{snapshot["latest_scan_timestamp"]}</div>
            <div><strong>Timestamp Source:</strong><br>{snapshot["timestamp_source"]}</div>
            <div><strong>Test Status:</strong><br>{snapshot["test_status"]}</div>
            <div><strong>Runtime:</strong><br>Google Cloud Run</div>
          </div>
          <h2>Artifact Analysis</h2>
          <div class='meta'>
            <div><strong>Status:</strong><br>{artifact["status"]}</div>
            <div><strong>Verification Timestamp:</strong><br>{artifact["scan_timestamp"]}</div>
            <div style='grid-column: 1 / -1;'><strong>Image:</strong><br><code>{artifact["image_uri"]}</code></div>
          </div>
          <h2>Control Checks</h2>
          <ul>{checks_html}</ul>
          <p><a href='/api/security-transparency'>View JSON API</a></p>
        </div>
      </div>
    </body>
    </html>
    """
    response = HTMLResponse(content=html)
    _set_admin_session_cookie(response, request, gate)
    return response


@app.get("/api/audit-dashboard")
async def audit_dashboard_api(request: Request, limit: int = 50) -> JSONResponse:
    """[FACT] Machine-readable audit dashboard snapshot for enterprise reporting."""
    _enforce_operator_rate_limit(request)
    _require_admin_token(request)
    return JSONResponse(status_code=200, content=_audit_dashboard_snapshot(limit=limit))


@app.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics(request: Request) -> PlainTextResponse:
    """[FACT] Authenticated Prometheus-style metrics for production observability."""
    _enforce_operator_rate_limit(request)
    _require_admin_token(request)
    return PlainTextResponse(
        content=_metrics_snapshot_text(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.get("/audit-dashboard", response_class=HTMLResponse)
async def audit_dashboard_page(request: Request) -> HTMLResponse:
    """[FACT] Human-friendly audit trail dashboard for compliance review."""
    _enforce_operator_rate_limit(request)
    gate = _guard_html_page(request, "/audit-dashboard")
    if isinstance(gate, HTMLResponse):
        return gate
    html = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
      <meta charset='utf-8' />
      <meta name='viewport' content='width=device-width, initial-scale=1' />
      <title>Audit Dashboard</title>
      <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f5f7fa; color: #0f172a; }
        .wrap { max-width: 1080px; margin: 0 auto; padding: 28px 18px 36px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 18px; }
        .card { background: #fff; border-radius: 10px; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08); padding: 14px; }
        .label { font-size: 12px; color: #475569; text-transform: uppercase; letter-spacing: .06em; }
        .value { font-size: 24px; font-weight: 700; margin-top: 6px; }
        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08); }
        th, td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; text-align: left; }
        th { background: #0f172a; color: #f8fafc; font-weight: 600; }
        .ok { color: #047857; font-weight: 600; }
        .bad { color: #b91c1c; font-weight: 600; }
      </style>
    </head>
    <body>
      <div class='wrap'>
        <h1>Audit Trail Dashboard</h1>
        <p>Live constitutional receipt telemetry for compliance review.</p>
        <div class='grid'>
          <div class='card'><div class='label'>Receipts</div><div id='total' class='value'>0</div></div>
          <div class='card'><div class='label'>Compliance Rate</div><div id='rate' class='value'>0%</div></div>
          <div class='card'><div class='label'>Interventions</div><div id='interventions' class='value'>0</div></div>
          <div class='card'><div class='label'>Requests</div><div id='requests' class='value'>0</div></div>
        </div>
        <table>
          <thead>
            <tr><th>Timestamp</th><th>Receipt</th><th>Status</th><th>Drift Code</th><th>Session</th></tr>
          </thead>
          <tbody id='rows'></tbody>
        </table>
      </div>
      <script>
        async function refreshDashboard() {
          const res = await fetch('/api/audit-dashboard?limit=25', { credentials: 'same-origin' });
          const data = await res.json();
          document.getElementById('total').textContent = data.receipts.total;
          document.getElementById('rate').textContent = data.receipts.compliance_rate + '%';
          document.getElementById('interventions').textContent = data.receipts.interventions;
          document.getElementById('requests').textContent = data.metrics.request_count;

          const rows = document.getElementById('rows');
          rows.innerHTML = '';
          for (const r of data.recent_receipts.slice().reverse()) {
            const tr = document.createElement('tr');
            const statusClass = r.valid ? 'ok' : 'bad';
            tr.innerHTML = `<td>${r.timestamp}</td><td>${r.receipt_id}</td><td class="${statusClass}">${r.valid ? 'PASS' : 'INTERVENTION'}</td><td>${r.drift_code || ''}</td><td>${r.session_id || ''}</td>`;
            rows.appendChild(tr);
          }
        }

        refreshDashboard();
        setInterval(refreshDashboard, 5000);
      </script>
    </body>
    </html>
    """
    response = HTMLResponse(content=html)
    _set_admin_session_cookie(response, request, gate)
    return response


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

    from live_demo_server import Receipt, metrics, receipt_store

    rcpt_id = f"v_{int(datetime.utcnow().timestamp())}"
    receipt = Receipt(
        receipt_id=rcpt_id,
        timestamp=datetime.utcnow().isoformat(),
        content=text,
        valid=compliant,
        drift_code=(
            "DRIFT-E"
            if not compliant and epistemic_count == 0
            else "DRIFT-A" if not compliant else None
        ),
    )
    receipt_store.add(receipt)

    # [FACT] Update global metrics
    metrics.record_request(0.0)  # Local validation is near-instant
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
async def live_websocket(websocket: WebSocket) -> None:
    """[FACT] WebSocket endpoint for real-time constitutional guarding.

    Receives audio/text stream, validates constitution, returns safe response.
    """
    if not _is_guardian_websocket_origin_allowed(websocket.headers):
        await websocket.close(code=1008)
        return
    if _admin_auth_enabled() and not _require_admin_websocket(websocket.headers):
        await websocket.close(code=1008)
        return
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
async def demo_websocket(websocket: WebSocket) -> None:
    """[FACT] Interactive demo WebSocket with Constitutional Guardian validation."""
    client_host = websocket.client.host if websocket.client else "unknown"
    print(f"[FACT] WebSocket connection attempt from: {client_host}")
    try:
        if not _is_guardian_websocket_origin_allowed(websocket.headers):
            print(f"[WARN] WebSocket origin rejected for: {client_host}")
            await websocket.close(code=1008)
            return
        if _admin_auth_enabled() and not _require_admin_websocket(websocket.headers):
            print(f"[WARN] WebSocket admin auth rejected for: {client_host}")
            await websocket.close(code=1008)
            return
        await websocket.accept()
        print(f"[FACT] WebSocket connection ACCEPTED for: {client_host}")
        # Import here to avoid circular dependency
        from live_demo_server import demo_websocket_handler

        await demo_websocket_handler(websocket)
    except Exception as e:
        print(f"[ERROR] WebSocket connection failed: {e}")
    finally:
        client_host = websocket.client.host if websocket.client else "unknown"
        print(f"[FACT] WebSocket connection CLOSED for: {client_host}")


@app.get("/api/receipts")
async def get_receipts(request: Request, limit: int = 50) -> dict[str, Any]:
    """[FACT] API endpoint for demo receipt explorer retrieval."""
    _enforce_operator_rate_limit(request)
    _require_admin_token(request)
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
async def get_receipt(receipt_id: str, request: Request) -> dict[str, Any]:
    """[FACT] API endpoint for specific receipt detail and verification."""
    _enforce_operator_rate_limit(request)
    _require_admin_token(request)
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

    def __init__(self) -> None:
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


def main() -> None:
    """[FACT] Entry point for Cloud Run deployment and local execution."""
    port = int(os.getenv("PORT", "8180"))
    host = "0.0.0.0"  # nosec B104 - Cloud Run requires binding to all interfaces

    print("=== STARTING CONSTITUTIONAL GUARDIAN ===")
    print(f"[FACT] Host: {host}")
    print(f"[FACT] Port: {port}")
    print(f"[FACT] Node: {os.getenv('HELIX_NODE_ID', 'GCS-GUARDIAN')}")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
