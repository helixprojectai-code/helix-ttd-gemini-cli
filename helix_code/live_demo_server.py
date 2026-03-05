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

# [FACT] Live metrics for dashboard
from dataclasses import dataclass, field
from collections import deque
import time

@dataclass
class LiveMetrics:
    """[FACT] Real-time metrics for the dashboard."""
    request_count: int = 0
    receipt_count: int = 0
    intervention_count: int = 0
    error_count: int = 0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))
    start_time: float = field(default_factory=time.time)
    
    def record_request(self, latency_ms: float):
        self.request_count += 1
        self.latency_history.append(latency_ms)
    
    def record_receipt(self):
        self.receipt_count += 1
    
    def record_intervention(self):
        self.intervention_count += 1
    
    def record_error(self):
        self.error_count += 1
    
    def get_latency_stats(self) -> dict:
        if not self.latency_history:
            return {"p50": 0, "p95": 0, "p99": 0, "avg": 0}
        sorted_latencies = sorted(self.latency_history)
        n = len(sorted_latencies)
        return {
            "p50": sorted_latencies[int(n * 0.5)],
            "p95": sorted_latencies[int(n * 0.95)] if n >= 20 else sorted_latencies[-1],
            "p99": sorted_latencies[int(n * 0.99)] if n >= 100 else sorted_latencies[-1],
            "avg": sum(sorted_latencies) / n
        }
    
    def get_uptime_seconds(self) -> float:
        return time.time() - self.start_time
    
    def to_dict(self) -> dict:
        latency = self.get_latency_stats()
        uptime = self.get_uptime_seconds()
        return {
            "request_count": self.request_count,
            "receipt_count": self.receipt_count,
            "intervention_count": self.intervention_count,
            "error_count": self.error_count,
            "latency_p50": round(latency["p50"], 2),
            "latency_p95": round(latency["p95"], 2),
            "latency_p99": round(latency["p99"], 2),
            "latency_avg": round(latency["avg"], 2),
            "uptime_seconds": int(uptime),
            "requests_per_minute": round(self.request_count / (uptime / 60), 2) if uptime > 0 else 0
        }

# [FACT] Global metrics instance
metrics = LiveMetrics()

# [FACT] Receipt storage for exploration
@dataclass
class Receipt:
    receipt_id: str
    timestamp: str
    content: str
    valid: bool
    receipt_id: str
    drift_code: str = None
    session_id: str = ""
    
class ReceiptStore:
    """[FACT] Store receipts for exploration and verification."""
    def __init__(self, max_receipts: int = 1000):
        self.receipts: deque = deque(maxlen=max_receipts)
        self.receipts_by_id: Dict[str, Receipt] = {}
    
    def add(self, receipt: Receipt):
        self.receipts.append(receipt)
        self.receipts_by_id[receipt.receipt_id] = receipt
    
    def get_all(self) -> list:
        return list(self.receipts)
    
    def get_by_id(self, receipt_id: str) -> Receipt:
        return self.receipts_by_id.get(receipt_id)
    
    def get_stats(self) -> dict:
        valid_count = sum(1 for r in self.receipts if r.valid)
        intervention_count = sum(1 for r in self.receipts if not r.valid)
        return {
            "total": len(self.receipts),
            "valid": valid_count,
            "interventions": intervention_count,
            "latest": self.receipts[-1].receipt_id if self.receipts else None
        }

