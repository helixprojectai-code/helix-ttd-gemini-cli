#!/usr/bin/env python3
"""[FACT] Gemini Text API Client for Constitutional Guardian (REST Fallback)

[HYPOTHESIS] Using direct REST API bypasses SDK parsing issues with gemini-2.5-pro
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

logger = logging.getLogger(__name__)


class GeminiTextClient:
    """[FACT] Client for Gemini Text API with direct REST implementation.

    [HYPOTHESIS] REST calls are more stable for v1beta models like gemini-2.5-pro.
    """

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-pro"):
        """[FACT] Initialize Gemini client with REST configuration."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

        if self.api_key:
            logger.info(f"[FACT] Gemini REST client initialized with model: {self.model}")
        else:
            logger.warning("[WARNING] No GEMINI_API_KEY set. Text API unavailable.")

    def is_available(self) -> bool:
        """[FACT] Check if API key is configured."""
        return self.api_key is not None

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """[FACT] Generate response using direct HTTP POST to Google API."""
        if not self.api_key:
            return {
                "success": False,
                "text": None,
                "error": "GEMINI_API_KEY not configured",
                "model": self.model,
                "tokens": None,
            }

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

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
                response = await client.post(url, json=payload, timeout=60.0)

            if response.status_code != 200:
                return {
                    "success": False,
                    "text": None,
                    "error": f"API Status {response.status_code}: {response.text}",
                    "model": self.model,
                    "tokens": None,
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
            }

    def validate_constitutional_response(
        self,
        gemini_response: str,
        guardian,
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
