"""[FACT] Tests for Live Demo Server WebSocket and HTTP handlers.

[HYPOTHESIS] Testing WebSocket handlers improves coverage of critical paths.
[ASSUMPTION] Mocking Gemini client allows testing without API calls.
"""

from typing import Any

import helix_code.live_demo_server as live_demo_server
from helix_code.live_demo_server import (
    LiveMetrics,
    Receipt,
    ReceiptStore,
    _check_audio_ingress_rate_limit,
    _generate_session_id,
    _is_audio_audit_authorized,
    get_gemini_text_client,
)
from helix_code.request_limits import SlidingWindowRateLimiter


class TestLiveMetrics:
    """[FACT] Test suite for LiveMetrics telemetry."""

    def test_record_request(self) -> None:
        """[FACT] Records request and latency."""
        metrics = LiveMetrics()
        metrics.record_request(150.5)

        assert metrics.request_count == 1
        assert len(metrics.latency_history) == 1
        assert metrics.latency_history[0] == 150.5

    def test_record_receipt(self) -> None:
        """[FACT] Records valid receipt."""
        metrics = LiveMetrics()
        metrics.record_receipt()

        assert metrics.receipt_count == 1
        assert metrics.valid_count == 1

    def test_record_intervention_agency(self) -> None:
        """[FACT] Records agency intervention."""
        metrics = LiveMetrics()
        metrics.record_intervention(category="Agency")

        assert metrics.intervention_count == 1
        assert metrics.agency_count == 1

    def test_record_intervention_epistemic(self) -> None:
        """[FACT] Records epistemic intervention."""
        metrics = LiveMetrics()
        metrics.record_intervention(category="Epistemic")

        assert metrics.intervention_count == 1
        assert metrics.epistemic_count == 1

    def test_calculate_percentile(self) -> None:
        """[FACT] Calculates latency percentiles."""
        metrics = LiveMetrics()

        # Add sorted latencies
        for lat in [10, 20, 30, 40, 50]:
            metrics.record_request(lat)

        p50 = metrics._calculate_percentile(50)
        assert p50 == 30  # Middle value

    def test_to_dict(self) -> None:
        """[FACT] Converts metrics to dictionary."""
        metrics = LiveMetrics()
        metrics.record_request(100)
        metrics.record_receipt()

        data = metrics.to_dict()

        assert data["request_count"] == 1
        assert data["receipt_count"] == 1
        assert "latency_avg" in data
        assert "latency_p50" in data
        assert "latency_p95" in data
        assert "latency_p99" in data
        assert "uptime_seconds" in data
        assert "categories" in data
        assert "voice_pipe" in data

    def test_voice_pipe_metrics(self) -> None:
        """[FACT] Tracks voice-pipe connect/disconnect and turn-boundary counters."""
        metrics = LiveMetrics()
        metrics.record_ws_connect()
        metrics.record_turn_boundary()
        metrics.record_ws_disconnect()

        data = metrics.to_dict()
        assert data["voice_pipe"]["ws_connect_count"] == 1
        assert data["voice_pipe"]["ws_disconnect_count"] == 1
        assert data["voice_pipe"]["turn_boundary_count"] == 1

    def test_security_event_metrics(self) -> None:
        """[FACT] Tracks auth failures and throttling events for observability."""
        metrics = LiveMetrics()
        metrics.record_rate_limit("operator")
        metrics.record_rate_limit("auth")
        metrics.record_rate_limit("audio")
        metrics.record_auth_failure("operator")
        metrics.record_auth_failure("websocket")

        data = metrics.to_dict()
        assert data["security_events"]["operator_rate_limit_count"] == 1
        assert data["security_events"]["auth_rate_limit_count"] == 1
        assert data["security_events"]["audio_rate_limit_count"] == 1
        assert data["security_events"]["operator_auth_failure_count"] == 1
        assert data["security_events"]["websocket_auth_failure_count"] == 1


