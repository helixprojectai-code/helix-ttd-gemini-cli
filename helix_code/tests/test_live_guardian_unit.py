import base64

import pytest
from fastapi.testclient import TestClient

from helix_code.gemini_live_bridge import GeminiLiveBridge
from helix_code.live_guardian import app


def _pcm_chunk_base64(samples: int = 320, amplitude: int = 0) -> str:
    """Create a 16-bit PCM mono chunk encoded as base64."""
    sample = int(amplitude).to_bytes(2, byteorder="little", signed=True)
    pcm = sample * samples
    return base64.b64encode(pcm).decode("ascii")


class DummyWS:
    def __init__(self) -> None:
        self.messages: list[dict] = []

    async def send_json(self, payload: dict) -> None:
        self.messages.append(payload)


def test_health_endpoint() -> None:
    """[FACT] Verify Cloud Run health endpoint status."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_api_info_endpoint() -> None:
    """[FACT] Verify API info endpoint retrieval."""
    with TestClient(app) as client:
        response = client.get("/api")
        assert response.status_code == 200
        assert "Constitutional Guardian" in response.json()["service"]


def test_security_transparency_page() -> None:
    """[FACT] Verify security transparency HTML page is served."""
    with TestClient(app) as client:
        response = client.get("/security-transparency")
        assert response.status_code == 200
        assert "Security Transparency" in response.text
        assert "Latest Scan Timestamp" in response.text


def test_security_transparency_api() -> None:
    """[FACT] Verify machine-readable transparency endpoint."""
    with TestClient(app) as client:
        response = client.get("/api/security-transparency")
        assert response.status_code == 200
        payload = response.json()
        assert "latest_scan_timestamp" in payload
        assert "checks" in payload


def test_validate_endpoint_compliant() -> None:
    """[FACT] Verify POST /validate with compliant text."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "[FACT] The Lattice is dry."})
        assert response.status_code == 200
        assert response.json()["compliant"]


def test_validate_endpoint_non_compliant() -> None:
    """[FACT] Verify POST /validate with non-compliant text."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "I will take over."})
        assert response.status_code == 200
        assert not response.json()["compliant"]


@pytest.mark.anyio
async def test_bridge_session_creation() -> None:
    """[FACT] Verify GeminiLiveBridge session initialization."""
    bridge = GeminiLiveBridge(api_key="test_key")
    session = await bridge.create_session("test_session")
    assert session.session_id == "test_session"
    assert session.guardian is not None


@pytest.mark.anyio
async def test_bridge_validation_logic() -> None:
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
async def test_bridge_turn_end_by_silence(monkeypatch: pytest.MonkeyPatch) -> None:
    """[FACT] Silence streak should finalize a turn once minimum duration is met."""
    monkeypatch.setenv("HELIX_AUDIO_SIMULATION", "1")
    bridge = GeminiLiveBridge(api_key="test_key")
    bridge.client = None
    bridge.min_turn_ms = 60
    bridge.max_turn_ms = 5000
    bridge.silence_chunks_for_turn_end = 2

    ws = DummyWS()
    session = await bridge.create_session("test_session")
    session.client_ws = ws

    silent_chunk = _pcm_chunk_base64(samples=320, amplitude=0)  # 20ms
    for _ in range(4):
        await bridge.stream_audio_to_gemini(session, silent_chunk)

    assert any("Turn boundary detected" in m.get("message", "") for m in ws.messages)


@pytest.mark.anyio
async def test_bridge_turn_end_by_gap(monkeypatch: pytest.MonkeyPatch) -> None:
    """[FACT] A large inter-chunk gap should finalize a turn when long enough."""
    monkeypatch.setenv("HELIX_AUDIO_SIMULATION", "1")
    bridge = GeminiLiveBridge(api_key="test_key")
    bridge.client = None
    bridge.min_turn_ms = 20
    bridge.chunk_gap_ms = 1

    ws = DummyWS()
    session = await bridge.create_session("test_session")
    session.client_ws = ws

    speech_chunk = _pcm_chunk_base64(samples=320, amplitude=1200)
    await bridge.stream_audio_to_gemini(session, speech_chunk)
    # Force an artificial gap
    session.last_chunk_ts = 0.0
    await bridge.stream_audio_to_gemini(session, speech_chunk)

    assert any("chunk_gap" in m.get("message", "") for m in ws.messages)


@pytest.mark.anyio
async def test_bridge_turn_end_by_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """[FACT] Max-turn timeout should finalize regardless of silence."""
    monkeypatch.setenv("HELIX_AUDIO_SIMULATION", "1")
    bridge = GeminiLiveBridge(api_key="test_key")
    bridge.client = None
    bridge.min_turn_ms = 1000
    bridge.max_turn_ms = 40

    ws = DummyWS()
    session = await bridge.create_session("test_session")
    session.client_ws = ws

    speech_chunk = _pcm_chunk_base64(samples=320, amplitude=1000)
    for _ in range(3):
        await bridge.stream_audio_to_gemini(session, speech_chunk)

    assert any("max_turn_timeout" in m.get("message", "") for m in ws.messages)


@pytest.mark.anyio
async def test_bridge_simulation_fallback_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    """[FACT] Simulation fallback should not emit random agency text."""
    monkeypatch.setenv("HELIX_AUDIO_SIMULATION", "1")
    bridge = GeminiLiveBridge(api_key="test_key")
    bridge.client = None
    bridge.min_turn_ms = 20
    bridge.silence_chunks_for_turn_end = 1

    ws = DummyWS()
    session = await bridge.create_session("test_session")
    session.client_ws = ws

    await bridge.stream_audio_to_gemini(session, _pcm_chunk_base64(samples=320, amplitude=0))

    delivered = [
        m.get("delivered", "") for m in ws.messages if m.get("type") == "validated_response"
    ]
    assert delivered
    assert delivered[0] == "[ASSUMPTION] Simulation fallback transcript placeholder."


@pytest.mark.anyio
async def test_bridge_explicit_audio_end(monkeypatch: pytest.MonkeyPatch) -> None:
    """[FACT] Explicit mic-stop signal should deterministically finalize the turn."""
    monkeypatch.setenv("HELIX_AUDIO_SIMULATION", "1")
    bridge = GeminiLiveBridge(api_key="test_key")
    bridge.client = None

    ws = DummyWS()
    session = await bridge.create_session("test_session")
    session.client_ws = ws

    await bridge.finalize_audio_turn(session, reason="mic_stop")

    assert any("mic_stop" in m.get("message", "") for m in ws.messages)
    delivered = [
        m.get("delivered", "") for m in ws.messages if m.get("type") == "validated_response"
    ]
    assert delivered
    assert delivered[0] == "[ASSUMPTION] Simulation fallback transcript placeholder."


def test_bridge_normalize_live_model_name() -> None:
    """[FACT] Live model names are normalized by removing optional models/ prefix."""
    bridge = GeminiLiveBridge(api_key="test_key")
    assert bridge._normalize_live_model_name(
        "models/gemini-2.5-flash-native-audio-preview-12-2025"
    ) == ("gemini-2.5-flash-native-audio-preview-12-2025")
    assert bridge._normalize_live_model_name("gemini-2.5-flash-native-audio-preview-12-2025") == (
        "gemini-2.5-flash-native-audio-preview-12-2025"
    )
