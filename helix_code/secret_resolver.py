"""Secret resolution utilities with optional Vault backend and env fallback."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VaultConfig:
    """Runtime configuration for HashiCorp Vault lookups."""

    address: str
    token: str
    path: str
    field: str
    namespace: str | None
    timeout_seconds: float


_cache_lock = threading.Lock()
_secret_cache: dict[str, tuple[str | None, float]] = {}


def _sanitize_secret(value: str | None) -> str | None:
    if value is None:
        return None
    compact = "".join(value.splitlines()).strip()
    return compact or None


def _cache_ttl_seconds() -> float:
    raw = os.getenv("HELIX_SECRET_CACHE_TTL_SECONDS", "30").strip()
    try:
        ttl = float(raw)
    except ValueError:
        return 30.0
    return max(0.0, ttl)


def _cache_get(cache_key: str) -> tuple[bool, str | None]:
    now = time.time()
    with _cache_lock:
        cached = _secret_cache.get(cache_key)
        if not cached:
            return False, None
        value, expires_at = cached
        if now > expires_at:
            _secret_cache.pop(cache_key, None)
            return False, None
        return True, value


def _cache_set(cache_key: str, value: str | None) -> None:
    expires_at = time.time() + _cache_ttl_seconds()
    with _cache_lock:
        _secret_cache[cache_key] = (value, expires_at)


def _cache_identity(
    backend: str,
    env_var: str,
    path_env: str,
    field_env: str,
) -> str:
    """Build a collision-resistant cache identity from active resolution inputs."""
    payload = {
        "backend": backend,
        "env_var": env_var,
        "secret_backend_pref": os.getenv("HELIX_SECRET_BACKEND", "auto"),
        "vault_addr": os.getenv("VAULT_ADDR", ""),
        "vault_namespace": os.getenv("VAULT_NAMESPACE", ""),
        "vault_mount": os.getenv("VAULT_KV_MOUNT", ""),
        "path_env": path_env,
        "path_value": os.getenv(path_env, ""),
        "field_env": field_env,
        "field_value": os.getenv(field_env, ""),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return digest


def _vault_config_for(path_env: str, field_env: str) -> VaultConfig | None:
    address = os.getenv("VAULT_ADDR", "").strip().rstrip("/")
    token = os.getenv("VAULT_TOKEN", "").strip()
    path = os.getenv(path_env, "").strip().strip("/")
    field = os.getenv(field_env, "").strip() or "GEMINI_API_KEY"
    namespace = os.getenv("VAULT_NAMESPACE", "").strip() or None

    timeout_raw = os.getenv("VAULT_HTTP_TIMEOUT_SECONDS", "5").strip()
    try:
        timeout_seconds = float(timeout_raw)
    except ValueError:
        timeout_seconds = 5.0

    if not (address and token and path):
        return None

    return VaultConfig(
        address=address,
        token=token,
        path=path,
        field=field,
        namespace=namespace,
        timeout_seconds=max(1.0, timeout_seconds),
    )


def vault_is_configured(
    path_env: str = "GEMINI_API_KEY_VAULT_PATH",
    field_env: str = "GEMINI_API_KEY_VAULT_FIELD",
) -> bool:
    return _vault_config_for(path_env, field_env) is not None


def _selected_backend(path_env: str, field_env: str) -> str:
    backend_pref = os.getenv("HELIX_SECRET_BACKEND", "auto").strip().lower()
    if backend_pref not in {"auto", "env", "vault"}:
        backend_pref = "auto"

    has_vault = vault_is_configured(path_env=path_env, field_env=field_env)

    if backend_pref == "env":
        return "env"
    if backend_pref == "vault":
        return "vault" if has_vault else "env"
    return "vault" if has_vault else "env"


def active_secret_backend() -> str:
    return _selected_backend(
        path_env="GEMINI_API_KEY_VAULT_PATH",
        field_env="GEMINI_API_KEY_VAULT_FIELD",
    )


def _vault_url(config: VaultConfig) -> str:
    if "/data/" in config.path:
        return f"{config.address}/v1/{config.path}"
    mount = os.getenv("VAULT_KV_MOUNT", "secret").strip().strip("/") or "secret"
    return f"{config.address}/v1/{mount}/data/{config.path}"


def _extract_vault_secret(payload: dict, field: str) -> str | None:
    data = payload.get("data")
    if not isinstance(data, dict):
        return None

    nested = data.get("data")
    if isinstance(nested, dict) and field in nested:
        return _sanitize_secret(str(nested.get(field)))

    if field in data:
        return _sanitize_secret(str(data.get(field)))

    return None


def _read_from_vault(config: VaultConfig) -> str | None:
    url = _vault_url(config)
    headers = {"X-Vault-Token": config.token}
    if config.namespace:
        headers["X-Vault-Namespace"] = config.namespace

    response = httpx.get(url, headers=headers, timeout=config.timeout_seconds)
    response.raise_for_status()

    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError("Vault response was not valid JSON") from exc

    secret = _extract_vault_secret(payload, config.field)
    if not secret:
        raise RuntimeError(f"Vault secret field '{config.field}' not found")
    return secret


def resolve_secret(
    env_var: str,
    *,
    path_env: str,
    field_env: str,
    refresh: bool = False,
) -> str | None:
    backend = _selected_backend(path_env=path_env, field_env=field_env)
    cache_key = _cache_identity(backend, env_var, path_env, field_env)

    if not refresh:
        found, cached = _cache_get(cache_key)
        if found:
            return cached

    resolved: str | None = None

    if backend == "vault":
        config = _vault_config_for(path_env, field_env)
        if config is not None:
            try:
                resolved = _read_from_vault(config)
            except Exception as exc:
                logger.warning("Vault secret resolution failed for %s: %s", env_var, exc)

    if not resolved:
        resolved = _sanitize_secret(os.getenv(env_var))

    _cache_set(cache_key, resolved)
    return resolved


def resolve_gemini_api_key(refresh: bool = False) -> str | None:
    return resolve_secret(
        "GEMINI_API_KEY",
        path_env="GEMINI_API_KEY_VAULT_PATH",
        field_env="GEMINI_API_KEY_VAULT_FIELD",
        refresh=refresh,
    )


def resolve_admin_token(refresh: bool = False) -> str | None:
    return resolve_secret(
        "HELIX_ADMIN_TOKEN",
        path_env="HELIX_ADMIN_TOKEN_VAULT_PATH",
        field_env="HELIX_ADMIN_TOKEN_VAULT_FIELD",
        refresh=refresh,
    )


def resolve_audio_audit_token(refresh: bool = False) -> str | None:
    return resolve_secret(
        "AUDIO_AUDIT_TOKEN",
        path_env="AUDIO_AUDIT_TOKEN_VAULT_PATH",
        field_env="AUDIO_AUDIT_TOKEN_VAULT_FIELD",
        refresh=refresh,
    )


def is_gemini_api_key_configured() -> bool:
    return bool(resolve_gemini_api_key())


def is_admin_token_configured() -> bool:
    return bool(resolve_admin_token())


def is_audio_audit_token_configured() -> bool:
    return bool(resolve_audio_audit_token())


def gemini_secret_cache_key(refresh: bool = False) -> str | None:
    secret = resolve_gemini_api_key(refresh=refresh)
    if not secret:
        return None
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()[:16]
    return f"{active_secret_backend()}:{digest}"