class TestReceiptStore:
    """[FACT] Test suite for ReceiptStore."""

    def test_add_receipt(self) -> None:
        """[FACT] Adds receipt to store."""
        store = ReceiptStore(max_receipts=10)
        receipt = Receipt(
            receipt_id="test_001",
            timestamp="2024-01-01T00:00:00",
            content="Test content",
            valid=True,
            session_id="session_1",
        )

        store.add(receipt)

        assert len(store.get_all()) == 1
        result = store.get_by_id("test_001")
        assert result is not None
        assert result.content == "Test content"

    def test_get_all(self) -> None:
        """[FACT] Retrieves all receipts."""
        store = ReceiptStore(max_receipts=10)

        # Add receipts
        store.add(Receipt("r1", "2024-01-01", "Valid", True, None, "s1"))
        store.add(Receipt("r2", "2024-01-01", "Invalid", False, "DRIFT-A", "s1"))

        all_receipts = store.get_all()
        assert len(all_receipts) == 2

    def test_get_by_id(self) -> None:
        """[FACT] Retrieves receipt by ID."""
        store = ReceiptStore(max_receipts=10)
        store.add(Receipt("r1", "2024-01-01", "Content", True, None, "s1"))

        found = store.get_by_id("r1")
        assert found is not None
        assert found.content == "Content"

        not_found = store.get_by_id("nonexistent")
        assert not_found is None

    def test_get_stats(self) -> None:
        """[FACT] Returns store statistics."""
        store = ReceiptStore(max_receipts=10)
        store.add(Receipt("r1", "2024-01-01", "Content", True, None, "s1"))

        stats = store.get_stats()
        assert stats["total"] == 1
        assert stats["backend"] == "memory"
        assert stats["enabled"] is False

    def test_receipt_store_local_persistence_round_trip(self, monkeypatch, tmp_path) -> None:
        """[FACT] Local receipt persistence restores recent receipts across store instances."""
        ledger_path = tmp_path / "receipts.jsonl"
        monkeypatch.setenv("HELIX_RECEIPT_PERSISTENCE", "local")
        monkeypatch.setenv("HELIX_RECEIPT_STORE_PATH", str(ledger_path))

        store = ReceiptStore(max_receipts=10)
        store.add(Receipt("persisted", "2024-01-01", "Saved", True, None, "s1"))

        restored_store = ReceiptStore(max_receipts=10)
        restored = restored_store.get_by_id("persisted")

        assert restored is not None
        assert restored.content == "Saved"
        assert restored_store.get_stats()["backend"] == "local"
        assert ledger_path.exists()

    def test_receipt_store_overflow(self) -> None:
        """[FACT] Removes oldest when exceeding max size."""
        store = ReceiptStore(max_receipts=3)

        for i in range(5):
            store.add(Receipt(f"r{i}", "2024-01-01", f"Content {i}", True, None, "s1"))

        assert len(store.get_all()) == 3
        # Oldest (r0, r1) should be removed
        assert store.get_by_id("r0") is None
        assert store.get_by_id("r1") is None
        assert store.get_by_id("r2") is not None


class TestGeminiTextClientCache:
    """[FACT] Test suite for client caching logic."""

    def test_get_gemini_text_client_caching(self, monkeypatch: Any) -> None:
        """[FACT] Client is cached and reused."""
        monkeypatch.setenv("GEMINI_API_KEY", "test_key_12345")

        # Clear cache first
        import helix_code.live_demo_server as server

        server.gemini_text_client = None
        server.gemini_cached_key = None

        client1 = get_gemini_text_client()
        client2 = get_gemini_text_client()

        # Should be same instance
        assert client1 is client2

    def test_get_gemini_text_client_key_change(self, monkeypatch: Any) -> None:
        """[FACT] New client created when key changes."""
        monkeypatch.setenv("GEMINI_API_KEY", "key_1")

        import helix_code.live_demo_server as server

        server.gemini_text_client = None
        server.gemini_cached_key = None

        client1 = get_gemini_text_client()

        # Simulate key change
        monkeypatch.setenv("GEMINI_API_KEY", "key_2")
        server.gemini_cached_key = "key_1"  # Force mismatch

        client2 = get_gemini_text_client()

        # Should be different instances
        assert client1 is not client2


class TestReceiptDataclass:
    """[FACT] Test Receipt dataclass."""

    def test_receipt_defaults(self) -> None:
        """[FACT] Receipt has correct default values."""
        r = Receipt("r1", "2024-01-01", "Content", True)

        assert r.receipt_id == "r1"
        assert r.timestamp == "2024-01-01"
        assert r.content == "Content"
        assert r.valid is True
        assert r.drift_code is None
        assert r.session_id == ""  # Default

    def test_receipt_with_drift(self) -> None:
        """[FACT] Receipt captures drift code."""
        r = Receipt("r1", "2024-01-01", "Content", False, "DRIFT-A", "s1")

        assert r.valid is False
        assert r.drift_code == "DRIFT-A"
        assert r.session_id == "s1"


