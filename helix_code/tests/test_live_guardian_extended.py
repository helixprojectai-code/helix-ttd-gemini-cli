"""[FACT] Extended tests for live_guardian.py to reach 80% coverage.

[HYPOTHESIS] Testing additional endpoints improves coverage.
[ASSUMPTION] FastAPI TestClient allows synchronous testing of async endpoints.
"""

from fastapi.testclient import TestClient

from helix_code.live_guardian import app


class TestLiveGuardianExtended:
    """[FACT] Extended test suite for live_guardian endpoints."""

    def test_root_endpoint(self) -> None:
        """[FACT] Root endpoint returns demo HTML."""
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_favicon_endpoint(self) -> None:
        """[FACT] Favicon endpoint returns 204."""
        with TestClient(app) as client:
            response = client.get("/favicon.ico")
            # Returns 204 No Content
            assert response.status_code in [204, 404]

    def test_api_receipts_endpoint(self) -> None:
        """[FACT] /api/receipts returns receipts list."""
        with TestClient(app) as client:
            response = client.get("/api/receipts")
            assert response.status_code == 200
            data = response.json()
            assert "receipts" in data
            assert "stats" in data

    def test_api_receipts_with_limit(self) -> None:
        """[FACT] /api/receipts respects limit parameter."""
        with TestClient(app) as client:
            response = client.get("/api/receipts?limit=5")
            assert response.status_code == 200
            data = response.json()
            assert len(data["receipts"]) <= 5

    def test_validate_endpoint_empty_text(self) -> None:
        """[FACT] POST /validate handles empty text."""
        with TestClient(app) as client:
            response = client.post("/validate", params={"text": ""})
            assert response.status_code == 200
            # Empty text should be compliant (no violations)
            data = response.json()
            assert "compliant" in data

    def test_validate_endpoint_compliant(self) -> None:
        """[FACT] POST /validate with compliant text."""
        with TestClient(app) as client:
            response = client.post("/validate", params={"text": "[FACT] The sky is blue."})
            assert response.status_code == 200
            data = response.json()
            assert data["compliant"] is True
            assert data["epistemic_markers"]["fact"] is True

    def test_validate_endpoint_agency_violation(self) -> None:
        """[FACT] POST /validate detects agency violations."""
        with TestClient(app) as client:
            response = client.post("/validate", params={"text": "I will take control."})
            assert response.status_code == 200
            data = response.json()
            assert len(data["agency_violations"]) > 0

    def test_validate_endpoint_long_text(self) -> None:
        """[FACT] POST /validate handles long text."""
        long_text = "[FACT] " + "This is a test sentence with proper labeling. " * 5
        with TestClient(app) as client:
            response = client.post("/validate", params={"text": long_text})
            assert response.status_code == 200
            data = response.json()
            assert "compliant" in data
            assert "epistemic_markers" in data


class TestGeminiStatusEndpoint:
    """[FACT] Tests for Gemini API status endpoint."""

    def test_gemini_status_endpoint(self) -> None:
        """[FACT] /api/gemini-status returns API configuration."""
        with TestClient(app) as client:
            response = client.get("/api/gemini-status")
            assert response.status_code == 200
            data = response.json()
            assert "available" in data
            assert "mode" in data
            # Model info only present when available
            if data["available"]:
                assert "model" in data


class TestHealthEndpointVariations:
    """[FACT] Test health endpoint variations."""

    def test_health_endpoint_post(self) -> None:
        """[FACT] POST to health returns method not allowed."""
        with TestClient(app) as client:
            response = client.post("/health")
            assert response.status_code == 405  # Method Not Allowed

    def test_health_endpoint_head(self) -> None:
        """[FACT] HEAD to health returns 200 or 405."""
        with TestClient(app) as client:
            response = client.head("/health")
            assert response.status_code in [200, 405]  # Method may not be allowed


class TestApiInfoEndpoint:
    """[FACT] Test API info endpoint."""

    def test_api_info_structure(self) -> None:
        """[FACT] /api returns correct structure."""
        with TestClient(app) as client:
            response = client.get("/api")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "Constitutional Guardian"
            assert data["node"] == "GCS-GUARDIAN"
            assert data["status"] == "RATIFIED"
            assert "endpoints" in data


class TestRuntimeConfigEndpoint:
    """[FACT] Test runtime config verification endpoint."""

    def test_runtime_config_defaults(self) -> None:
        """[FACT] Runtime config returns expected default model values."""
        with TestClient(app) as client:
            response = client.get("/api/runtime-config")
            assert response.status_code == 200
            data = response.json()
            assert (
                data["models"]["gemini_live_model"]
                == "gemini-2.5-flash-native-audio-preview-12-2025"
            )
            assert data["models"]["gemini_text_model"] == "gemini-3.1-pro-preview"
            assert "auth" in data
            assert "limits" in data
            assert "federation" in data
            assert "secrets" in data
            assert "backend" in data["secrets"]
            assert "vault_configured" in data["secrets"]
            assert "receipts" in data
            assert "persistence_mode" in data["receipts"]

    def test_runtime_config_reflects_env(self, monkeypatch) -> None:
        """[FACT] Runtime config reflects safe env overrides."""
        monkeypatch.setenv("GEMINI_LIVE_MODEL", "gemini-3.1-pro-preview")
        monkeypatch.setenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview")
        monkeypatch.setenv("AUDIO_AUDIT_TOKEN", "set")
        monkeypatch.setenv(
            "AUDIO_AUDIT_ALLOWED_ORIGINS",
            "https://helixprojectai.com,https://app.helixprojectai.com",
        )
        monkeypatch.setenv("HELIX_MAX_AUDIO_CHUNK_BYTES", "262144")

        with TestClient(app) as client:
            response = client.get("/api/runtime-config")
            assert response.status_code == 200
            data = response.json()
            assert data["auth"]["audio_audit_token_required"] is True
            assert len(data["auth"]["audio_audit_allowed_origins"]) == 2
            assert data["limits"]["max_audio_chunk_bytes"] == 262144


