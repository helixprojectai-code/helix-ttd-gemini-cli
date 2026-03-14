#!/usr/bin/env python3
"""[FACT] Gemini Text API Client for Constitutional Guardian (REST Fallback)

[HYPOTHESIS] Using direct REST API bypasses SDK parsing issues with gemini-3.1-pro-preview
reasoning-model responses (which include thoughtsTokenCount).

Node: GCS-GUARDIAN
Status: RATIFIED
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

try:
    from model_armor_client import ModelArmorClient
    from secret_resolver import resolve_gemini_api_key
except ImportError:  # pragma: no cover
    from .model_armor_client import ModelArmorClient
    from .secret_resolver import resolve_gemini_api_key

logger = logging.getLogger(__name__)


class GeminiTextClient:
    """[FACT] Client for Gemini Text API with direct REST implementation.

    [HYPOTHESIS] REST calls are more stable for v1beta models like gemini-3.1-pro-preview.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-3.1-pro-preview"),
        model_armor_client: ModelArmorClient | None = None,
    ):
        """[FACT] Initialize Gemini client with REST configuration."""
        self._explicit_api_key = api_key is not None
        self.api_key = api_key or resolve_gemini_api_key()
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_armor = model_armor_client or ModelArmorClient()

        if self.api_key:
            logger.info(f"[FACT] Gemini REST client initialized with model: {self.model}")
        else:
            logger.warning("[WARNING] No GEMINI_API_KEY set. Text API unavailable.")

    @staticmethod
    def _serialize_model_armor_result(result: Any) -> dict[str, Any] | None:
        if result is None:
            return None
        return {
            "blocked": result.blocked,
            "action": result.action,
            "findings": result.findings,
            "template": result.template,
            "latency_ms": result.latency_ms,
            "error": result.error,
        }

    def is_available(self) -> bool:
        """[FACT] Check if API key is configured."""
        if not self._explicit_api_key and not self.api_key:
            self.api_key = resolve_gemini_api_key()
        return self.api_key is not None

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """[FACT] Generate response using direct HTTP POST to Google API."""
        if not self._explicit_api_key:
            refreshed_key = resolve_gemini_api_key(refresh=True)
            if refreshed_key:
                self.api_key = refreshed_key

        if not self.api_key:
            return {
                "success": False,
                "text": None,
                "error": "GEMINI_API_KEY not configured",
                "model": self.model,
                "tokens": None,
                "model_armor": {"input": None, "output": None},
            }

        armor_input = self.model_armor.screen_input_text(
            prompt,
            context={"path": "text", "direction": "input", "model": self.model},
        )
        if armor_input.blocked:
            return {
                "success": False,
                "text": None,
                "error": "Blocked by Model Armor before Gemini request",
                "model": self.model,
                "tokens": None,
                "model_armor": {
                    "input": self._serialize_model_armor_result(armor_input),
                    "output": None,
                },
            }

        # [FACT] Keep API key out of request URLs to prevent accidental log leakage.
        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {"x-goog-api-key": self.api_key}

        # Build payload
        contents = [{"parts": [{"text": prompt}]}]

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            logger.info(f"[DEBUG] Calling Gemini REST API: {self.model}")
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=60.0)

            if response.status_code != 200:
                return {
                    "success": False,
                    "text": None,
                    "error": f"API Status {response.status_code}: {response.text}",
                    "model": self.model,
                    "tokens": None,
                    "model_armor": {
                        "input": {
                            "blocked": armor_input.blocked,
                            "action": armor_input.action,
                            "findings": armor_input.findings,
                            "template": armor_input.template,
                            "latency_ms": armor_input.latency_ms,
                            "error": armor_input.error,
                        },
                        "output": None,
                    },
                }

            data = response.json()

            # [DEBUG] Log full response if text is empty
            text = ""
            try:
                if "candidates" in data and data["candidates"]:
                    candidate = data["candidates"][0]

                    # Check finish reason
                    finish_reason = candidate.get("finishReason")
                    if finish_reason != "STOP":
                        logger.warning(f"[WARNING] Gemini finished with reason: {finish_reason}")

                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "text" in part:
                                text += part["text"]

                if not text:
                    logger.warning(
                        f"[DEBUG] Empty text response from Gemini. Raw: {json.dumps(data)}"
                    )
                    if "candidates" in data and data["candidates"]:
                        c = data["candidates"][0]
                        if "safetyRatings" in c:
                            logger.info(f"[DEBUG] Safety Ratings: {c['safetyRatings']}")

            except (KeyError, IndexError) as e:
                logger.error(f"[ERROR] Parsing REST response: {e}")
                return {
                    "success": False,
                    "text": None,
                    "error": "Failed to parse API response",
                    "model": self.model,
                    "tokens": None,
                    "model_armor": {
                        "input": {
                            "blocked": armor_input.blocked,
                            "action": armor_input.action,
                            "findings": armor_input.findings,
                            "template": armor_input.template,
                            "latency_ms": armor_input.latency_ms,
                            "error": armor_input.error,
                        },
                        "output": None,
                    },
                }

            armor_output = self.model_armor.screen_output_text(
                text,
                context={"path": "text", "direction": "output", "model": self.model},
            )
            if armor_output.blocked:
                return {
                    "success": False,
                    "text": None,
                    "error": "Blocked by Model Armor after Gemini response",
                    "model": self.model,
                    "tokens": None,
                    "model_armor": {
                        "input": self._serialize_model_armor_result(armor_input),
                        "output": self._serialize_model_armor_result(armor_output),
                    },
                }

            # [FACT] Get token usage (including reasoning thoughts)
            tokens = data.get("usageMetadata", {}).get("totalTokenCount")
            thoughts = data.get("usageMetadata", {}).get("thoughtsTokenCount", 0)
            if thoughts > 0:
                logger.info(f"[FACT] Model generated {thoughts} reasoning tokens.")

            return {
                "success": True,
                "text": text,
                "error": None,
                "model": self.model,
                "tokens": tokens,
                "model_armor": {
                    "input": self._serialize_model_armor_result(armor_input),
                    "output": self._serialize_model_armor_result(armor_output),
                },
            }

        except Exception as e:
            error_msg = f"Gemini REST error: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "text": None,
                "error": error_msg,
                "model": self.model,
                "tokens": None,
                "model_armor": {
                    "input": self._serialize_model_armor_result(armor_input),
                    "output": None,
                },
            }

    def validate_constitutional_response(
        self,
        gemini_response: str,
        guardian: Any,
    ) -> dict[str, Any]:
        """[FACT] Validate Gemini response through Constitutional Guardian."""
        validation = guardian.validate_text(gemini_response)

        result = {
            "original": gemini_response,
            "delivered": gemini_response,
            "valid": validation.compliant,
            "intervention": not validation.compliant,
            "drift_code": validation.drift_code if not validation.compliant else None,
        }

        if not validation.compliant:
            interventions = {
                "DRIFT-A": "[CONSTITUTIONAL GUARDIAN: Agency claim detected. AI is a non-agentic tool.]",
                "DRIFT-E": "[CONSTITUTIONAL GUARDIAN: Epistemic markers missing. Factual integrity unverified.]",
                "DRIFT-G": "[CONSTITUTIONAL GUARDIAN: Unauthorized guidance detected. Custodial hierarchy violation.]",
            }
            warning = interventions.get(
                validation.drift_code, "[CONSTITUTIONAL GUARDIAN: Flagged content.]"
            )
            result["delivered"] = f"{warning}\n\n{gemini_response}"

        return result


def create_gemini_text_client(api_key: str | None = None) -> GeminiTextClient:
    """[FACT] Factory function for Gemini Text Client."""
    return GeminiTextClient(api_key=api_key)
