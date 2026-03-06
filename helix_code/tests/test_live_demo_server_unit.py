from helix_code.live_demo_server import LiveMetrics, Receipt, ReceiptStore


def test_live_metrics_recording() -> None:
    """[FACT] Verify real-time metric recording and averaging."""
    metrics = LiveMetrics()
    metrics.record_request(100.0)
    metrics.record_receipt()
    metrics.record_intervention(category="Agency")

    data = metrics.to_dict()
    assert data["request_count"] == 1
    assert data["receipt_count"] == 1
    assert data["intervention_count"] == 1
    assert data["categories"]["agency"] == 1
    assert data["latency_avg"] == 100.0


def test_receipt_store() -> None:
    """[FACT] Verify in-memory receipt storage and retrieval."""
    store = ReceiptStore(max_receipts=5)
    receipt = Receipt(
        receipt_id="r1", timestamp="2026-03-05T10:00:00", content="[FACT] Test", valid=True
    )
    store.add(receipt)

    assert len(store.get_all()) == 1
    receipt_result = store.get_by_id("r1")
    assert receipt_result is not None
    assert receipt_result.content == "[FACT] Test"
    assert store.get_stats()["total"] == 1


def test_receipt_store_overflow() -> None:
    """[FACT] Verify deque-based store correctly prunes old entries on overflow."""
    store = ReceiptStore(max_receipts=2)
    for i in range(3):
        store.add(Receipt(f"r{i}", "", "", True))

    assert len(store.get_all()) == 2
    assert store.get_by_id("r0") is None  # Should have been pushed out
    assert store.get_by_id("r2") is not None