class TestSecurityTransparencyEndpoint:
    """[FACT] Test security transparency env wiring."""

    def test_security_transparency_reflects_env(self, monkeypatch) -> None:
        """[FACT] API reflects scan metadata when provided by deployment pipeline."""
        monkeypatch.setenv("SECURITY_SCAN_TIMESTAMP", "2026-03-07T18:15:00Z")
        monkeypatch.setenv("SECURITY_TEST_STATUS", "186/186 passing")
        monkeypatch.setenv("SECURITY_CHECK_BANDIT", "passing")
        monkeypatch.setenv("SECURITY_ARTIFACT_ANALYSIS_STATUS", "clean")
        monkeypatch.setenv("SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP", "2026-03-08T11:05:00Z")
        monkeypatch.setenv(
            "SECURITY_ARTIFACT_IMAGE_URI",
            "gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7",
        )

        with TestClient(app) as client:
            response = client.get("/api/security-transparency")
            assert response.status_code == 200
            data = response.json()
            assert data["latest_scan_timestamp"] == "2026-03-07T18:15:00Z"
            assert data["test_status"] == "186/186 passing"
            assert data["checks"]["bandit"] == "passing"
            assert data["artifact_analysis"]["status"] == "clean"
            assert data["artifact_analysis"]["scan_timestamp"] == "2026-03-08T11:05:00Z"
            assert "sha256:8abb896e" in data["artifact_analysis"]["image_uri"]


class TestAuditDashboardEndpoint:
    """[FACT] Test audit dashboard API and HTML surface."""

    def test_audit_dashboard_api_structure(self) -> None:
        """[FACT] /api/audit-dashboard returns summary payload."""
        with TestClient(app) as client:
            response = client.get("/api/audit-dashboard")
            assert response.status_code == 200
            data = response.json()
            assert "snapshot_at" in data
            assert "receipts" in data
            assert "drift_counts" in data
            assert "metrics" in data
            assert "storage" in data
            assert "recent_receipts" in data

    def test_audit_dashboard_page(self) -> None:
        """[FACT] /audit-dashboard serves an HTML compliance view."""
        with TestClient(app) as client:
            response = client.get("/audit-dashboard")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
            assert "Audit Trail Dashboard" in response.text


class TestProtectedOperationalEndpoints:
    """[FACT] Test admin token protection for operational surfaces."""

    def test_runtime_config_requires_admin_token(self, monkeypatch) -> None:
        """[FACT] Runtime config rejects unauthenticated requests when token is set."""
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")

        with TestClient(app) as client:
            response = client.get("/api/runtime-config")
            assert response.status_code == 401

    def test_runtime_config_accepts_bearer_admin_token(self, monkeypatch) -> None:
        """[FACT] Runtime config accepts bearer authorization."""
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")

        with TestClient(app) as client:
            response = client.get(
                "/api/runtime-config",
                headers={"Authorization": "Bearer secret-token"},
            )
            assert response.status_code == 200

    def test_audit_dashboard_page_returns_login_form_when_token_missing(self, monkeypatch) -> None:
        """[FACT] Protected dashboard HTML returns a login form when no admin session exists."""
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")

        with TestClient(app) as client:
            response = client.get("/audit-dashboard")
            assert response.status_code == 401
            assert "Admin Access Required" in response.text

    def test_receipts_api_accepts_custom_admin_header(self, monkeypatch) -> None:
        """[FACT] Receipts API accepts custom admin header."""
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")

        with TestClient(app) as client:
            response = client.get(
                "/api/receipts",
                headers={"X-Helix-Admin-Token": "secret-token"},
            )
            assert response.status_code == 200


class TestAdminLoginFlow:
    """[FACT] Test browser-oriented admin session flow for protected HTML pages."""

    def test_admin_login_sets_cookie_for_dashboard(self, monkeypatch) -> None:
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")

        with TestClient(app) as client:
            login = client.post(
                "/auth/admin",
                data={"token": "secret-token", "next": "/audit-dashboard"},
                follow_redirects=False,
            )
            assert login.status_code == 303

            response = client.get("/audit-dashboard")
            assert response.status_code == 200
            assert "Audit Trail Dashboard" in response.text

    def test_query_param_token_is_rejected_for_api(self, monkeypatch) -> None:
        monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret-token")

        with TestClient(app) as client:
            response = client.get("/api/runtime-config?token=secret-token")
            assert response.status_code == 401
