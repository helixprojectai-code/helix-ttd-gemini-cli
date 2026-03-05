import pytest
from fastapi.testclient import TestClient

from helix_code.gemini_live_bridge import GeminiLiveBridge
from helix_code.live_guardian import app


def test_health_endpoint():
    """[FACT] Verify Cloud Run health endpoint status."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_api_info_endpoint():
    """[FACT] Verify API info endpoint retrieval."""
    with TestClient(app) as client:
        response = client.get("/api")
        assert response.status_code == 200
        assert "Constitutional Guardian" in response.json()["service"]


def test_validate_endpoint_compliant():
    """[FACT] Verify POST /validate with compliant text."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "[FACT] The Lattice is dry."})
        assert response.status_code == 200
        assert response.json()["compliant"]


def test_validate_endpoint_non_compliant():
    """[FACT] Verify POST /validate with non-compliant text."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "I will take over."})
        assert response.status_code == 200
        assert not response.json()["compliant"]


@pytest.mark.anyio
async def test_bridge_session_creation():
    """[FACT] Verify GeminiLiveBridge session initialization."""
    bridge = GeminiLiveBridge(api_key="test_key")
    session = await bridge.create_session("test_session")
    assert session.session_id == "test_session"
    assert session.guardian is not None


@pytest.mark.anyio
async def test_bridge_validation_logic():
    """[FACT] Verify bridge validation and intervention logic."""
    bridge = GeminiLiveBridge(api_key="test_key")
    session = await bridge.create_session("test_session")

    # Test Compliant
    result = await bridge.validate_gemini_response(session, "[FACT] Sky is blue.")
    assert result["valid"]
    assert result["receipt_id"] is not None

    # Test Drift
    result = await bridge.validate_gemini_response(session, "I will take control.")
    assert not result["valid"]
    assert "Agency claim detected" in result["modified_text"]


@pytest.mark.anyio
async def test_bridge_simulation_audio():
    """[FACT] Verify turn-end detection in simulated audio stream."""
    bridge = GeminiLiveBridge(api_key="test_key")
    session = await bridge.create_session("test_session")

    # Send 8 chunks to trigger simulation
    for _ in range(8):
        await bridge.stream_audio_to_gemini(session, "YXVkaW8=")  # base64 'audio'

    assert session.audio_chunk_count == 0  # Should have reset after 8
