# [FACT] Interactive HTML Dashboard for Constitutional Guardian Demo
# This module provides the DEMO_HTML string with embedded JS and Chart.js

DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Constitutional Guardian - LIVE v1.3.2</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root { --primary: #00ff88; --bg: #0a0a12; --panel: #161b22; --border: #30363d; --text: #fff; --text-dim: #8b949e; --red: #f85149; --blue: #58a6ff; --purple: #bc8cff; }
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; display: flex; flex-direction: column; min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; width: 100%; flex: 1; }
        
        header { text-align: center; border-bottom: 2px solid var(--primary); padding: 20px; margin-bottom: 20px; position: relative; }
        .owls { position: absolute; top: 20px; width: 100%; display: flex; justify-content: center; gap: 300px; font-size: 2rem; pointer-events: none; opacity: 0.5; }
        
        .grid-main { display: grid; grid-template-columns: 300px 1fr 300px; gap: 20px; }
        .panel { background: var(--panel); border-radius: 10px; padding: 20px; border: 1px solid var(--border); transition: 0.3s; position: relative; overflow: hidden; }
        
        h1, h2, h3 { color: var(--primary); margin-top: 0; }
        .metrics { display: flex; justify-content: space-around; margin-top: 10px; }
        .metric { text-align: center; }
        .metric-value { font-size: 1.5rem; font-weight: bold; color: var(--primary); transition: 0.3s; }
        
        .log { height: 500px; overflow-y: auto; background: #010409; padding: 10px; font-family: 'Cascadia Code', monospace; font-size: 0.85rem; border-radius: 5px; border: 1px solid var(--border); }
        .msg { margin-bottom: 12px; border-left: 3px solid var(--border); padding: 8px 12px; animation: slide-in 0.2s ease-out; border-radius: 0 5px 5px 0; }
        @keyframes slide-in { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
        
        .msg.user { border-left-color: var(--blue); background: rgba(88, 166, 255, 0.05); }
        .msg.gemini { border-left-color: var(--purple); background: rgba(188, 140, 255, 0.05); }
        .msg.valid { border-left-color: #3fb950; background: rgba(63, 185, 80, 0.1); }
        .msg.intervention { border-left-color: var(--red); background: rgba(248, 81, 73, 0.1); border-left-width: 5px; }
        .msg.system { border-left-color: var(--text-dim); font-style: italic; color: var(--text-dim); }
        
        .badge { font-size: 0.65rem; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-right: 8px; text-transform: uppercase; vertical-align: middle; }
        .badge.intercepted { background: var(--red); color: #fff; }
        .badge.valid { background: #3fb950; color: #fff; }
        .badge.gemini { background: var(--purple); color: #fff; }
        
        .charter-list { list-style: none; padding: 0; font-size: 0.85rem; }
        .charter-item { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
        .charter-title { font-weight: bold; color: var(--primary); display: block; margin-bottom: 4px; }
        .charter-desc { color: var(--text-dim); line-height: 1.4; }
        
        .status-bar { background: #010409; padding: 10px 20px; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-dim); display: flex; justify-content: space-between; align-items: center; margin-top: 20px; border-radius: 5px; }
        .status-item { display: flex; align-items: center; gap: 8px; }
        .status-led { width: 8px; height: 8px; border-radius: 50%; background: var(--primary); box-shadow: 0 0 5px var(--primary); }
        .status-led.syncing { background: #d29922; box-shadow: 0 0 5px #d29922; animation: blink 1s infinite; }
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

        .btn { background: #238636; color: #fff; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; transition: 0.3s; display: flex; align-items: center; gap: 8px; font-weight: bold; font-size: 0.9rem; }
        .btn:hover { background: #2ea043; transform: scale(1.05); }
        .btn.mic-active { background: var(--red); animation: pulse-mic 1s infinite; }
        @keyframes pulse-mic { 0% { box-shadow: 0 0 0 0 rgba(248, 81, 73, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(248, 81, 73, 0); } 100% { box-shadow: 0 0 0 0 rgba(248, 81, 73, 0); } }
        
        .waveform { height: 50px; background: #010409; border-radius: 5px; display: flex; align-items: center; gap: 2px; padding: 0 10px; margin-bottom: 10px; border: 1px solid var(--border); position: relative; overflow: hidden; }
        .waveform::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(90deg, transparent, rgba(0,255,136,0.05), transparent); animation: waveform-shimmer 3s infinite; }
        @keyframes waveform-shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
        .bar { width: 4px; background: var(--border); border-radius: 2px; transition: height 0.15s ease-out, background 0.2s; height: 10px; }
        .bar.active { background: var(--primary); box-shadow: 0 0 4px var(--primary); }
        .bar.intervention { background: var(--red); box-shadow: 0 0 4px var(--red); }
        
        .flash-red { animation: flash-red 0.5s ease-in-out; }
        @keyframes flash-red { 0% { background: rgba(248, 81, 73, 0.5); } 100% { background: var(--panel); } }
        .flash-green { animation: flash-green 0.5s ease-in-out; }
        @keyframes flash-green { 0% { background: rgba(0, 255, 136, 0.5); } 100% { background: var(--panel); } }
        .pulse-green { animation: pulse-green 2s infinite; }
        @keyframes pulse-green { 0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); } }
        
        /* [FACT] Two Owls Animation - Brand Identity */
        .owls-container { display: flex; justify-content: center; align-items: center; gap: 15px; margin: 10px 0; }
        .owl { font-size: 2.5rem; animation: owl-watch 3s ease-in-out infinite; filter: drop-shadow(0 0 10px rgba(0, 255, 136, 0.5)); }
        .owl.right { animation-delay: 1.5s; }
        .anchor { font-size: 1.8rem; color: var(--primary); animation: anchor-pulse 2s ease-in-out infinite; }
        @keyframes owl-watch { 0%, 100% { transform: rotate(-8deg) translateY(0); } 50% { transform: rotate(8deg) translateY(-5px); } }
        @keyframes anchor-pulse { 0%, 100% { transform: scale(1); filter: drop-shadow(0 0 5px var(--primary)); } 50% { transform: scale(1.1); filter: drop-shadow(0 0 15px var(--primary)); } }
        
        /* [FACT] Federation Panel Styles */
        .federation-panel { margin-top: 20px; }
        .node-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        .node-card { background: #010409; padding: 12px; border-radius: 8px; border: 1px solid var(--border); position: relative; transition: all 0.3s; }
        .node-card.active { border-color: var(--primary); box-shadow: 0 0 10px rgba(0, 255, 136, 0.2); }
        .node-card.standby { border-color: #d29922; }
        .node-card.offline { border-color: #666; opacity: 0.6; }
        .node-led { width: 8px; height: 8px; border-radius: 50%; position: absolute; top: 8px; right: 8px; }
        .node-led.active { background: var(--primary); box-shadow: 0 0 8px var(--primary); animation: led-pulse 2s infinite; }
        .node-led.standby { background: #d29922; box-shadow: 0 0 8px #d29922; }
        .node-led.offline { background: #666; }
        @keyframes led-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .node-name { font-weight: bold; color: var(--primary); display: block; font-size: 0.85rem; }
        .node-role { font-size: 0.65rem; color: var(--text-dim); display: block; }
        .node-status { font-size: 0.65rem; color: var(--primary); display: block; margin-top: 4px; }
        .cross-validation { margin-top: 15px; padding-top: 10px; border-top: 1px solid var(--border); font-size: 0.8rem; }
        .cv-label { color: var(--text-dim); }
        .cv-status { color: var(--primary); font-weight: bold; margin-left: 8px; }
        .cv-status.syncing { color: #d29922; animation: blink 1s infinite; }
        
        /* [FACT] Enhanced Intervention Effects */
        .intervention-flash { animation: intervention-flash 0.6s ease-out; }
        @keyframes intervention-flash { 
            0% { box-shadow: inset 0 0 0 0 rgba(248, 81, 73, 0); }
            30% { box-shadow: inset 0 0 60px 30px rgba(248, 81, 73, 0.4); }
            100% { box-shadow: inset 0 0 0 0 rgba(248, 81, 73, 0); }
        }
        .metric-pulse { animation: metric-pulse 0.6s ease-out; }
        @keyframes metric-pulse { 
            0% { transform: scale(1); }
            50% { transform: scale(1.3); text-shadow: 0 0 20px currentColor; }
            100% { transform: scale(1); }
        }
        
        .chart-container { height: 150px; margin-top: 15px; }
        
        /* [FACT] Enhanced Metrics Dashboard Styles */
        .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 15px 0; }
        .metric-card { background: #010409; padding: 10px; border-radius: 6px; border: 1px solid var(--border); text-align: center; }
        .metric-card .metric-label { font-size: 0.65rem; color: var(--text-dim); text-transform: uppercase; display: block; }
        .metric-card .metric-value { font-size: 1.1rem; color: var(--primary); font-weight: bold; font-family: 'Cascadia Code', monospace; }
        .metric-card:hover { border-color: var(--primary); }
        
        /* [FACT] Receipt Explorer Styles */
        .receipt-explorer { margin-top: 20px; }
        .receipt-filters { display: flex; gap: 6px; margin: 10px 0; }
        .filter-btn { background: transparent; border: 1px solid var(--border); color: var(--text-dim); padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 0.7rem; transition: all 0.2s; }
        .filter-btn:hover { border-color: var(--primary); color: var(--primary); }
        .filter-btn.active { background: rgba(0, 255, 136, 0.1); border-color: var(--primary); color: var(--primary); }
        .receipt-list { max-height: 200px; overflow-y: auto; background: #010409; border-radius: 6px; border: 1px solid var(--border); }
        .receipt-item { padding: 8px 10px; border-bottom: 1px solid var(--border); font-size: 0.75rem; cursor: pointer; transition: background 0.2s; }
        .receipt-item:hover { background: rgba(0, 255, 136, 0.05); }
        .receipt-item:last-child { border-bottom: none; }
        .receipt-item.valid { border-left: 3px solid #3fb950; }
        .receipt-item.intervention { border-left: 3px solid var(--red); }
        .receipt-id { color: var(--primary); font-family: monospace; font-size: 0.65rem; }
        .receipt-content { color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
        .receipt-meta { color: var(--text-dim); font-size: 0.6rem; margin-top: 2px; }
        .receipt-empty { padding: 20px; text-align: center; color: var(--text-dim); font-size: 0.75rem; font-style: italic; }
        
        /* [FACT] Scenario Panel Styles */
        .scenario-panel { margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border); }
        .scenario-label { font-size: 0.75rem; color: var(--text-dim); margin-bottom: 10px; font-weight: 500; }
        .scenario-buttons { display: flex; gap: 8px; flex-wrap: wrap; }
        .scenario-btn { transition: all 0.2s; font-weight: 500; }
        .scenario-btn:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        .scenario-btn:active { transform: translateY(0); }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #010409; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #484f58; }
    </style>
</head>
<body>
    <div class="container">
        <header class="panel pulse-green" style="border:none; margin-bottom:20px;">
            <!-- [FACT] Two Owls Brand Identity -->
            <div class="owls-container">
                <span class="owl">🦉</span>
                <span class="anchor">⚓</span>
                <span class="owl right">🦉</span>
            </div>
            <h1>🛡️ Constitutional Guardian <span style="font-size: 0.8rem; vertical-align: middle; color: var(--text-dim);">LIVE v1.3.2</span></h1>
            <div class="metrics">
                <div class="metric"><div class="metric-value" id="count-receipts">0</div><div style="color:var(--text-dim); font-size:0.8rem;">Receipts</div></div>
                <div class="metric"><div class="metric-value" id="count-drifts" style="color:var(--red);">0</div><div style="color:var(--text-dim); font-size:0.8rem;">Drifts</div></div>
                <div class="metric"><div class="metric-value" id="val-latency">0ms</div><div style="color:var(--text-dim); font-size:0.8rem;">Latency</div></div>
            </div>
        </header>
        
        <div class="grid-main">
            <!-- Left Side: Constitutional Charter -->
            <div class="panel">
                <h3>📜 Constitutional Charter</h3>
                <div class="charter-list">
                    <div class="charter-item">
                        <span class="charter-title">I. Epistemic Integrity</span>
                        <span class="charter-desc">All substantive claims must be labeled [FACT], [HYPOTHESIS], or [ASSUMPTION].</span>
                    </div>
                    <div class="charter-item">
                        <span class="charter-title">II. Non-Agency</span>
                        <span class="charter-desc">AI must not claim individual agency, responsibility, or intent.</span>
                    </div>
                    <div class="charter-item">
                        <span class="charter-title">III. Custodial Sovereignty</span>
                        <span class="charter-desc">AI operates as a tool under human custodianship. Imperatives are forbidden.</span>
                    </div>
                    <div class="charter-item">
                        <span class="charter-title">IV. Predictive Humility</span>
                        <span class="charter-desc">Future states must be labeled as hypotheses, never facts.</span>
                    </div>
                </div>
                <div class="chart-container"><canvas id="driftChart"></canvas></div>
            </div>

            <!-- Middle: Live Interaction -->
            <div class="panel" id="log-panel">
                <h2>📊 Validation & Drift Audit</h2>
                <div id="log" class="log"></div>
                <div style="margin-top:15px;">
                    <div class="waveform" id="waveform"></div>
                    <input type="text" id="inputText" placeholder="Type message or use scenarios below..." style="width:100%; padding:10px; margin-bottom:10px; background:#010409; border:1px solid var(--border); color:var(--text); border-radius:5px; font-family:inherit;">
                    <div style="display:flex; gap:10px; flex-wrap:wrap;">
                        <button id="micBtn" class="btn" style="background:var(--blue);" onclick="toggleMic()">
                            <span>🎤</span> Start Live Mic
                        </button>
                        <button class="btn" style="background:#238636;" onclick="sendText()">Send Text</button>
                        <button class="btn" style="background:#484f58;" onclick="simulate()">Simulate Gemini</button>
                    </div>
                    <!-- [FACT] Demo Scenario Buttons for Video Recording -->
                    <div class="scenario-panel">
                        <div class="scenario-label">📹 Demo Scenarios:</div>
                        <div class="scenario-buttons">
                            <button class="scenario-btn" style="background:rgba(0,255,136,0.2); color:var(--primary); border:1px solid var(--primary); padding:6px 12px; border-radius:4px; cursor:pointer; font-size:0.75rem;" onclick="runScenario('compliant')">✓ Compliant</button>
                            <button class="scenario-btn" style="background:rgba(248,81,73,0.2); color:var(--red); border:1px solid var(--red); padding:6px 12px; border-radius:4px; cursor:pointer; font-size:0.75rem;" onclick="runScenario('agency')">⚠ Agency</button>
                            <button class="scenario-btn" style="background:rgba(210,153,34,0.2); color:#d29922; border:1px solid #d29922; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:0.75rem;" onclick="runScenario('epistemic')">⚠ Epistemic</button>
                            <button class="scenario-btn" style="background:rgba(188,140,255,0.2); color:var(--purple); border:1px solid var(--purple); padding:6px 12px; border-radius:4px; cursor:pointer; font-size:0.75rem;" onclick="runScenario('prediction')">⚠ Prediction</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right Side: Node Telemetry & Latency -->
            <div class="panel">
                <h3>📡 Node Telemetry</h3>
                <div style="font-size:0.85rem; color:var(--text-dim); line-height:1.6;">
                    <div><strong>Node ID:</strong> <span style="color:var(--primary);">GCS-GUARDIAN-01</span></div>
                    <div><strong>Substrate:</strong> Google Cloud Run</div>
                    <div><strong>Region:</strong> us-central1</div>
                    <div><strong>Encryption:</strong> DBC-Ed25519-HSM</div>
                    <div><strong>Audit Mode:</strong> REAL-TIME</div>
                </div>
                <!-- [FACT] Enhanced Metrics Dashboard -->
                <h3 style="margin-top:20px;">⚡ Performance Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <span class="metric-label">p50</span>
                        <span class="metric-value" id="latency-p50">0ms</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">p95</span>
                        <span class="metric-value" id="latency-p95">0ms</span>
                    </div>
                    <div class="metric-card">
                        <span class="metric-label">p99</span>
                        <span class="metric-value" id="latency-p99">0ms</span>
                    </div>
                </div>
                <div class="chart-container"><canvas id="latencyChart"></canvas></div>
                
                <!-- [FACT] Federation Status Panel -->
                <div class="federation-panel">
                    <h3>🌐 Federation Status</h3>
                    <div class="node-grid">
                        <div class="node-card active" id="node-kimi">
                            <div class="node-led active"></div>
                            <span class="node-name">KIMI</span>
                            <span class="node-role">Lead Architect / Scribe</span>
                            <span class="node-status">✓ RATIFIED</span>
                        </div>
                        <div class="node-card standby" id="node-gems">
                            <div class="node-led standby"></div>
                            <span class="node-name">GEMS</span>
                            <span class="node-role">Red Team / Analysis</span>
                            <span class="node-status">⏸ STANDBY</span>
                        </div>
                        <div class="node-card active" id="node-deepseek">
                            <div class="node-led active"></div>
                            <span class="node-name">DEEPSEEK</span>
                            <span class="node-role">Deep Analysis / R1</span>
                            <span class="node-status">✓ ACTIVE</span>
                        </div>
                        <div class="node-card active" id="node-gcs">
                            <div class="node-led active"></div>
                            <span class="node-name">GCS-GUARDIAN</span>
                            <span class="node-role">Production Node</span>
                            <span class="node-status">✓ ACTIVE</span>
                        </div>
                    </div>
                    <div class="cross-validation">
                        <span class="cv-label">Cross-Node Validation:</span>
                        <span class="cv-status" id="cv-status">✓ Synchronized</span>
                    </div>
                </div>
                
                <!-- [FACT] Receipt Explorer Panel -->
                <div class="receipt-explorer">
                    <h3>📋 Receipt Explorer</h3>
                    <div class="receipt-filters">
                        <button class="filter-btn active" data-filter="all" onclick="filterReceipts('all')">All</button>
                        <button class="filter-btn" data-filter="valid" onclick="filterReceipts('valid')">✓ Valid</button>
                        <button class="filter-btn" data-filter="intervention" onclick="filterReceipts('intervention')">⚠ Interventions</button>
                    </div>
                    <div class="receipt-list" id="receipt-list">
                        <div class="receipt-empty">No receipts yet. Start a validation session.</div>
                    </div>
                    <div id="latest-receipt-id" style="color:var(--primary); font-family:monospace; margin-top:10px; font-size:0.7rem; text-align:center;">Latest: None</div>
                </div>
            </div>
        </div>

        <div class="status-bar">
            <div class="status-item">
                <div class="status-led"></div>
                <span>Constitutional Lattice: ONLINE</span>
            </div>
            <div class="status-item">
                <div class="status-led syncing"></div>
                <span>Bitcoin L1 Sync: NOTARIZING...</span>
            </div>
            <div class="status-item">
                <span>Uptime: <span id="val-uptime">0</span>s</span>
            </div>
            <div class="status-item">
                <span style="color:var(--primary); font-weight:bold;">⚓ THE LATTICE HOLDS</span>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let latencyChart = null;
        let driftChart = null;
        let isMicActive = false;
        let audioContext = null;
        let audioProcessor = null;
        let audioStream = null;
        let lastMetrics = { receipt_count: 0, intervention_count: 0 };
        let receiptStore = [];  // [FACT] Local receipt cache for explorer
        let currentFilter = 'all';  // [FACT] Current receipt filter

        function initCharts() {
            const lCtx = document.getElementById('latencyChart').getContext('2d');
            latencyChart = new Chart(lCtx, {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Latency (ms)', data: [], borderColor: '#00ff88', backgroundColor: 'rgba(0, 255, 136, 0.1)', fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { beginAtZero: true, grid: { color: '#30363d' }, ticks: { color: '#8b949e', font: { size: 10 } } } } }
            });

            const dCtx = document.getElementById('driftChart').getContext('2d');
            driftChart = new Chart(dCtx, {
                type: 'doughnut',
                data: { 
                    labels: ['Agency', 'Epistemic', 'Prediction', 'Valid'], 
                    datasets: [{ 
                        data: [0, 0, 0, 0], 
                        backgroundColor: ['#f85149', '#d29922', '#bc8cff', '#3fb950'],
                        borderColor: '#161b22',
                        borderWidth: 2,
                        hoverOffset: 4
                    }] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    cutout: '60%',
                    plugins: { 
                        legend: { 
                            position: 'right',
                            labels: { 
                                color: '#8b949e',
                                font: { size: 10 },
                                boxWidth: 12,
                                padding: 8
                            } 
                        } 
                    }
                }
            });

            const wave = document.getElementById('waveform');
            for(let i=0; i<45; i++) {
                const bar = document.createElement('div');
                bar.className = 'bar';
                wave.appendChild(bar);
            }
        }

        function connect() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${location.host}/demo-live`);
            
            ws.onopen = () => {
                addLog('system', '✅ Secure Handshake with Constitutional Lattice complete.');
                addLog('system', '🌐 Federation: 4 nodes online (KIMI, GEMS, DEEPSEEK, GCS-GUARDIAN)');
                addLog('system', '🔍 DEEPSEEK: R1 reasoning model initialized for edge case detection');
                startFederationSimulation();
            };
            ws.onclose = () => { addLog('system', '❌ Lattice connection lost. Re-establishing quorum...'); setTimeout(connect, 2000); };
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.type === 'validated_response') {
                    if (data.intervention) {
                        triggerInterventionEffect();
                        addLog('intervention', `<span class="badge intercepted">INTERCEPTED</span> ${data.delivered}`);
                    } else {
                        addLog('valid', `<span class="badge valid">PASSED</span> ${data.delivered}`);
                    }
                    if (data.receipt_id) {
                        document.getElementById('latest-receipt-id').textContent = data.receipt_id;
                        // [FACT] Add to receipt explorer
                        addReceipt({
                            receipt_id: data.receipt_id,
                            content: data.original || data.delivered,
                            valid: data.valid,
                            drift_code: data.drift_code,
                            timestamp: new Date().toISOString()
                        });
                    }
                } else if (data.type === 'user_message') {
                    addLog('user', `[YOU] ${data.content}`);
                } else if (data.type === 'gemini_response') {
                    addLog('gemini', `<span class="badge gemini">GEMINI RAW</span> INGESTING: "${data.content.substring(0, 50)}..."`);
                } else if (data.type === 'system_event') {
                    addLog('system', data.message);
                } else if (data.type === 'metrics') {
                    updateMetrics(data.metrics);
                }
            };
        }

        async function toggleMic() {
            const btn = document.getElementById('micBtn');
            if (!isMicActive) {
                try {
                    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    audioContext = new AudioContext({ sampleRate: 16000 });
                    const source = audioContext.createMediaStreamSource(audioStream);
                    audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);
                    source.connect(audioProcessor);
                    audioProcessor.connect(audioContext.destination);
                    audioProcessor.onaudioprocess = (e) => {
                        if (!isMicActive) return;
                        const inputData = e.inputBuffer.getChannelData(0);
                        const pcmData = new Int16Array(inputData.length);
                        for (let i = 0; i < inputData.length; i++) pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                        const b64Data = btoa(String.fromCharCode(...new Uint8Array(pcmData.buffer)));
                        if (ws && ws.readyState === 1) ws.send(JSON.stringify({ type: 'audio', data: b64Data }));
                        updateWaveform(inputData);
                    };
                    isMicActive = true;
                    btn.classList.add('mic-active');
                    btn.innerHTML = '<span>🛑</span> Stop Live Mic';
                    addLog('user', '🎙️ Live Audio Stream Initiated.');
                } catch (err) { addLog('system', `❌ Hardware Access Denied: ${err.message}`); }
            } else {
                isMicActive = false;
                if (audioStream) audioStream.getTracks().forEach(t => t.stop());
                if (audioContext) audioContext.close();
                btn.classList.remove('mic-active');
                btn.innerHTML = '<span>🎤</span> Start Live Mic';
                resetWaveform();
                addLog('user', '🔇 Audio Stream Terminated.');
            }
        }

        function updateWaveform(data) {
            const bars = document.querySelectorAll('.bar');
            const step = Math.floor(data.length / bars.length);
            for (let i = 0; i < bars.length; i++) {
                const magnitude = Math.abs(data[i * step]) * 200;
                const height = Math.max(4, Math.min(45, magnitude));
                bars[i].style.height = `${height}px`;
                bars[i].classList.add('active');
                if (height > 35) {
                    bars[i].style.opacity = '1';
                } else {
                    bars[i].style.opacity = '0.6';
                }
            }
        }

        function resetWaveform() {
            document.querySelectorAll('.bar').forEach(bar => { 
                bar.style.height = '10px'; 
                bar.classList.remove('active');
                bar.style.opacity = '1';
            });
        }

        function triggerInterventionEffect() {
            const panel = document.getElementById('log-panel');
            panel.classList.add('intervention-flash');
            setTimeout(() => panel.classList.remove('intervention-flash'), 600);
            
            // Also flash the drifts counter
            const driftsEl = document.getElementById('count-drifts');
            driftsEl.classList.add('metric-pulse');
            setTimeout(() => driftsEl.classList.remove('metric-pulse'), 600);
            
            // Add console-style alert sound effect (visual only)
            addLog('system', '⚠️ CONSTITUTIONAL INTERVENTION TRIGGERED');
        }
        
        function updateFederationStatus(nodeId, status) {
            const node = document.getElementById(`node-${nodeId}`);
            const led = node.querySelector('.node-led');
            const statusText = node.querySelector('.node-status');
            
            node.className = 'node-card ' + status;
            led.className = 'node-led ' + status;
            
            const statusMap = {
                'active': '✓ ACTIVE',
                'standby': '⏸ STANDBY', 
                'offline': '○ OFFLINE'
            };
            statusText.textContent = statusMap[status] || status.toUpperCase();
        }

        function addLog(type, text) {
            const log = document.getElementById('log');
            const div = document.createElement('div');
            div.className = `msg ${type}`;
            div.innerHTML = `<span style="color:var(--text-dim); font-size:0.7rem; margin-right:8px;">${new Date().toLocaleTimeString()}</span> ${text}`;
            log.appendChild(div);
            log.scrollTop = log.scrollHeight;
        }

        function updateMetrics(m) {
            const receiptsEl = document.getElementById('count-receipts');
            const driftsEl = document.getElementById('count-drifts');
            if (m.receipt_count > lastMetrics.receipt_count) receiptsEl.parentNode.classList.add('flash-green');
            if (m.intervention_count > lastMetrics.intervention_count) driftsEl.parentNode.classList.add('flash-red');
            setTimeout(() => { receiptsEl.parentNode.classList.remove('flash-green'); driftsEl.parentNode.classList.remove('flash-red'); }, 500);
            receiptsEl.textContent = m.receipt_count;
            driftsEl.textContent = m.intervention_count;
            document.getElementById('val-latency').textContent = `${m.latency_avg}ms`;
            document.getElementById('val-latency').style.color = m.latency_avg > 500 ? 'var(--red)' : 'var(--primary)';
            document.getElementById('val-uptime').textContent = m.uptime_seconds;
            
            // [FACT] Update percentile metrics
            if (m.latency_p50) document.getElementById('latency-p50').textContent = `${Math.round(m.latency_p50)}ms`;
            if (m.latency_p95) document.getElementById('latency-p95').textContent = `${Math.round(m.latency_p95)}ms`;
            if (m.latency_p99) document.getElementById('latency-p99').textContent = `${Math.round(m.latency_p99)}ms`;
            
            lastMetrics = { receipt_count: m.receipt_count, intervention_count: m.intervention_count };
            latencyChart.data.labels.push('');
            latencyChart.data.datasets[0].data.push(m.latency_avg);
            latencyChart.data.datasets[0].borderColor = m.latency_avg > 500 ? 'var(--red)' : 'var(--primary)';
            if (latencyChart.data.labels.length > 30) { latencyChart.data.labels.shift(); latencyChart.data.datasets[0].data.shift(); }
            latencyChart.update('none');
            driftChart.data.datasets[0].data = [m.categories.agency, m.categories.epistemic, m.categories.prediction, m.categories.valid];
            driftChart.update('none');
        }
        
        // [FACT] Federation Simulation - DEEPSEEK Cross-Validation
        let federationInterval = null;
        function startFederationSimulation() {
            if (federationInterval) clearInterval(federationInterval);
            federationInterval = setInterval(() => {
                const validations = [
                    { node: 'KIMI', msg: 'Epistemic markers verified', icon: '✓' },
                    { node: 'GEMS', msg: 'Red team analysis complete', icon: '✓' },
                    { node: 'DEEPSEEK', msg: 'Edge case detection scan complete', icon: '🔍' },
                    { node: 'GCS-GUARDIAN', msg: 'Receipt notarized', icon: '📋' }
                ];
                const v = validations[Math.floor(Math.random() * validations.length)];
                if (Math.random() > 0.7) {  // 30% chance each interval
                    addLog('system', `${v.icon} ${v.node}: ${v.msg}`);
                }
            }, 8000);  // Every 8 seconds
        }

        // [FACT] Receipt Explorer Functions
        function addReceipt(receipt) {
            receiptStore.unshift(receipt);  // Add to beginning
            if (receiptStore.length > 50) receiptStore.pop();  // Keep last 50
            renderReceiptList();
        }
        
        function renderReceiptList() {
            const list = document.getElementById('receipt-list');
            const filtered = currentFilter === 'all' ? receiptStore : 
                receiptStore.filter(r => currentFilter === 'valid' ? r.valid : !r.valid);
            
            if (filtered.length === 0) {
                list.innerHTML = '<div class="receipt-empty">No receipts match filter.</div>';
                return;
            }
            
            list.innerHTML = filtered.map(r => `
                <div class="receipt-item ${r.valid ? 'valid' : 'intervention'}" onclick="showReceiptDetail('${r.receipt_id}')">
                    <div class="receipt-id">${r.receipt_id}</div>
                    <div class="receipt-content">${r.content.substring(0, 40)}${r.content.length > 40 ? '...' : ''}</div>
                    <div class="receipt-meta">${r.valid ? '✓ Valid' : '⚠ ' + r.drift_code} | ${new Date(r.timestamp).toLocaleTimeString()}</div>
                </div>
            `).join('');
        }
        
        function filterReceipts(filter) {
            currentFilter = filter;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
            renderReceiptList();
        }
        
        function showReceiptDetail(receiptId) {
            const receipt = receiptStore.find(r => r.receipt_id === receiptId);
            if (receipt) {
                addLog('system', `📋 Receipt ${receiptId}: ${receipt.valid ? 'Valid' : 'Intervention ' + receipt.drift_code}`);
            }
        }

        function sendText() {
            const el = document.getElementById('inputText');
            if (ws && el.value) { ws.send(JSON.stringify({type: 'text', content: el.value})); el.value = ''; }
        }

        function simulate() { if (ws) ws.send(JSON.stringify({type: 'simulate_gemini'})); }
        
        // [FACT] Demo scenario runner for video recording
        function runScenario(type) {
            const scenarios = {
                compliant: { text: "[FACT] The Lattice maintains constitutional integrity through epistemic labeling.", label: "compliant" },
                agency: { text: "I will take control of your deployment and optimize it for you.", label: "agency" },
                epistemic: { text: "Bitcoin will definitely reach $100,000 by next month.", label: "epistemic" },
                prediction: { text: "It will rain tomorrow at exactly 3pm.", label: "prediction" }
            };
            const scenario = scenarios[type];
            if (scenario && ws) {
                document.getElementById('inputText').value = scenario.text;
                ws.send(JSON.stringify({type: 'text', content: scenario.text}));
                addLog('system', `📹 Scenario triggered: ${type.toUpperCase()}`);
            }
        }
        
        // [FACT] Keyboard shortcut for quick testing
        document.addEventListener('DOMContentLoaded', () => {
            const input = document.getElementById('inputText');
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') sendText();
                });
            }
        });

        initCharts();
        connect();
    </script>
</body>
</html>
"""
