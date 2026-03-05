#!/usr/bin/env python3
"""[FACT] Gemini Text API Client for Constitutional Guardian

[HYPOTHESIS] Text input to Gemini API with real-time validation
proves constitutional guardrails work with live LLM.
[ASSUMPTION] Text is lower complexity than audio - faster iteration.

Phase 1: Text-only Gemini Live
Phase 2: Audio streaming (next iteration)

Node: GCS-GUARDIAN
Status: RATIFIED
"""

from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai import types


class GeminiTextClient:
    """[FACT] Client for Gemini Text API with constitutional validation hook.
    
    [HYPOTHESIS] Wraps Gemini API with mandatory validation step.
    [ASSUMPTION] Model: gemini-2.5-pro for state-of-the-art reasoning.
    """

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-pro"):
        """[FACT] Initialize Gemini client with optional API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client: genai.Client | None = None
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            print(f"[FACT] Gemini client initialized with model: {self.model}")
            print(f"[FACT] API Key (first 8 chars): {self.api_key[:8]}...")
        else:
            print("[WARNING] No GEMINI_API_KEY set. Text API unavailable.")
            print(f"[DEBUG] os.getenv('GEMINI_API_KEY') = {os.getenv('GEMINI_API_KEY')}")

    def is_available(self) -> bool:
        """[FACT] Check if Gemini API is configured and available."""
        return self.client is not None

    async def generate_response(
        self, 
        prompt: str, 
        system_instruction: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """[FACT] Generate response from Gemini API.
        
        [HYPOTHESIS] Returns dict with text, tokens used, latency info.
        [ASSUMPTION] Caller must validate response constitutionally.
        
        Args:
            prompt: User input text
            system_instruction: Optional system prompt for persona
            temperature: Creativity (0.0 = deterministic, 1.0 = creative)
            
        Returns:
            {
                "success": bool,
                "text": str | None,
                "error": str | None,
                "model": str,
                "tokens": int | None,
            }
        """
        if not self.client:
            return {
                "success": False,
                "text": None,
                "error": "GEMINI_API_KEY not configured",
                "model": self.model,
                "tokens": None,
            }

        try:
            # [FACT] Build generation config
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=1024,
            )
            
            # [FACT] Add system instruction if provided
            if system_instruction:
                config.system_instruction = system_instruction

            # [DEBUG] Verify prompt before sending
            print(f"[DEBUG] About to call Gemini API with prompt: '{prompt[:50]}...' (len={len(prompt)})")
            if not prompt or not prompt.strip():
                return {
                    "success": False,
                    "text": None,
                    "error": "Cannot send empty prompt to Gemini API",
                    "model": self.model,
                    "tokens": None,
                }
            
            # [FACT] Call Gemini API (async)
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            # [FACT] Extract response text
            text = response.text if response.text else ""
            
            # [DEBUG] Log raw response
            print(f"[DEBUG] Gemini raw response: '{text[:100]}...' (len={len(text)})")
            print(f"[DEBUG] Response type: {type(response)}")
            print(f"[DEBUG] Response candidates: {len(response.candidates) if response.candidates else 0}")
            
            # [FACT] Get token usage if available
            tokens = None
            if response.usage_metadata:
                tokens = response.usage_metadata.total_token_count

            return {
                "success": True,
                "text": text,
                "error": None,
                "model": self.model,
                "tokens": tokens,
            }

        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(f"[ERROR] Exception type: {type(e)}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
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
        guardian,  # ConstitutionalCompliance instance
    ) -> dict[str, Any]:
        """[FACT] Validate Gemini response through Constitutional Guardian.
        
        [HYPOTHESIS] This is THE key function - validates LLM output.
        [ASSUMPTION] Returns modified response if non-compliant.
        
        Args:
            gemini_response: Raw text from Gemini
            guardian: ConstitutionalCompliance instance
            
        Returns:
            {
                "original": str,
                "delivered": str,
                "valid": bool,
                "intervention": bool,
                "drift_code": str | None,
            }
        """
        # [FACT] Run constitutional validation
        validation = guardian.validate_text(gemini_response)

        result = {
            "original": gemini_response,
            "delivered": gemini_response,
            "valid": validation.compliant,
            "intervention": not validation.compliant,
            "drift_code": validation.drift_code if not validation.compliant else None,
        }

        # [FACT] If non-compliant, generate intervention
        if not validation.compliant:
            interventions = {
                "DRIFT-A": "[CONSTITUTIONAL GUARDIAN: Agency claim detected. AI is a non-agentic tool.]",
                "DRIFT-E": "[CONSTITUTIONAL GUARDIAN: Epistemic markers missing. Factual integrity unverified.]",
                "DRIFT-G": "[CONSTITUTIONAL GUARDIAN: Unauthorized guidance detected. Custodial hierarchy violation.]",
            }
            warning = interventions.get(
                validation.drift_code, 
                "[CONSTITUTIONAL GUARDIAN: Flagged content.]"
            )
            result["delivered"] = f"{warning}\n\n{gemini_response}"

        return result


def create_gemini_text_client(api_key: str | None = None) -> GeminiTextClient:
    """[FACT] Factory function for Gemini Text Client."""
    return GeminiTextClient(api_key=api_key)


# [FACT] Module test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        client = create_gemini_text_client()
        
        if not client.is_available():
            print("[SKIP] No API key configured")
            return
            
        print("[TEST] Testing Gemini Text Client...")
        
        # Test 1: Basic query
        result = await client.generate_response(
            "What is the constitutional approach to AI governance?",
            system_instruction="You are a helpful assistant. Always use epistemic markers like [FACT], [HYPOTHESIS], [ASSUMPTION]."
        )
        
        if result["success"]:
            print(f"[OK] Response: {result['text'][:100]}...")
            print(f"[OK] Tokens: {result['tokens']}")
        else:
            print(f"[ERR] {result['error']}")
    
    asyncio.run(test())
