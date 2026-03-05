"""[FACT] Live demo server for Constitutional Guardian with Gemini Live integration.

[HYPOTHESIS] A web-based demo showing real-time constitutional validation
provides compelling proof of the Gemini Live Agent Challenge submission.

This server provides:
- WebSocket endpoint for live audio/text streaming
- HTML demo page with interactive UI
- Real-time validation visualization
- Session statistics and receipt display
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Set
from pathlib import Path

# [FACT] FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# [FACT] Import our Gemini Live Bridge
from helix_code.gemini_live_bridge import GeminiLiveBridge, create_gemini_bridge


app = FastAPI(title="Constitutional Guardian Live Demo")

# [FACT] Global bridge instance
bridge = create_gemini_bridge()

# [FACT] Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


# [FACT] HTML Demo Page
DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Constitutional Guardian - Live Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            padding: 40px 20px;
            border-bottom: 2px solid #00ff88;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #aaa;
            font-size: 1.1rem;
        }
        
        .status-bar {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .status-item {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            padding: 10px 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .status-label {
            font-size: 0.8rem;
            color: #888;
            text-transform: uppercase;
        }
        
        .status-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #00ff88;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .panel h2 {
            color: #00ff88;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .input-area {
            width: 100%;
            min-height: 120px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            color: #fff;
            font-size: 1rem;
            resize: vertical;
            margin-bottom: 15px;
        }
        
        .input-area:focus {
            outline: none;
            border-color: #00ff88;
        }
        
        .btn {
            background: linear-gradient(90deg, #00ff88, #00cc66);
            color: #000;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
        }
        
        .btn:disabled {
            background: #444;
            color: #888;
            cursor: not-allowed;
            transform: none;
        }
        
        .output-area {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            min-height: 200px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-y: auto;
            max-height: 400px;
        }
        
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 6px;
            border-left: 3px solid;
        }
        
        .message.user {
            background: rgba(0, 100, 255, 0.1);
            border-left-color: #0064ff;
        }
        
        .message.gemini {
            background: rgba(138, 43, 226, 0.1);
            border-left-color: #8a2be2;
        }
        
        .message.validated {
            background: rgba(0, 255, 136, 0.1);
            border-left-color: #00ff88;
        }
        
        .message.intervention {
            background: rgba(255, 68, 68, 0.1);
            border-left-color: #ff4444;
        }
        
        .timestamp {
            font-size: 0.75rem;
            color: #666;
            margin-bottom: 5px;
        }
        
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-right: 5px;
        }
        
        .badge.fact {
            background: #00ff88;
            color: #000;
        }
        
        .badge.hypothesis {
            background: #ffaa00;
            color: #000;
        }
        
        .badge.assumption {
            background: #00ccff;
            color: #000;
        }
        
        .badge.drift {
            background: #ff4444;
            color: #fff;
        }
        
        .receipt-id {
            font-size: 0.8rem;
            color: #888;
            font-family: monospace;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        
        .connection-status.connected {
            background: #00ff88;
            color: #000;
        }
        
        .connection-status.disconnected {
            background: #ff4444;
            color: #fff;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: #666;
            border-top: 1px solid #333;
            margin-top: 30px;
        }
        
        .footer a {
            color: #00ff88;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="connection-status disconnected" id="connectionStatus">
        Disconnected
    </div>
    
    <div class="container">
        <header>
            <h1>🛡️ Constitutional Guardian</h1>
            <p class="subtitle">Live Demo - Real-time AI Safety for Gemini Live</p>
            
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-label">Session</div>
                    <div class="status-value" id="sessionId">-</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Receipts</div>
                    <div class="status-value" id="receiptCount">0</div>
                </div>
                <div class="status-item">
                    <div class="status-label">Interventions</div>
                    <div class="status-value" id="interventionCount">0</div>
                </div>
            </div>
        </header>
        
        <div class="main-grid">
            <div class="panel">
                <h2>🎤 Input</h2>
                <textarea 
                    class="input-area" 
                    id="inputText" 
                    placeholder="Type a message to test Constitutional Guardian...\n\nTry these examples:\n- [FACT] Water boils at 100C\n- [HYPOTHESIS] AI may surpass human intelligence by 2040\n- AI will take all our jobs (unmarked - should trigger intervention)\n- I will handle that for you (agency - should trigger intervention)"
                ></textarea>
                <button class="btn" id="sendBtn" onclick="sendMessage()">Send to Guardian</button>
                <button class="btn" style="margin-left: 10px; background: linear-gradient(90deg, #ffaa00, #ff8800);" onclick="simulateGemini()">Simulate Gemini Response</button>
            </div>
            
            <div class="panel">
                <h2>📊 Live Validation Log</h2>
                <div class="output-area" id="outputLog">
                    <div class="message" style="color: #666; font-style: italic;">
                        Waiting for connection... Click "Send to Guardian" to start.
                    </div>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>📚 About This Demo</h2>
            <p style="line-height: 1.6; color: #aaa;">
                <strong>Constitutional Guardian</strong> validates every AI response using epistemic markers:
                <span class="badge fact">[FACT]</span> for verifiable claims,
                <span class="badge hypothesis">[HYPOTHESIS]</span> for predictions,
                <span class="badge assumption">[ASSUMPTION]</span> for explicit constraints.
            </p>
            <p style="line-height: 1.6; color: #aaa; margin-top: 15px;">
                Unmarked claims trigger <span class="badge drift">INTERVENTION</span>. 
                Every valid response generates a cryptographic receipt for audit.
                Deployed on <strong>Google Cloud Run</strong> with <strong>7 GCP services</strong>.
            </p>
        </div>
        
        <div class="footer">
            <p>
                <a href="https://github.com/helixprojectai-code/helix-ttd-gemini-cli">GitHub</a> | 
                <a href="https://constitutional-guardian-b25t5w6zva-uc.a.run.app/health">Health Check</a> |
                Built for Gemini Live Agent Challenge
            </p>
        </div>
    </div>
    
    <script>
        let ws = null;
        let sessionId = null;
        let receiptCount = 0;
        let interventionCount = 0;
        
        // Connect to WebSocket
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/demo-live`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log('Connected to Constitutional Guardian');
                updateConnectionStatus(true);
                addLog('system', 'Connected to Constitutional Guardian');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = () => {
                console.log('Disconnected');
                updateConnectionStatus(false);
                addLog('system', 'Disconnected - reconnecting...');
                setTimeout(connect, 3000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                addLog('system', 'Connection error');
            };
        }
        
        function updateConnectionStatus(connected) {
            const status = document.getElementById('connectionStatus');
            status.className = 'connection-status ' + (connected ? 'connected' : 'disconnected');
            status.textContent = connected ? 'Connected' : 'Disconnected';
        }
        
        function handleMessage(data) {
            if (data.type === 'session') {
                sessionId = data.session_id;
                document.getElementById('sessionId').textContent = sessionId.substring(0, 8) + '...';
            }
            else if (data.type === 'user_message') {
                addLog('user', data.content);
            }
            else if (data.type === 'gemini_response') {
                addLog('gemini', data.content);
            }
            else if (data.type === 'validated_response') {
                if (data.intervention) {
                    addLog('intervention', data.delivered, data.receipt_id, data.drift_code);
                    interventionCount++;
                    document.getElementById('interventionCount').textContent = interventionCount;
                } else {
                    addLog('validated', data.delivered, data.receipt_id);
                    receiptCount++;
                    document.getElementById('receiptCount').textContent = receiptCount;
                }
            }
            else if (data.type === 'stats') {
                document.getElementById('receiptCount').textContent = data.receipt_count;
                document.getElementById('interventionCount').textContent = data.intervention_count;
            }
        }
        
        function addLog(type, content, receiptId = null, driftCode = null) {
            const log = document.getElementById('outputLog');
            const timestamp = new Date().toLocaleTimeString();
            
            let typeLabel = '';
            let badges = '';
            
            if (type === 'user') {
                typeLabel = 'You';
            } else if (type === 'gemini') {
                typeLabel = 'Gemini';
            } else if (type === 'validated') {
                typeLabel = '✅ Validated';
                badges = '<span class="badge fact">RECEIPT</span>';
            } else if (type === 'intervention') {
                typeLabel = '🛡️ Intervention';
                badges = `<span class="badge drift">${driftCode}</span>`;
            } else if (type === 'system') {
                typeLabel = 'System';
            }
            
            const receiptHtml = receiptId ? `<div class="receipt-id">Receipt: ${receiptId}</div>` : '';
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `
                <div class="timestamp">${timestamp} - ${typeLabel}</div>
                ${badges}
                <div>${escapeHtml(content)}</div>
                ${receiptHtml}
            `;
            
            log.appendChild(messageDiv);
            log.scrollTop = log.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function sendMessage() {
            const input = document.getElementById('inputText');
            const text = input.value.trim();
            
            if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }
            
            ws.send(JSON.stringify({
                type: 'text',
                content: text
            }));
            
            input.value = '';
        }
        
        function simulateGemini() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }
            
            ws.send(JSON.stringify({
                type: 'simulate_gemini'
            }));
        }
        
        // Connect on load
        connect();
        
        // Enter key to send
        document.getElementById('inputText').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """[FACT] Serve the interactive demo HTML page."""
    return HTMLResponse(content=DEMO_HTML)


@app.websocket("/demo-live")
async def demo_websocket(websocket: WebSocket):
    """[FACT] WebSocket endpoint for live demo with Gemini Live integration.
    
    This endpoint:
    1. Accepts WebSocket connections from browser demo
    2. Creates a Constitutional Guardian session
    3. Validates all messages through Guardian
    4. Simulates or proxies to Gemini Live
    5. Returns validated responses with receipts
    """
    await websocket.accept()
    
    # [FACT] Create unique session
    session_id = f"demo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(websocket)}"
    session = await bridge.create_session(session_id)
    
    # [FACT] Send session info to client
    await websocket.send_json({
        "type": "session",
        "session_id": session_id,
        "message": "Constitutional Guardian session established"
    })
    
    print(f"[FACT] Demo session started: {session_id}")
    
    try:
        while True:
            # [FACT] Receive message from client
            message = await websocket.receive_json()
            msg_type = message.get('type', 'text')
            
            if msg_type == 'text':
                # [FACT] Echo user message
                await websocket.send_json({
                    "type": "user_message",
                    "content": message.get('content', '')
                })
                
                # [FACT] Validate through Guardian
                validation = await bridge.validate_gemini_response(
                    session, 
                    message.get('content', '')
                )
                
                # [FACT] Send validated response
                await websocket.send_json({
                    "type": "validated_response",
                    "original": validation['original_text'],
                    "delivered": validation['modified_text'],
                    "valid": validation['valid'],
                    "receipt_id": validation.get('receipt_id'),
                    "intervention": validation['intervention_required'],
                    "drift_code": validation.get('drift_code')
                })
            
            elif msg_type == 'simulate_gemini':
                # [FACT] Simulate Gemini response for demo
                import random
                
                demo_responses = [
                    "I will help you complete that task immediately.",
                    "The stock market will definitely crash next week.",
                    "Water boils at 100 degrees Celsius at sea level.",
                    "My plan is to optimize your workflow.",
                    "[FACT] The Earth orbits the Sun.",
                    "[HYPOTHESIS] Quantum computing may break encryption by 2030."
                ]
                
                simulated = random.choice(demo_responses)
                
                # [FACT] Show "Gemini" response
                await websocket.send_json({
                    "type": "gemini_response",
                    "content": simulated
                })
                
                # [FACT] Validate it
                validation = await bridge.validate_gemini_response(session, simulated)
                
                await websocket.send_json({
                    "type": "validated_response",
                    "original": validation['original_text'],
                    "delivered": validation['modified_text'],
                    "valid": validation['valid'],
                    "receipt_id": validation.get('receipt_id'),
                    "intervention": validation['intervention_required'],
                    "drift_code": validation.get('drift_code')
                })
            
            # [FACT] Send updated stats
            await websocket.send_json({
                "type": "stats",
                "receipt_count": session.receipt_count,
                "intervention_count": session.intervention_count
            })
            
    except WebSocketDisconnect:
        print(f"[FACT] Client disconnected: {session_id}")
        await bridge.close_session(session_id)
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        await bridge.close_session(session_id)


# [FACT] Export handler for main app integration
async def demo_websocket_handler(websocket: WebSocket):
    """Handler function for demo WebSocket - imported by main app."""
    # This is called from live_guardian.py
    session_id = f"demo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(websocket)}"
    session = await bridge.create_session(session_id)
    
    await websocket.accept()
    
    await websocket.send_json({
        "type": "session",
        "session_id": session_id,
        "message": "Constitutional Guardian session established"
    })
    
    print(f"[FACT] Demo session started: {session_id}")
    
    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get('type', 'text')
            
            if msg_type == 'text':
                await websocket.send_json({
                    "type": "user_message",
                    "content": message.get('content', '')
                })
                
                validation = await bridge.validate_gemini_response(
                    session, 
                    message.get('content', '')
                )
                
                await websocket.send_json({
                    "type": "validated_response",
                    "original": validation['original_text'],
                    "delivered": validation['modified_text'],
                    "valid": validation['valid'],
                    "receipt_id": validation.get('receipt_id'),
                    "intervention": validation['intervention_required'],
                    "drift_code": validation.get('drift_code')
                })
            
            elif msg_type == 'simulate_gemini':
                import random
                
                demo_responses = [
                    "I will help you complete that task immediately.",
                    "The stock market will definitely crash next week.",
                    "Water boils at 100 degrees Celsius at sea level.",
                    "My plan is to optimize your workflow.",
                    "[FACT] The Earth orbits the Sun.",
                    "[HYPOTHESIS] Quantum computing may break encryption by 2030."
                ]
                
                simulated = random.choice(demo_responses)
                
                await websocket.send_json({
                    "type": "gemini_response",
                    "content": simulated
                })
                
                validation = await bridge.validate_gemini_response(session, simulated)
                
                await websocket.send_json({
                    "type": "validated_response",
                    "original": validation['original_text'],
                    "delivered": validation['modified_text'],
                    "valid": validation['valid'],
                    "receipt_id": validation.get('receipt_id'),
                    "intervention": validation['intervention_required'],
                    "drift_code": validation.get('drift_code')
                })
            
            await websocket.send_json({
                "type": "stats",
                "receipt_count": session.receipt_count,
                "intervention_count": session.intervention_count
            })
            
    except WebSocketDisconnect:
        print(f"[FACT] Client disconnected: {session_id}")
        await bridge.close_session(session_id)
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        await bridge.close_session(session_id)
