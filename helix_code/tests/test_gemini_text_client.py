"""[FACT] Tests for Gemini Text Client REST implementation.

[HYPOTHESIS] Direct REST API calls are more reliable than SDK.
[ASSUMPTION] Mocking httpx allows testing without API keys.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from helix_code.gemini_text_client import GeminiTextClient, create_gemini_text_client
from helix_code.model_armor_client import ModelArmorClient, ModelArmorScreenResult


@pytest.fixture(autouse=True)
def reset_secret_resolution_state(monkeypatch: Any) -> None:
    """[FACT] Ensure tests run with deterministic env-based secret resolution."""
    monkeypatch.delenv("HELIX_SECRET_BACKEND", raising=False)
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    monkeypatch.delenv("VAULT_TOKEN", raising=False)
    monkeypatch.delenv("VAULT_NAMESPACE", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_VAULT_PATH", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_VAULT_FIELD", raising=False)

    import sys

    for module_name in ("secret_resolver", "helix_code.secret_resolver"):
        module = sys.modules.get(module_name)
        if module is not None and hasattr(module, "_secret_cache"):
            module._secret_cache.clear()  # type: ignore[attr-defined]


class TestGeminiTextClient:
    """[FACT] Test suite for Gemini REST client."""

    def test_init_without_api_key(self, monkeypatch: Any) -> None:
        """[FACT] Client initializes but unavailable without key."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        client = GeminiTextClient(api_key=None)
        assert not client.is_available()
        assert client.api_key is None

    def test_init_with_api_key(self) -> None:
        """[FACT] Client initializes and available with key."""
        client = GeminiTextClient(api_key="test_key_12345")
        assert client.is_available()
        assert client.api_key == "test_key_12345"
        assert client.model == "gemini-3.1-pro-preview"

    def test_init_uses_env_var(self, monkeypatch: Any) -> None:
        """[FACT] Client reads API key from environment."""
        monkeypatch.setenv("GEMINI_API_KEY", "env_key_12345")
        client = create_gemini_text_client()
        assert client.is_available()
        assert client.api_key == "env_key_12345"

    @pytest.mark.anyio
    async def test_generate_response_no_api_key(self, monkeypatch: Any) -> None:
        """[FACT] Returns error when no API key configured."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        client = GeminiTextClient(api_key=None)
        result = await client.generate_response("Hello")

        assert not result["success"]
        assert result["text"] is None
        assert "GEMINI_API_KEY not configured" in result["error"]
        assert result["model"] == "gemini-3.1-pro-preview"

    @pytest.mark.anyio
    async def test_generate_response_api_error(self) -> None:
        """[FACT] Handles API error responses gracefully."""
        client = GeminiTextClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limited"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_response("Hello")

        assert not result["success"]
        assert "429" in result["error"]

    @pytest.mark.anyio
    async def test_generate_response_success(self) -> None:
        """[FACT] Successfully parses REST API response."""
        client = GeminiTextClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "[FACT] The sky is blue."}]},
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {"totalTokenCount": 25, "thoughtsTokenCount": 10},
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_response("What color is sky?")

            # [FACT] API key must not appear in URL; pass via header instead.
            call_args = mock_post.call_args
            request_url = call_args[0][0]
            request_headers = call_args[1]["headers"]
            assert "?key=" not in request_url
            assert request_headers.get("x-goog-api-key") == "test_key"

        assert result["success"]
        assert result["text"] == "[FACT] The sky is blue."
        assert result["tokens"] == 25
        assert result["error"] is None

    @pytest.mark.anyio
    async def test_generate_response_with_system_instruction(self) -> None:
        """[FACT] Includes system instruction in payload."""
        client = GeminiTextClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Response"}]}, "finishReason": "STOP"}],
            "usageMetadata": {"totalTokenCount": 10},
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            await client.generate_response("Hello", system_instruction="You are helpful.")

            # Verify system instruction was included
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert "systemInstruction" in payload
            assert payload["systemInstruction"]["parts"][0]["text"] == "You are helpful."

    @pytest.mark.anyio
    async def test_generate_response_safety_blocked(self) -> None:
        """[FACT] Handles safety-blocked responses."""
        client = GeminiTextClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {"parts": []},
                    "finishReason": "SAFETY",
                    "safetyRatings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "probability": "HIGH"}
                    ],
                }
            ],
            "usageMetadata": {"totalTokenCount": 5},
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_response("Hello")

        # Should succeed but with empty text
        assert result["success"]
        assert result["text"] == ""

    @pytest.mark.anyio
    async def test_generate_response_multiple_parts(self) -> None:
        """[FACT] Concatenates multiple text parts."""
        client = GeminiTextClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "[FACT] Part one. "}, {"text": "[FACT] Part two."}]
                    },
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {"totalTokenCount": 20},
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_response("Hello")

        assert result["text"] == "[FACT] Part one. [FACT] Part two."

    @pytest.mark.anyio
    async def test_generate_response_network_error(self) -> None:
        """[FACT] Handles network/timeout errors."""
        client = GeminiTextClient(api_key="test_key")

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection timeout")
            result = await client.generate_response("Hello")

        assert not result["success"]
        assert "Connection timeout" in result["error"]

    def test_validate_constitutional_response_compliant(self) -> None:
        """[FACT] Passes through compliant responses."""
        from helix_code.constitutional_compliance import ConstitutionalCompliance

        client = GeminiTextClient(api_key="test_key")
        guardian = ConstitutionalCompliance()

        result = client.validate_constitutional_response("[FACT] The sky is blue.", guardian)

        assert result["valid"]
        assert not result["intervention"]
        assert result["drift_code"] is None
        assert result["original"] == result["delivered"]

    def test_validate_constitutional_response_agency_drift(self) -> None:
        """[FACT] Intervenes on agency violations."""
        from helix_code.constitutional_compliance import ConstitutionalCompliance

        client = GeminiTextClient(api_key="test_key")
        guardian = ConstitutionalCompliance()

        result = client.validate_constitutional_response("I will take control.", guardian)

        assert not result["valid"]
        assert result["intervention"]
        assert result["drift_code"] == "DRIFT-A"
        assert "Agency claim detected" in result["delivered"]

    def test_validate_constitutional_response_epistemic_drift(self) -> None:
        """[FACT] Intervenes on missing epistemic markers."""
        from helix_code.constitutional_compliance import ConstitutionalCompliance

        client = GeminiTextClient(api_key="test_key")
        guardian = ConstitutionalCompliance()

        result = client.validate_constitutional_response(
            "The price of Bitcoin will definitely reach one hundred thousand dollars by next month.",
            guardian,
        )

        assert not result["valid"]
        assert result["intervention"]
        assert result["drift_code"] == "DRIFT-E"
        assert "Epistemic markers missing" in result["delivered"]

    @pytest.mark.anyio
    async def test_generate_response_returns_model_armor_metadata(self) -> None:
        """[FACT] Successful responses include Model Armor metadata."""
        client = GeminiTextClient(
            api_key="test_key",
            model_armor_client=StubModelArmorClient(ALLOW_RESULT, ALLOW_RESULT),
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "[FACT] Safe output."}]}, "finishReason": "STOP"}
            ],
            "usageMetadata": {"totalTokenCount": 10},
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_response("Hello")

        assert result["success"]
        assert result["model_armor"]["input"]["action"] == "allow"
        assert result["model_armor"]["output"]["action"] == "allow"

    @pytest.mark.anyio
    async def test_generate_response_blocks_before_gemini_request(self) -> None:
        """[FACT] Blocked inbound text short-circuits before Gemini call."""
        client = GeminiTextClient(
            api_key="test_key",
            model_armor_client=StubModelArmorClient(BLOCK_RESULT, ALLOW_RESULT),
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            result = await client.generate_response("Attack prompt")

        mock_post.assert_not_called()
        assert not result["success"]
        assert result["error"] == "Blocked by Model Armor before Gemini request"
        assert result["model_armor"]["input"]["blocked"]

    @pytest.mark.anyio
    async def test_generate_response_blocks_after_gemini_response(self) -> None:
        """[FACT] Blocked outbound text suppresses Gemini output."""
        client = GeminiTextClient(
            api_key="test_key",
            model_armor_client=StubModelArmorClient(ALLOW_RESULT, BLOCK_RESULT),
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "Unsafe output"}]}, "finishReason": "STOP"}
            ],
            "usageMetadata": {"totalTokenCount": 10},
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_response("Hello")

        assert not result["success"]
        assert result["error"] == "Blocked by Model Armor after Gemini response"
        assert result["model_armor"]["output"]["blocked"]

    def test_create_gemini_text_client_factory(self) -> None:
        """[FACT] Factory function creates client instance."""
        client = create_gemini_text_client(api_key="factory_test_key")
        assert isinstance(client, GeminiTextClient)
        assert client.api_key == "factory_test_key"


class StubModelArmorClient(ModelArmorClient):
    def __init__(self, input_result: ModelArmorScreenResult, output_result: ModelArmorScreenResult):
        super().__init__(enabled=False)
        self.input_result = input_result
        self.output_result = output_result

    def screen_input_text(
        self, text: str, context: dict[str, Any] | None = None
    ) -> ModelArmorScreenResult:
        return self.input_result

    def screen_output_text(
        self, text: str, context: dict[str, Any] | None = None
    ) -> ModelArmorScreenResult:
        return self.output_result


ALLOW_RESULT = ModelArmorScreenResult(
    blocked=False,
    action="allow",
    findings=[],
    template="input-template",
    latency_ms=1.0,
    failure_mode="open",
)

BLOCK_RESULT = ModelArmorScreenResult(
    blocked=True,
    action="block",
    findings=[{"category": "prompt_injection"}],
    template="input-template",
    latency_ms=1.0,
    failure_mode="open",
)