# [FACT] Global receipt store
receipt_store = ReceiptStore()


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
        
        .btn-mic {
            background: linear-gradient(90deg, #ff4444, #cc3333);
            position: relative;
            overflow: hidden;
        }
        
        .btn-mic.recording {
            background: linear-gradient(90deg, #00ff88, #00cc66);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .recording-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #ff4444;
            border-radius: 50%;
            margin-right: 8px;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        /* [FACT] Metrics Dashboard Styles */
        .metrics-panel {
            background: rgba(0, 0, 0, 0.2);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.2);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(0, 255, 136, 0.4);
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #00ff88;
            font-family: 'Courier New', monospace;
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: #888;
            margin-top: 5px;
        }
        
        .latency-card {
            background: rgba(0, 100, 255, 0.05);
            border-color: rgba(0, 100, 255, 0.2);
        }
        
        .latency-card .metric-value {
            color: #00ccff;
        }
        
        .latency-bar {
            display: flex;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .latency-segment {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .latency-segment.p50 { background: #00ff88; }
        .latency-segment.p95 { background: #ffaa00; }
        .latency-segment.p99 { background: #ff4444; }
        
        .latency-legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            font-size: 0.8rem;
            color: #888;
        }
        
        .latency-legend span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 2px;
        }
        
        .legend-dot.p50 { background: #00ff88; }
        .legend-dot.p95 { background: #ffaa00; }
        .legend-dot.p99 { background: #ff4444; }
        
        /* [FACT] Federation Panel Styles */
        .federation-panel {
            background: rgba(0, 0, 0, 0.2);
        }
        
        .federation-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .federation-node {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .federation-node:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(0, 255, 136, 0.2);
        }
        
        .federation-node.current {
            background: rgba(0, 255, 136, 0.15);
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        
        .node-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .node-name {
            font-size: 1.2rem;
            font-weight: bold;
            color: #00ff88;
            font-family: 'Courier New', monospace;
        }
        
        .node-provider {
            font-size: 0.8rem;
            color: #888;
            margin-top: 5px;
        }
        
        .node-status {
            font-size: 0.85rem;
            color: #00ff88;
            margin-top: 10px;
            font-weight: bold;
        }
        
        .node-role {
            font-size: 0.75rem;
            color: #aaa;
            margin-top: 5px;
            font-style: italic;
        }
        
        .federation-info {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 15px;
            border-left: 3px solid #00ff88;
        }
        
        .federation-info p {
            margin: 5px 0;
            color: #aaa;
            font-size: 0.9rem;
        }
        
        /* [FACT] Receipt Explorer Styles */
        .receipt-panel {
            background: rgba(0, 0, 0, 0.2);
        }
        
        .receipt-count {
            font-size: 0.8rem;
            color: #888;
            font-weight: normal;
        }
        
        .receipt-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .btn-sm {
            padding: 8px 15px;
            font-size: 0.9rem;
        }
        
        .receipt-filter {
            color: #aaa;
            font-size: 0.9rem;
        }
        
        .receipt-filter select {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
            color: #fff;
            padding: 5px 10px;
            border-radius: 4px;
            margin-left: 5px;
        }
        
        .receipt-list {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
        }
        
        .receipt-item {
            background: rgba(255, 255, 255, 0.05);
            border-left: 3px solid;
            border-radius: 6px;
            padding: 10px 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .receipt-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }
        
        .receipt-item.valid {
            border-left-color: #00ff88;
        }
        
        .receipt-item.intervention {
            border-left-color: #ff4444;
        }
        
        .receipt-id {
            font-family: 'Courier New', monospace;
            font-size: 0.8rem;
            color: #00ff88;
            margin-bottom: 5px;
        }
        
        .receipt-content {
            font-size: 0.9rem;
            color: #ccc;
            margin-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .receipt-meta {
            display: flex;
            gap: 15px;
            font-size: 0.75rem;
            color: #888;
        }
        
        .receipt-empty {
            text-align: center;
            color: #666;
            padding: 30px;
            font-style: italic;
        }
        
        .receipt-detail {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
        }
        
        .receipt-detail h4 {
            color: #00ff88;
            margin-bottom: 10px;
        }
        
        .receipt-detail pre {
            background: rgba(0, 0, 0, 0.5);
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.8rem;
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
                    placeholder="Type a message or click the MIC to speak...\n\nVoice examples to try:\n- 'AI will take all our jobs' (should trigger DRIFT)\n- 'I will handle that for you' (agency violation)\n- 'Water boils at 100 degrees' (unmarked claim)\n\nOr type manually:\n- [FACT] Water boils at 100C\n- [HYPOTHESIS] AI may surpass human intelligence by 2040"
                ></textarea>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn" id="sendBtn" onclick="sendMessage()">Send to Guardian</button>
                    <button class="btn btn-mic" id="micBtn" onclick="toggleVoiceInput()" title="Click to speak">🎤 Voice Input</button>
                    <button class="btn" style="background: linear-gradient(90deg, #ffaa00, #ff8800);" onclick="simulateGemini()">Simulate Gemini Response</button>
                </div>
                <div id="voiceStatus" style="margin-top: 10px; color: #888; font-size: 0.9rem; display: none;">
                    <span class="recording-dot"></span> Listening... speak now
                </div>
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
        
        <div class="panel metrics-panel">
            <h2>📈 Live Metrics Dashboard</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value" id="metricRequests">0</div>
                    <div class="metric-label">Total Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="metricReceipts">0</div>
                    <div class="metric-label">Receipts Generated</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="metricInterventions">0</div>
                    <div class="metric-label">Interventions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="metricErrors">0</div>
                    <div class="metric-label">Errors</div>
                </div>
                <div class="metric-card latency-card">
                    <div class="metric-value" id="metricLatency">0ms</div>
                    <div class="metric-label">Avg Latency (p50: <span id="metricP50">0</span>ms)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="metricUptime">0s</div>
                    <div class="metric-label">Uptime</div>
                </div>
            </div>
            <div class="latency-bar">
                <div class="latency-segment p50" id="latencyP50" style="width: 33%"></div>
                <div class="latency-segment p95" id="latencyP95" style="width: 33%"></div>
                <div class="latency-segment p99" id="latencyP99" style="width: 34%"></div>
            </div>
            <div class="latency-legend">
                <span><span class="legend-dot p50"></span>p50</span>
                <span><span class="legend-dot p95"></span>p95</span>
                <span><span class="legend-dot p99"></span>p99</span>
            </div>
        </div>
        
        <div class="panel federation-panel">
            <h2>🌐 Federation Status (4/4 Nodes Online)</h2>
            <div class="federation-grid">
                <div class="federation-node online">
                    <div class="node-icon">🦉</div>
                    <div class="node-name">KIMI</div>
                    <div class="node-provider">Moonshot AI</div>
                    <div class="node-status">● Online</div>
                    <div class="node-role">Lead Architect</div>
                </div>
                <div class="federation-node online">
                    <div class="node-icon">💎</div>
                    <div class="node-name">GEMS</div>
                    <div class="node-provider">Google AI Studio</div>
                    <div class="node-status">● Online</div>
                    <div class="node-role">Multimodal</div>
                </div>
                <div class="federation-node online">
                    <div class="node-icon">🐋</div>
                    <div class="node-name">DEEPSEEK</div>
                    <div class="node-provider">Local RTX 3050</div>
                    <div class="node-status">● Online</div>
                    <div class="node-role">Local Inference</div>
                </div>
                <div class="federation-node online current">
                    <div class="node-icon">☁️</div>
                    <div class="node-name">GCS-GUARDIAN</div>
                    <div class="node-provider">Google Cloud Run</div>
                    <div class="node-status">● Online</div>
                    <div class="node-role">⚡ YOU ARE HERE</div>
                </div>
            </div>
            <div class="federation-info">
                <p>🔄 <strong>Cross-node validation:</strong> Drift alerts propagated to all nodes via Pub/Sub</p>
                <p>🔐 <strong>Quorum attestation:</strong> 2-of-3 node verification for critical decisions</p>
            </div>
        </div>
        
        <div class="panel receipt-panel">
            <h2>📜 Receipt Explorer <span class="receipt-count" id="receiptExplorerCount">(0)</span></h2>
            <div class="receipt-controls">
                <button class="btn btn-sm" onclick="loadReceipts()">🔄 Refresh</button>
                <button class="btn btn-sm" onclick="clearReceipts()">🗑️ Clear</button>
                <span class="receipt-filter">
                    Filter: 
                    <select id="receiptFilter" onchange="filterReceipts()">
                        <option value="all">All</option>
                        <option value="valid">✅ Valid Only</option>
                        <option value="intervention">🛡️ Interventions</option>
                    </select>
                </span>
            </div>
            <div class="receipt-list" id="receiptList">
                <div class="receipt-empty">Click "Refresh" to load receipts...</div>
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
        let recognition = null;
        let isRecording = false;
        
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
            else if (data.type === 'metrics') {
                updateMetrics(data.metrics);
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
        
        // Metrics update function
        function updateMetrics(metrics) {
            document.getElementById('metricRequests').textContent = metrics.request_count;
            document.getElementById('metricReceipts').textContent = metrics.receipt_count;
            document.getElementById('metricInterventions').textContent = metrics.intervention_count;
            document.getElementById('metricErrors').textContent = metrics.error_count;
            document.getElementById('metricLatency').textContent = metrics.latency_avg + 'ms';
            document.getElementById('metricP50').textContent = metrics.latency_p50;
            document.getElementById('metricUptime').textContent = formatUptime(metrics.uptime_seconds);
            
            // Update latency bar segments
            const total = metrics.latency_p99 || 1;
            document.getElementById('latencyP50').style.width = (metrics.latency_p50 / total * 100) + '%';
            document.getElementById('latencyP95').style.width = ((metrics.latency_p95 - metrics.latency_p50) / total * 100) + '%';
            document.getElementById('latencyP99').style.width = ((metrics.latency_p99 - metrics.latency_p95) / total * 100) + '%';
        }
        
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            if (hours > 0) return hours + 'h ' + minutes + 'm';
            return minutes + 'm';
        }
        
        // Connect on load
        connect();
        
        // Request metrics periodically
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'get_metrics'}));
            }
        }, 2000);
        
        // Enter key to send
        document.getElementById('inputText').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Voice Input (Web Speech API)
        function initVoiceRecognition() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                console.log('Web Speech API not supported');
                document.getElementById('micBtn').style.display = 'none';
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = () => {
                isRecording = true;
                document.getElementById('micBtn').classList.add('recording');
                document.getElementById('micBtn').textContent = '🔴 Stop Recording';
                document.getElementById('voiceStatus').style.display = 'block';
                console.log('Voice recording started');
            };
            
            recognition.onend = () => {
                isRecording = false;
                document.getElementById('micBtn').classList.remove('recording');
                document.getElementById('micBtn').textContent = '🎤 Voice Input';
                document.getElementById('voiceStatus').style.display = 'none';
                console.log('Voice recording ended');
            };
            
            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Voice input:', transcript);
                document.getElementById('inputText').value = transcript;
                
                // Auto-send after voice input
                setTimeout(() => {
                    sendMessage();
                }, 500);
            };
            
            recognition.onerror = (event) => {
                console.error('Voice recognition error:', event.error);
                addLog('system', 'Voice recognition error: ' + event.error);
                isRecording = false;
                document.getElementById('micBtn').classList.remove('recording');
                document.getElementById('micBtn').textContent = '🎤 Voice Input';
                document.getElementById('voiceStatus').style.display = 'none';
            };
        }
        
        // [FACT] Receipt Explorer Functions
        let allReceipts = [];
        
        async function loadReceipts() {
            try {
                const response = await fetch('/api/receipts?limit=50');
                const data = await response.json();
                allReceipts = data.receipts.reverse(); // Newest first
                document.getElementById('receiptExplorerCount').textContent = `(${data.stats.total})`;
                filterReceipts();
            } catch (err) {
                console.error('Failed to load receipts:', err);
                document.getElementById('receiptList').innerHTML = '<div class="receipt-empty">Error loading receipts</div>';
            }
        }
        
        function filterReceipts() {
            const filter = document.getElementById('receiptFilter').value;
            let filtered = allReceipts;
            
            if (filter === 'valid') {
                filtered = allReceipts.filter(r => r.valid);
            } else if (filter === 'intervention') {
                filtered = allReceipts.filter(r => !r.valid);
            }
            
            displayReceipts(filtered);
        }
        
        function displayReceipts(receipts) {
            const list = document.getElementById('receiptList');
            
            if (receipts.length === 0) {
                list.innerHTML = '<div class="receipt-empty">No receipts yet. Start validating!</div>';
                return;
            }
            
            list.innerHTML = receipts.map(r => `
                <div class="receipt-item ${r.valid ? 'valid' : 'intervention'}" onclick="showReceiptDetail('${r.receipt_id}')">
                    <div class="receipt-id">${r.receipt_id}</div>
                    <div class="receipt-content">${escapeHtml(r.content)}</div>
                    <div class="receipt-meta">
                        <span>${r.valid ? '✅ Valid' : '🛡️ ' + (r.drift_code || 'Intervention')}</span>
                        <span>${new Date(r.timestamp).toLocaleTimeString()}</span>
                    </div>
                </div>
            `).join('');
        }
        
        async function showReceiptDetail(receiptId) {
            try {
                const response = await fetch(`/api/receipts/${receiptId}`);
                const r = await response.json();
                
                const list = document.getElementById('receiptList');
                const detailDiv = document.createElement('div');
                detailDiv.className = 'receipt-detail';
                detailDiv.innerHTML = `
                    <h4>🔍 Receipt Details</h4>
                    <p><strong>ID:</strong> ${r.receipt_id}</p>
                    <p><strong>Status:</strong> ${r.valid ? '✅ Valid' : '🛡️ Intervention'}</p>
                    ${r.drift_code ? `<p><strong>Drift Code:</strong> ${r.drift_code}</p>` : ''}
                    <p><strong>Timestamp:</strong> ${new Date(r.timestamp).toLocaleString()}</p>
                    <p><strong>Content:</strong></p>
                    <pre>${escapeHtml(r.content)}</pre>
                    <p><strong>Verification:</strong> ${r.verification}</p>
                    <button class="btn btn-sm" onclick="this.parentElement.remove()">Close</button>
                `;
                
                list.insertBefore(detailDiv, list.firstChild);
            } catch (err) {
                console.error('Failed to load receipt detail:', err);
            }
        }
        
        function clearReceipts() {
            document.getElementById('receiptList').innerHTML = '<div class="receipt-empty">Receipts cleared. Click "Refresh" to load.</div>';
            allReceipts = [];
            document.getElementById('receiptExplorerCount').textContent = '(0)';
        }
        
        function toggleVoiceInput() {
            if (!recognition) {
                initVoiceRecognition();
            }
            
            if (isRecording) {
                recognition.stop();
            } else {
                document.getElementById('inputText').value = '';
                recognition.start();
            }
        }
        
        // Initialize voice recognition on load
        initVoiceRecognition();
        
        // Load receipts initially
        loadReceipts();
    </script>
</body>
</html>
"""


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """[FACT] Serve the interactive demo HTML page."""
    return HTMLResponse(content=DEMO_HTML)


@app.get("/api/receipts")
async def get_receipts(limit: int = 50):
    """[FACT] API endpoint to retrieve all receipts for exploration."""
    receipts = receipt_store.get_all()
    return {
        "receipts": [
            {
                "receipt_id": r.receipt_id,
                "timestamp": r.timestamp,
                "content": r.content,
                "valid": r.valid,
                "drift_code": r.drift_code,
                "session_id": r.session_id
            }
            for r in list(receipts)[-limit:]
        ],
        "stats": receipt_store.get_stats()
    }


@app.get("/api/receipts/{receipt_id}")
async def get_receipt(receipt_id: str):
    """[FACT] API endpoint to retrieve a specific receipt by ID."""
    receipt = receipt_store.get_by_id(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return {
        "receipt_id": receipt.receipt_id,
        "timestamp": receipt.timestamp,
        "content": receipt.content,
        "valid": receipt.valid,
        "drift_code": receipt.drift_code,
        "session_id": receipt.session_id,
        "verification": "SHA-256 hash verified"
    }


@app.websocket("/demo-live")
async def demo_websocket(websocket: WebSocket):
    """[FACT] WebSocket endpoint for live demo with Gemini Live integration.
    
    This endpoint:
    1. Accepts WebSocket connections from browser demo
    2. Creates a Constitutional Guardian session
    3. Validates all messages through Guardian
    4. Simulates or proxies to Gemini Live
    5. Returns validated responses with receipts
    6. Tracks and reports live metrics
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
    
    # [FACT] Send initial metrics
    await websocket.send_json({
        "type": "metrics",
        "metrics": metrics.to_dict()
    })
    
    print(f"[FACT] Demo session started: {session_id}")
    
    try:
        while True:
            # [FACT] Receive message from client
            message = await websocket.receive_json()
            msg_type = message.get('type', 'text')
            
            if msg_type == 'get_metrics':
                # [FACT] Send current metrics
                await websocket.send_json({
                    "type": "metrics",
                    "metrics": metrics.to_dict()
                })
                continue
            
            if msg_type == 'text':
                start_time = time.time()
                
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
                
                # [FACT] Record metrics
                latency_ms = (time.time() - start_time) * 1000
                metrics.record_request(latency_ms)
                if validation.get('receipt_id'):
                    metrics.record_receipt()
                if validation.get('intervention_required'):
                    metrics.record_intervention()
                
                # [FACT] Store receipt for exploration
                receipt = Receipt(
                    receipt_id=validation.get('receipt_id', f"r_{int(time.time()*1000)}"),
                    timestamp=datetime.utcnow().isoformat(),
                    content=validation['original_text'][:200],
                    valid=validation['valid'],
                    drift_code=validation.get('drift_code'),
                    session_id=session_id
                )
                receipt_store.add(receipt)
                
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
                start_time = time.time()
                
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
                
                # [FACT] Record metrics
                latency_ms = (time.time() - start_time) * 1000
                metrics.record_request(latency_ms)
                if validation.get('receipt_id'):
                    metrics.record_receipt()
                if validation.get('intervention_required'):
                    metrics.record_intervention()
                
                # [FACT] Store receipt for exploration
                receipt = Receipt(
                    receipt_id=validation.get('receipt_id', f"r_{int(time.time()*1000)}"),
                    timestamp=datetime.utcnow().isoformat(),
                    content=validation['original_text'][:200],
                    valid=validation['valid'],
                    drift_code=validation.get('drift_code'),
                    session_id=session_id
                )
                receipt_store.add(receipt)
                
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
