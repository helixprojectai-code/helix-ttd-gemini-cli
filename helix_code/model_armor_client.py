#!/usr/bin/env python3
"""[FACT] Model Armor client for optional Helix request/response screening.

[ASSUMPTION] The initial Helix integration uses inspect-first rollout and keeps
Model Armor disabled unless explicitly configured.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT_MS = 3000


@dataclass(frozen=True)
class ModelArmorScreenResult:
    """[FACT] Stable normalized screening result for Helix code paths."""

    blocked: bool
    action: str
    findings: list[dict[str, Any]]
    template: str | None
    latency_ms: float | None
    failure_mode: str
    error: str | None = None


class ModelArmorClient:
    """[FACT] Small wrapper around Google Model Armor screening APIs."""

    def __init__(
        self,
        *,
        enabled: bool | None = None,
        enforcement: str | None = None,
        failure_mode: str | None = None,
        endpoint: str | None = None,
        input_template: str | None = None,
        output_template: str | None = None,
        timeout_ms: int | None = None,
        auth_token: str | None = None,
    ) -> None:
        env_enabled = os.getenv("HELIX_MODEL_ARMOR_ENABLED", "false").lower() == "true"
        self._enabled = env_enabled if enabled is None else enabled
        self.enforcement = (
            enforcement or os.getenv("HELIX_MODEL_ARMOR_ENFORCEMENT", "inspect").lower()
        )
        self.failure_mode = (
            failure_mode or os.getenv("HELIX_MODEL_ARMOR_FAILURE_MODE", "open").lower()
        )
        self.endpoint = endpoint or os.getenv("HELIX_MODEL_ARMOR_ENDPOINT")
        self.input_template = input_template or os.getenv("HELIX_MODEL_ARMOR_TEMPLATE_INPUT")
        self.output_template = output_template or os.getenv("HELIX_MODEL_ARMOR_TEMPLATE_OUTPUT")
        self.timeout_ms = timeout_ms or int(
            os.getenv("HELIX_MODEL_ARMOR_TIMEOUT_MS", str(_DEFAULT_TIMEOUT_MS))
        )
        self.auth_token = auth_token or os.getenv("HELIX_MODEL_ARMOR_AUTH_TOKEN")

    def enabled(self) -> bool:
        """[FACT] Returns whether Model Armor screening is active."""
        return self._enabled and bool(self.endpoint)

    def screen_input_text(
        self, text: str, context: dict[str, Any] | None = None
    ) -> ModelArmorScreenResult:
        """[FACT] Screen inbound user text before Gemini processing."""
        return self._screen_text(
            text=text,
            template=self.input_template,
            direction="input",
            context=context,
        )

    def screen_output_text(
        self, text: str, context: dict[str, Any] | None = None
    ) -> ModelArmorScreenResult:
        """[FACT] Screen outbound model text before user delivery."""
        return self._screen_text(
            text=text,
            template=self.output_template,
            direction="output",
            context=context,
        )

    def _screen_text(
        self,
        *,
        text: str,
        template: str | None,
        direction: str,
        context: dict[str, Any] | None,
    ) -> ModelArmorScreenResult:
        if not self.enabled():
            return self._allow_result(template=template)

        payload = self._build_request_payload(
            text=text,
            direction=direction,
            template=template,
            context=context,
        )
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        started = time.perf_counter()
        try:
            response = httpx.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout_ms / 1000.0,
            )
            response.raise_for_status()
            latency_ms = (time.perf_counter() - started) * 1000.0
            return self._normalize_result(
                data=response.json(),
                template=template,
                latency_ms=latency_ms,
            )
        except httpx.HTTPError as exc:
            logger.warning("[WARNING] Model Armor request failed: %s", exc)
            return self._fail_result(error=str(exc), template=template)

    def _build_request_payload(
        self,
        *,
        text: str,
        direction: str,
        template: str | None,
        context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "text": text,
            "direction": direction,
        }
        if template:
            payload["template"] = template
        if context:
            payload["context"] = context
        return payload

    def _normalize_result(
        self, *, data: dict[str, Any], template: str | None, latency_ms: float
    ) -> ModelArmorScreenResult:
        findings = data.get("findings", [])
        blocked = bool(data.get("blocked", False))
        action = str(data.get("action", "allow"))
        if self.enforcement == "inspect":
            blocked = False
            if action == "block":
                action = "inspect"
        elif self.enforcement == "soft_block" and action == "block":
            action = "soft_block"

        return ModelArmorScreenResult(
            blocked=blocked,
            action=action,
            findings=findings if isinstance(findings, list) else [],
            template=template,
            latency_ms=latency_ms,
            failure_mode=self.failure_mode,
            error=None,
        )

    def _fail_result(self, *, error: str, template: str | None) -> ModelArmorScreenResult:
        blocked = self.failure_mode == "closed"
        action = "error_block" if blocked else "error_allow"
        return ModelArmorScreenResult(
            blocked=blocked,
            action=action,
            findings=[],
            template=template,
            latency_ms=None,
            failure_mode=self.failure_mode,
            error=error,
        )

    def _allow_result(self, *, template: str | None) -> ModelArmorScreenResult:
        return ModelArmorScreenResult(
            blocked=False,
            action="allow",
            findings=[],
            template=template,
            latency_ms=None,
            failure_mode=self.failure_mode,
            error=None,
        )
