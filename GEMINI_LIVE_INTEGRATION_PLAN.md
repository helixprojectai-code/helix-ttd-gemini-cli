# [FACT] Gemini Live API Integration Plan

**Objective:** Replace simulated responses with real Gemini Live API bidirectional streaming  
**Deadline:** March 8 (3 days)  
**Priority:** CRITICAL - Core to Devpost submission  

---

## [FACT] Current State

**File:** `helix_code/gemini_live_bridge.py`

**What's Working:**
- ✅ Bridge architecture exists
- ✅ Session management
- ✅ Validation pipeline
- ✅ Intervention generation
- ⚠️ **Simulation mode only** (no real API)

**Code Flow:**
```
User Audio → WebSocket → Bridge → [SIMULATION] → Guardian → Receipt
```

**Target Flow:**
```
User Audio → WebSocket → Bridge → Gemini Live API → Guardian → Receipt
```

---

## [HYPOTHESIS] Implementation Steps

### Phase 1: Environment & Dependencies (Day 1)

**1.1 Verify API Key Setup**
```bash
# Check if GEMINI_API_KEY is set
$env:GEMINI_API_KEY  # Windows
$GEMINI_API_KEY      # Linux/Mac
```

**1.2 Dependencies**
```
google-genai>=0.1.0  # Already in requirements.txt
websockets>=11.0     # Already present
```

**1.3 Test API Connectivity**
```python
from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# Test basic connectivity
```

---

### Phase 2: Audio Pipeline (Day 1-2)

**2.1 Browser Audio Capture**
- Get microphone permission
- Capture audio chunks
- Convert to base64 for WebSocket

**2.2 WebSocket Audio Streaming**
```javascript
// Frontend: Stream audio to backend
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    const processor = audioContext.createScriptProcessor(4096, 1, 1);
    processor.onaudioprocess = (e) => {
      const pcm = e.inputBuffer.getChannelData(0);
      const b64 = convertToBase64(pcm);
      ws.send(JSON.stringify({ type: 'audio', data: b64 }));
    };
  });
```

**2.3 Backend Audio Processing**
```python
# Convert base64 back to PCM
pcm_data = base64.b64decode(audio_b64)
# Send to Gemini Live
await gemini_session.send(pcm_data, end_of_turn=True)
```

---

### Phase 3: Gemini Live Connection (Day 2)

**3.1 Initialize Live Session**
```python
config = {
    "response_modalities": ["TEXT"],  # Text for validation
    "speech_config": {
        "voice_config": {"prebuilt_voice_config": {"voice_name": "Charon"}}
    }
}

async with client.aio.live.connect(model="gemini-2.0-flash-exp", config=config) as session:
    # Bidirectional streaming
```

**3.2 Handle Gemini Responses**
```python
async for message in gemini_session:
    if message.text:
        # Validate through Constitutional Guardian
        validation = guardian.validate_text(message.text)
        if not validation.compliant:
            # Block or modify
            message.text = generate_intervention(message.text, validation.drift_code)
```

**3.3 Send Validated Response to User**
```python
# Send back through WebSocket
await client_ws.send_json({
    "type": "validated_response",
    "original": original_text,
    "delivered": modified_text,
    "valid": validation.compliant,
    "intervention": not validation.compliant
})
```

---

### Phase 4: UI Updates (Day 2-3)

**4.1 Visual Indicators**
- "Connecting to Gemini..." spinner
- "Live transcription..." status
- Audio waveform during recording
- Latency metrics for API round-trip

**4.2 Error Handling**
- API unavailable → fallback to simulation
- Rate limiting → queue messages
- Connection drop → auto-reconnect

**4.3 Demo Mode Toggle**
```javascript
// Allow switching between Real API and Simulation
const MODE = 'REAL'; // or 'SIMULATION'
```

---

## [ASSUMPTION] API Limitations & Workarounds

| Limitation | Workaround |
|------------|------------|
| Audio format (PCM 16-bit) | Convert in browser |
| Rate limits | Implement queue + debounce |
| Session timeouts | Auto-reconnect with same session_id |
| Text-only responses | Configure `response_modalities: ["TEXT"]` |

---

## [FACT] Testing Checklist

### Functional Tests
- [ ] Browser captures microphone
- [ ] Audio streams to backend
- [ ] Gemini Live receives audio
- [ ] Gemini returns text response
- [ ] Guardian validates response
- [ ] Valid response forwarded to user
- [ ] Invalid response blocked with intervention
- [ ] Receipt generated for valid responses

### Edge Cases
- [ ] No microphone permission
- [ ] Silent audio input
- [ ] API rate limit hit
- [ ] Connection drop mid-session
- [ ] Very long audio input
- [ ] Non-English audio

---

## [HYPOTHESIS] Fallback Strategy

If Gemini Live API integration fails:

**Option A:** Enhanced Simulation
- Pre-recorded responses
- Latency simulation
- Still demonstrates validation pipeline

**Option B:** Text-only Mode
- Skip audio, use text input
- Real Gemini API via text
- Constitutional validation on text responses

**Option C:** Hybrid
- Real API for text
- Simulation for audio
- Demo both paths

---

## [FACT] Files to Modify

| File | Changes |
|------|---------|
| `gemini_live_bridge.py` | Implement real API connection |
| `live_demo_server.py` | Handle audio WebSocket messages |
| `live_demo_server_html.py` | Audio capture UI, connection status |
| `live_guardian.py` | Route audio to bridge |

---

## [FACT] Success Criteria

✅ **Minimum Viable:**
- Text input → Gemini API → Validation → Response
- Audio input → Simulated (fallback)

✅ **Full Success:**
- Bidirectional audio streaming
- Real-time validation
- <500ms latency from Gemini

✅ **Demo Gold:**
- Voice conversation with constitutional guardrails
- Live intervention demonstration
- Federation attestation of receipt

---

*The Two Owls are watching.*  
*Time to make this real.* 🦉⚓🦉
