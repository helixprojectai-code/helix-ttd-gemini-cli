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
    [ASSUMPTION] Model: gemini-1.5-flash for low latency.
    """

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        """[FACT] Initialize Gemini client with optional API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client: genai.Client | None = None
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            print("[WARNING] No GEMINI_API_KEY set. Text API unavailable.")

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

            # [FACT] Call Gemini API
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            # [FACT] Extract response text
            text = response.text if response.text else ""
            
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
            return {
                "success": False,
                "text": None,
                "error": f"Gemini API error: {str(e)}",
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
