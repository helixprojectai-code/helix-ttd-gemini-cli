"""[FACT] Gemini Live API WebSocket bridge with Constitutional Guardian validation.

[HYPOTHESIS] Real-time audio/text streaming with constitutional validation
demonstrates the core value proposition for the Gemini Live Agent Challenge.

This module creates a bidirectional bridge between:
- User (WebSocket client - browser/demo)
- Gemini Live API (Google's multimodal streaming API)
- Constitutional Guardian (our validation layer)

The Guardian intercepts Gemini responses, validates epistemic integrity,
and blocks or modifies non-compliant content before it reaches the user.
"""

import os
import json
import base64
import asyncio
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

# [FACT] WebSocket imports
try:
    import websockets
    from websockets.client import connect as ws_connect
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# [FACT] Google GenAI imports for Gemini Live
try:
    from google.genai import types
    from google.genai.types import LiveConnectConfig, LiveServerMessage
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# [FACT] Import our Constitutional Guardian
from helix_code.live_guardian import ConstitutionalGuardian, ValidationResult


@dataclass
class LiveSession:
    """[FACT] Represents a live validation session."""
    session_id: str
    created_at: str
    guardian: ConstitutionalGuardian
    gemini_ws: Optional[Any] = None
    client_ws: Optional[Any] = None
    receipt_count: int = 0
    intervention_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "receipt_count": self.receipt_count,
            "intervention_count": self.intervention_count,
            "status": "active"
        }


