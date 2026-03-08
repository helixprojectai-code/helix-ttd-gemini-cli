"""[FACT] Tests for secret resolution with optional Vault backend."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import httpx

from helix_code import secret_resolver


def _clear_cache() -> None:
    secret_resolver._secret_cache.clear()  # noqa: SLF001


def test_env_secret_resolution_default_backend(monkeypatch: Any) -> None:
    monkeypatch.delenv("HELIX_SECRET_BACKEND", raising=False)
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    monkeypatch.delenv("VAULT_TOKEN", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_VAULT_PATH", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "line1\n")

    _clear_cache()

    assert secret_resolver.active_secret_backend() == "env"
    assert secret_resolver.resolve_gemini_api_key(refresh=True) == "line1"


def test_vault_secret_resolution_success(monkeypatch: Any) -> None:
    monkeypatch.setenv("HELIX_SECRET_BACKEND", "auto")
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example")
    monkeypatch.setenv("VAULT_TOKEN", "token")
    monkeypatch.setenv("GEMINI_API_KEY_VAULT_PATH", "helix/gemini")
    monkeypatch.setenv("GEMINI_API_KEY_VAULT_FIELD", "api_key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = MagicMock()
    response.json.return_value = {"data": {"data": {"api_key": "vault_key_123"}}}

    _clear_cache()

    with patch("helix_code.secret_resolver.httpx.get", return_value=response) as mock_get:
        resolved = secret_resolver.resolve_gemini_api_key(refresh=True)

    assert resolved == "vault_key_123"
    assert secret_resolver.active_secret_backend() == "vault"
    assert mock_get.call_count == 1


def test_vault_resolution_falls_back_to_env(monkeypatch: Any) -> None:
    monkeypatch.setenv("HELIX_SECRET_BACKEND", "vault")
    monkeypatch.setenv("VAULT_ADDR", "https://vault.example")
    monkeypatch.setenv("VAULT_TOKEN", "token")
    monkeypatch.setenv("GEMINI_API_KEY_VAULT_PATH", "helix/gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "env_fallback_key")

    _clear_cache()

    with patch("helix_code.secret_resolver.httpx.get") as mock_get:
        mock_get.side_effect = httpx.HTTPError("network down")
        resolved = secret_resolver.resolve_gemini_api_key(refresh=True)

    assert resolved == "env_fallback_key"


def test_secret_cache_key_uses_hash(monkeypatch: Any) -> None:
    monkeypatch.delenv("HELIX_SECRET_BACKEND", raising=False)
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    monkeypatch.delenv("VAULT_TOKEN", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_VAULT_PATH", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "super_secret_key")

    _clear_cache()

    key = secret_resolver.gemini_secret_cache_key(refresh=True)
    assert key is not None
    assert key.startswith("env:")
    assert "super_secret_key" not in key


def test_is_configured_false_when_missing(monkeypatch: Any) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("VAULT_ADDR", raising=False)
    monkeypatch.delenv("VAULT_TOKEN", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_VAULT_PATH", raising=False)

    _clear_cache()

    assert secret_resolver.is_gemini_api_key_configured() is False


def test_admin_and_audio_tokens_use_shared_resolver(monkeypatch: Any) -> None:
    monkeypatch.setenv("HELIX_ADMIN_TOKEN", "admin_secret")
    monkeypatch.setenv("AUDIO_AUDIT_TOKEN", "audio_secret")

    _clear_cache()

    assert secret_resolver.resolve_admin_token(refresh=True) == "admin_secret"
    assert secret_resolver.resolve_audio_audit_token(refresh=True) == "audio_secret"
    assert secret_resolver.is_admin_token_configured() is True
    assert secret_resolver.is_audio_audit_token_configured() is True


def test_cache_identity_is_hashed(monkeypatch: Any) -> None:
    monkeypatch.setenv("HELIX_SECRET_BACKEND", "env")
    monkeypatch.setenv("HELIX_ADMIN_TOKEN", "secret:with:colons")
    monkeypatch.setenv("HELIX_ADMIN_TOKEN_VAULT_PATH", "path:with:colons")

    _clear_cache()
    secret_resolver.resolve_admin_token(refresh=True)

    cache_keys = list(secret_resolver._secret_cache.keys())  # noqa: SLF001
    assert len(cache_keys) == 1
    assert ":with:colons" not in cache_keys[0]
    assert len(cache_keys[0]) == 64
