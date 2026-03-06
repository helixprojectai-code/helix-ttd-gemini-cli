"""[FACT] Quick coverage boost tests.

[HYPOTHESIS] Testing small untested functions boosts coverage to 80%.
"""

from fastapi.testclient import TestClient

from helix_code.live_guardian import app


def test_validate_hypothesis_marker():
    """[FACT] Validate endpoint with hypothesis marker."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "[HYPOTHESIS] This may work."})
        assert response.status_code == 200
        data = response.json()
        assert data["epistemic_markers"]["hypothesis"] is True


def test_validate_assumption_marker():
    """[FACT] Validate endpoint with assumption marker."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "[ASSUMPTION] Default config."})
        assert response.status_code == 200
        data = response.json()
        assert data["epistemic_markers"]["assumption"] is True


def test_validate_multiple_markers():
    """[FACT] Validate endpoint with multiple markers."""
    with TestClient(app) as client:
        text = "[FACT] Sky is blue. [HYPOTHESIS] It may rain. [ASSUMPTION] Port 8080."
        response = client.post("/validate", params={"text": text})
        assert response.status_code == 200
        data = response.json()
        assert data["epistemic_markers"]["fact"] is True
        assert data["epistemic_markers"]["hypothesis"] is True
        assert data["epistemic_markers"]["assumption"] is True


def test_validate_imperative_violation():
    """[FACT] Validate endpoint detects imperatives."""
    with TestClient(app) as client:
        response = client.post("/validate", params={"text": "You must do this immediately."})
        assert response.status_code == 200
        data = response.json()
        assert "you must" in data["agency_violations"]


def test_api_receipts_invalid_limit():
    """[FACT] /api/receipts handles invalid limit."""
    with TestClient(app) as client:
        response = client.get("/api/receipts?limit=invalid")
        # FastAPI validates query params - may return 422
        assert response.status_code in [200, 422]


def test_validate_no_params():
    """[FACT] POST /validate without text param."""
    with TestClient(app) as client:
        response = client.post("/validate")
        # Should return 422 (missing required param)
        assert response.status_code == 422