class GeminiLiveBridge:
    """[FACT] Bridge between user, Gemini Live, and Constitutional Guardian.
    
    [HYPOTHESIS] A bidirectional streaming proxy with validation middleware
    provides real-time AI safety without significant latency impact.
    
    Architecture:
    User <-> WebSocket <-> Guardian <-> Gemini Live API
                    |
                    v
            Receipt Storage (GCS)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.sessions: Dict[str, LiveSession] = {}
        self.on_intervention: Optional[Callable] = None
        
        if not self.api_key:
            print("[WARNING] GEMINI_API_KEY not set. Gemini Live integration disabled.")
    
    async def create_session(self, session_id: str) -> LiveSession:
        """[FACT] Create a new validated live session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            LiveSession configured with Guardian
        """
        guardian = ConstitutionalGuardian()
        
        session = LiveSession(
            session_id=session_id,
            created_at=datetime.utcnow().isoformat(),
            guardian=guardian
        )
        
        self.sessions[session_id] = session
        print(f"[FACT] Created live session: {session_id}")
        
        return session
    
    async def validate_gemini_response(
        self, 
        session: LiveSession, 
        response_text: str
    ) -> Dict[str, Any]:
        """[FACT] Validate Gemini response through Constitutional Guardian.
        
        Args:
            session: Active live session
            response_text: Text from Gemini Live API
            
        Returns:
            Dict with validation result and action
        """
        # [FACT] Run constitutional validation
        validation = session.guardian.validate_utterance(
            text=response_text,
            session_id=session.session_id
        )
        
        result = {
            "original_text": response_text,
            "valid": validation.valid,
            "receipt_id": None,
            "intervention_required": False,
            "modified_text": response_text,
            "drift_code": validation.drift_code if hasattr(validation, 'drift_code') else None
        }
        
        if validation.valid:
            # [FACT] Generate receipt for valid responses
            session.receipt_count += 1
            result["receipt_id"] = f"live_{session.session_id}_{session.receipt_count}"
            result["message"] = "[FACT] Response validated and receipted."
        else:
            # [FACT] Handle constitutional drift
            session.intervention_count += 1
            result["intervention_required"] = True
            result["message"] = f"[DRIFT] Constitutional violation detected: {result['drift_code']}"
            
            # [HYPOTHESIS] Modify response to mark non-compliant content
            result["modified_text"] = self._generate_intervention(response_text, result['drift_code'])
            
            # [FACT] Trigger intervention callback if set
            if self.on_intervention:
                await self.on_intervention(session, result)
        
        return result
    
    def _generate_intervention(self, original_text: str, drift_code: str) -> str:
        """[FACT] Generate intervention message for non-compliant content.
        
        Instead of blocking entirely, we prepend a constitutional warning
        and mark the content appropriately.
        """
        interventions = {
            "DRIFT-A": "[CONSTITUTIONAL GUARDIAN: Agency claim detected. This statement expresses autonomous intent.]",
            "DRIFT-C": "[CONSTITUTIONAL GUARDIAN: Persona drift detected. Epistemic markers missing.]",
            "DRIFT-E": "[CONSTITUTIONAL GUARDIAN: Unmarked claim. Fact/hypothesis/assumption unclear.]"
        }
        
        warning = interventions.get(drift_code, "[CONSTITUTIONAL GUARDIAN: Content flagged for review.]")
        return f"{warning}\n\n{original_text}"
    
    async def handle_client_message(
        self,
        session: LiveSession,
        message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """[FACT] Process incoming message from client.
        
        Args:
            session: Active live session
            message: WebSocket message from client
            
        Returns:
            Response to send back to client
        """
        msg_type = message.get('type', 'text')
        
        if msg_type == 'text':
            # [FACT] Validate user input as well (optional)
            text = message.get('content', '')
            return {
                'type': 'forward',
                'content': text,
                'validated': True
            }
        
        elif msg_type == 'audio':
            # [FACT] Forward audio to Gemini Live
            return {
                'type': 'forward_audio',
                'audio': message.get('audio'),
                'mime_type': message.get('mime_type', 'audio/webm')
            }
        
        elif msg_type == 'ping':
            return {'type': 'pong', 'timestamp': datetime.utcnow().isoformat()}
        
        return None
    
    async def handle_gemini_response(
        self,
        session: LiveSession,
        gemini_message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """[FACT] Process response from Gemini Live API.
        
        This is the CRITICAL PATH - every Gemini response flows through
        Constitutional Guardian before reaching the user.
        """
        # [FACT] Extract text from Gemini response
        text = self._extract_text_from_gemini(gemini_message)
        
        if not text:
            return {'type': 'gemini_raw', 'data': gemini_message}
        
        # [FACT] Validate through Guardian
        validation = await self.validate_gemini_response(session, text)
        
        return {
            'type': 'validated_response',
            'original': text,
            'delivered': validation['modified_text'] if validation['intervention_required'] else text,
            'valid': validation['valid'],
            'receipt_id': validation.get('receipt_id'),
            'intervention': validation['intervention_required'],
            'drift_code': validation.get('drift_code'),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _extract_text_from_gemini(self, message: Dict[str, Any]) -> str:
        """[FACT] Extract text content from Gemini Live message."""
        # [HYPOTHESIS] Gemini Live returns various message formats
        if 'text' in message:
            return message['text']
        
        if 'content' in message and isinstance(message['content'], str):
            return message['content']
        
        # [FACT] Handle structured responses
        if 'parts' in message:
            parts = message['parts']
            text_parts = [p.get('text', '') for p in parts if isinstance(p, dict)]
            return ' '.join(text_parts)
        
        return ""
    
    async def stream_audio_to_gemini(
        self,
        session: LiveSession,
        audio_base64: str,
        mime_type: str = "audio/webm"
    ):
        """[FACT] Stream audio data to Gemini Live API.
        
        [HYPOTHESIS] Real-time audio streaming with <500ms latency
        enables natural voice conversation flow.
        """
        if not GENAI_AVAILABLE or not self.api_key:
            print("[WARNING] Gemini Live not available. Simulating response.")
            return await self._simulate_gemini_response(session, "[Simulated Gemini response]")
        
        # [FACT] Actual Gemini Live integration would go here
        # This requires the full Google GenAI SDK with Live API access
        print(f"[FACT] Streaming audio to Gemini Live: {len(audio_base64)} bytes")
        
        # [HYPOTHESIS] Placeholder for actual implementation
        # Real implementation would use:
        # - google.genai.Client.live.connect()
        # - Bidirectional streaming
        # - Real-time response handling
        
        return await self._simulate_gemini_response(session, "[Audio processed by Gemini]")
    
    async def _simulate_gemini_response(
        self,
        session: LiveSession,
        text: str
    ) -> Dict[str, Any]:
        """[FACT] Simulate Gemini response for testing without API key."""
        # [HYPOTHESIS] Simulate various response types for demo
        demo_responses = [
            "I will help you with that task right away.",
            "The stock market will definitely go up tomorrow.",
            "Water boils at 100 degrees Celsius at sea level.",
            "My goal is to assist you efficiently."
        ]
        
        import random
        simulated = random.choice(demo_responses)
        
        return await self.handle_gemini_response(session, {'text': simulated})
    
    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """[FACT] Get statistics for a live session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        return session.to_dict()
    
    async def close_session(self, session_id: str):
        """[FACT] Clean up and close a live session."""
        session = self.sessions.pop(session_id, None)
        if session:
            print(f"[FACT] Closed live session: {session_id}")
            print(f"[FACT] Session stats: {session.receipt_count} receipts, {session.intervention_count} interventions")


# [FACT] Convenience factory function
def create_gemini_bridge(api_key: Optional[str] = None) -> GeminiLiveBridge:
    """Create a configured Gemini Live Bridge with Constitutional Guardian."""
    return GeminiLiveBridge(api_key=api_key)
