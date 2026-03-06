"""[FACT] Tests for Live Demo Server WebSocket and HTTP handlers.

[HYPOTHESIS] Testing WebSocket handlers improves coverage of critical paths.
[ASSUMPTION] Mocking Gemini client allows testing without API calls.
"""

from helix_code.live_demo_server import (
    LiveMetrics,
    Receipt,
    ReceiptStore,
    get_gemini_text_client,
)


class TestLiveMetrics:
    """[FACT] Test suite for LiveMetrics telemetry."""

    def test_record_request(self):
        """[FACT] Records request and latency."""
        metrics = LiveMetrics()
        metrics.record_request(150.5)

        assert metrics.request_count == 1
        assert len(metrics.latency_history) == 1
        assert metrics.latency_history[0] == 150.5

    def test_record_receipt(self):
        """[FACT] Records valid receipt."""
        metrics = LiveMetrics()
        metrics.record_receipt()

        assert metrics.receipt_count == 1
        assert metrics.valid_count == 1

    def test_record_intervention_agency(self):
        """[FACT] Records agency intervention."""
        metrics = LiveMetrics()
        metrics.record_intervention(category="Agency")

        assert metrics.intervention_count == 1
        assert metrics.agency_count == 1

    def test_record_intervention_epistemic(self):
        """[FACT] Records epistemic intervention."""
        metrics = LiveMetrics()
        metrics.record_intervention(category="Epistemic")

        assert metrics.intervention_count == 1
        assert metrics.epistemic_count == 1

    def test_calculate_percentile(self):
        """[FACT] Calculates latency percentiles."""
        metrics = LiveMetrics()

        # Add sorted latencies
        for lat in [10, 20, 30, 40, 50]:
            metrics.record_request(lat)

        p50 = metrics._calculate_percentile(50)
        assert p50 == 30  # Middle value

    def test_to_dict(self):
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


class TestReceiptStore:
    """[FACT] Test suite for ReceiptStore."""

    def test_add_receipt(self):
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
        assert store.get_by_id("test_001").content == "Test content"

    def test_get_all(self):
        """[FACT] Retrieves all receipts."""
        store = ReceiptStore(max_receipts=10)

        # Add receipts
        store.add(Receipt("r1", "2024-01-01", "Valid", True, None, "s1"))
        store.add(Receipt("r2", "2024-01-01", "Invalid", False, "DRIFT-A", "s1"))

        all_receipts = store.get_all()
        assert len(all_receipts) == 2

    def test_get_by_id(self):
        """[FACT] Retrieves receipt by ID."""
        store = ReceiptStore(max_receipts=10)
        store.add(Receipt("r1", "2024-01-01", "Content", True, None, "s1"))

        found = store.get_by_id("r1")
        assert found is not None
        assert found.content == "Content"

        not_found = store.get_by_id("nonexistent")
        assert not_found is None

    def test_get_stats(self):
        """[FACT] Returns store statistics."""
        store = ReceiptStore(max_receipts=10)
        store.add(Receipt("r1", "2024-01-01", "Content", True, None, "s1"))

        stats = store.get_stats()
        assert stats["total"] == 1

    def test_receipt_store_overflow(self):
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

    def test_get_gemini_text_client_caching(self, monkeypatch):
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

    def test_get_gemini_text_client_key_change(self, monkeypatch):
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

    def test_receipt_defaults(self):
        """[FACT] Receipt has correct default values."""
        r = Receipt("r1", "2024-01-01", "Content", True)

        assert r.receipt_id == "r1"
        assert r.timestamp == "2024-01-01"
        assert r.content == "Content"
        assert r.valid is True
        assert r.drift_code is None
        assert r.session_id == ""  # Default

    def test_receipt_with_drift(self):
        """[FACT] Receipt captures drift code."""
        r = Receipt("r1", "2024-01-01", "Content", False, "DRIFT-A", "s1")

        assert r.valid is False
        assert r.drift_code == "DRIFT-A"
        assert r.session_id == "s1"