class TestAudioIngressRateLimiting:
    """[FACT] Test audio ingress connection throttling."""

    def test_audio_ingress_rate_limit_rejects_bursts(self, monkeypatch: Any) -> None:
        """[FACT] Audio ingress allows the first connection and throttles the next in-window attempt."""
        monkeypatch.setenv("HELIX_AUDIO_INGRESS_MAX_CONNECTIONS", "1")
        monkeypatch.setenv("HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS", "60")

        import helix_code.live_demo_server as server

        monkeypatch.setattr(
            server,
            "audio_ingress_rate_limiter",
            SlidingWindowRateLimiter(now_fn=lambda: 300.0),
        )

        class StubClient:
            host = "203.0.113.10"

        class StubWebSocket:
            headers: dict[str, str] = {}
            client = StubClient()

        first_allowed, _ = _check_audio_ingress_rate_limit(StubWebSocket())
        second_allowed, retry_after = _check_audio_ingress_rate_limit(StubWebSocket())

        assert first_allowed is True
        assert second_allowed is False
        assert retry_after > 0


class TestStandaloneAdminWebsocketAuthorization:
    """[FACT] Test standalone WebSocket admin gating telemetry."""

    def test_missing_websocket_admin_token_does_not_increment_failure_metric(
        self, monkeypatch: Any
    ) -> None:
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")
        monkeypatch.setattr(live_demo_server, "metrics", LiveMetrics())

        assert live_demo_server._require_admin_websocket({}) is False
        assert live_demo_server.metrics.websocket_auth_failure_count == 0

    def test_wrong_websocket_admin_token_increments_failure_metric(self, monkeypatch: Any) -> None:
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")
        monkeypatch.setattr(live_demo_server, "metrics", LiveMetrics())

        assert (
            live_demo_server._require_admin_websocket({"x-helix-admin-token": "wrong-token"})
            is False
        )
        assert live_demo_server.metrics.websocket_auth_failure_count == 1


class TestAudioAuditAuthorization:
    """[FACT] Test suite for audio audit authorization gates."""

    def test_authorization_passes_without_policy(self, monkeypatch: Any) -> None:
        """[FACT] If no policy is set, connection is allowed."""
        monkeypatch.delenv("AUDIO_AUDIT_TOKEN", raising=False)
        monkeypatch.delenv("AUDIO_AUDIT_ALLOWED_ORIGINS", raising=False)

        class StubWebSocket:
            query_params: dict[str, str] = {}
            headers: dict[str, str] = {}

        assert _is_audio_audit_authorized(StubWebSocket()) is True

    def test_authorization_rejects_missing_token_without_counting_auth_failure(
        self, monkeypatch: Any
    ) -> None:
        """[FACT] Missing audio-audit tokens are denied without inflating failure metrics."""
        monkeypatch.setenv("AUDIO_AUDIT_TOKEN", "s3cr3t")
        monkeypatch.setattr(live_demo_server, "metrics", LiveMetrics())

        class StubWebSocket:
            query_params: dict[str, str] = {}
            headers: dict[str, str] = {}

        assert _is_audio_audit_authorized(StubWebSocket()) is False
        assert live_demo_server.metrics.websocket_auth_failure_count == 0

    def test_authorization_rejects_bad_token(self, monkeypatch: Any) -> None:
        """[FACT] Wrong token is denied."""
        monkeypatch.setenv("AUDIO_AUDIT_TOKEN", "s3cr3t")
        monkeypatch.setattr(live_demo_server, "metrics", LiveMetrics())

        class StubWebSocket:
            query_params: dict[str, str] = {}
            headers = {"x-audio-audit-token": "wrong"}

        assert _is_audio_audit_authorized(StubWebSocket()) is False
        assert live_demo_server.metrics.websocket_auth_failure_count == 1

    def test_authorization_rejects_bad_origin(self, monkeypatch: Any) -> None:
        """[FACT] Origin not in allowlist is denied."""
        monkeypatch.delenv("AUDIO_AUDIT_TOKEN", raising=False)
        monkeypatch.setenv("AUDIO_AUDIT_ALLOWED_ORIGINS", "https://helixprojectai.com")

        class StubWebSocket:
            query_params: dict[str, str] = {}
            headers = {"origin": "https://evil.example"}

        assert _is_audio_audit_authorized(StubWebSocket()) is False

    def test_authorization_accepts_token_and_origin(self, monkeypatch: Any) -> None:
        """[FACT] Valid token + origin passes."""
        monkeypatch.setenv("AUDIO_AUDIT_TOKEN", "s3cr3t")
        monkeypatch.setenv("AUDIO_AUDIT_ALLOWED_ORIGINS", "https://helixprojectai.com")

        class StubWebSocket:
            query_params: dict[str, str] = {}
            headers = {
                "origin": "https://helixprojectai.com",
                "x-audio-audit-token": "s3cr3t",
            }

        assert _is_audio_audit_authorized(StubWebSocket()) is True


def test_generate_session_id_is_collision_resistant() -> None:
    """[FACT] Session ID generation uses UUIDs and should not collide in normal runs."""
    values = {_generate_session_id("demo") for _ in range(200)}
    assert len(values) == 200
    assert all(v.startswith("demo_") for v in values)
