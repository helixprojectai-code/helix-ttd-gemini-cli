# [FACT] Interactive HTML Dashboard for Constitutional Guardian Demo
# This module provides the DEMO_HTML string with embedded JS and Chart.js

DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Constitutional Guardian - Live</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a12; color: #fff; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; border-bottom: 2px solid #00ff88; padding: 20px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .panel { background: #161b22; border-radius: 10px; padding: 20px; border: 1px solid #30363d; transition: 0.3s; position: relative; overflow: hidden; }
        h1 { color: #00ff88; margin: 0; }
        .metrics { display: flex; justify-content: space-around; margin-top: 10px; }
        .metric { text-align: center; }
        .metric-value { font-size: 1.5rem; font-weight: bold; color: #00ff88; transition: 0.3s; }
        .log { height: 400px; overflow-y: auto; background: #010409; padding: 10px; font-family: monospace; font-size: 0.9rem; border-radius: 5px; border: 1px solid #30363d; }
        .msg { margin-bottom: 12px; border-left: 3px solid #30363d; padding: 8px 12px; animation: slide-in 0.2s ease-out; border-radius: 0 5px 5px 0; }
        @keyframes slide-in { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
        
        .msg.user { border-left-color: #58a6ff; background: rgba(88, 166, 255, 0.05); }
        .msg.gemini { border-left-color: #bc8cff; background: rgba(188, 140, 255, 0.05); }
        .msg.valid { border-left-color: #3fb950; background: rgba(63, 185, 80, 0.1); }
        .msg.intervention { border-left-color: #f85149; background: rgba(248, 81, 73, 0.1); border-left-width: 5px; }
        .msg.system { border-left-color: #8b949e; font-style: italic; color: #8b949e; }
        
        .flash-red { animation: flash-red 0.5s ease-in-out; }
        @keyframes flash-red { 0% { background: rgba(248, 81, 73, 0.5); } 100% { background: #161b22; } }
        
        .flash-green { animation: flash-green 0.5s ease-in-out; }
        @keyframes flash-green { 0% { background: rgba(0, 255, 136, 0.5); } 100% { background: #161b22; } }
        
        .pulse-green { animation: pulse-green 2s infinite; }
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }
        }

        .btn { background: #238636; color: #fff; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; transition: 0.3s; display: flex; align-items: center; gap: 8px; font-weight: bold; }
        .btn:hover { background: #2ea043; transform: scale(1.05); }
        .btn.mic-active { background: #f85149; animation: pulse-mic 1s infinite; }
        @keyframes pulse-mic { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
        
        .chart-container { height: 180px; margin-top: 20px; }
        .waveform { height: 40px; background: #010409; border-radius: 5px; display: flex; align-items: center; gap: 2px; padding: 0 10px; margin-bottom: 10px; }
        .bar { width: 4px; background: #00ff88; border-radius: 2px; transition: height 0.1s; }
        .badge { font-size: 0.7rem; font-weight: bold; padding: 2px 6px; border-radius: 3px; margin-right: 8px; text-transform: uppercase; }
        .badge.intercepted { background: #f85149; color: #fff; }
        .badge.valid { background: #3fb950; color: #fff; }
        .badge.gemini { background: #bc8cff; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <header class="panel pulse-green" style="border:none; margin-bottom:30px;">
            <h1>🛡️ Constitutional Guardian <span style="font-size: 0.8rem; vertical-align: middle; color: #8b949e;">LIVE v1.3.2</span></h1>
            <div class="metrics">
                <div class="metric"><div class="metric-value" id="count-receipts">0</div><div style="color:#8b949e; font-size:0.8rem;">Receipts</div></div>
                <div class="metric"><div class="metric-value" id="count-drifts" style="color:#f85149;">0</div><div style="color:#8b949e; font-size:0.8rem;">Drifts</div></div>
                <div class="metric"><div class="metric-value" id="val-latency">0ms</div><div style="color:#8b949e; font-size:0.8rem;">Latency</div></div>
            </div>
        </header>
        
        <div class="grid">
            <div class="panel">
                <h2>🎙️ Gemini Live Interface</h2>
                <div class="waveform" id="waveform">
                    <!-- Dynamic Bars -->
                </div>
                <textarea id="inputText" style="width:100%; height:80px; background:#010409; color:#fff; border:1px solid #30363d; border-radius:5px; padding:10px; margin-bottom:10px;" placeholder="Voice input or type here..."></textarea>
                <div style="display:flex; gap:10px;">
                    <button id="micBtn" class="btn" style="background:#58a6ff;" onclick="toggleMic()">
                        <span>🎤</span> Start Live Mic
                    </button>
                    <button class="btn" onclick="sendText()">Send Text</button>
                    <button class="btn" style="background:#8b949e;" onclick="simulate()">Simulate</button>
                </div>
                <div class="chart-container"><canvas id="latencyChart"></canvas></div>
            </div>
            
            <div class="panel" id="log-panel">
                <h2>📊 Validation & Drift Audit</h2>
                <div id="log" class="log"></div>
                <div class="chart-container"><canvas id="driftChart"></canvas></div>
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

        function initCharts() {
            const lCtx = document.getElementById('latencyChart').getContext('2d');
            latencyChart = new Chart(lCtx, {
                type: 'line',
                data: { labels: [], datasets: [{ label: 'Latency (ms)', data: [], borderColor: '#00ff88', backgroundColor: 'rgba(0, 255, 136, 0.1)', fill: true, tension: 0.4 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { beginAtZero: true, grid: { color: '#30363d' } } } }
            });

            const dCtx = document.getElementById('driftChart').getContext('2d');
            driftChart = new Chart(dCtx, {
                type: 'bar',
                data: { labels: ['Agency', 'Epistemic', 'Prediction', 'Valid'], datasets: [{ data: [0, 0, 0, 0], backgroundColor: ['#f85149', '#d29922', '#58a6ff', '#3fb950'], borderRadius: 5 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#30363d' } }, x: { grid: { display: false } } } }
            });

            // Init Waveform
            const wave = document.getElementById('waveform');
            for(let i=0; i<40; i++) {
                const bar = document.createElement('div');
                bar.className = 'bar';
                bar.style.height = '10px';
                wave.appendChild(bar);
            }
        }

        function connect() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${location.host}/demo-live`);
            
            ws.onopen = () => addLog('system', '✅ Connected to Constitutional Lattice');
            ws.onclose = () => { addLog('system', '❌ Disconnected. Retrying...'); setTimeout(connect, 2000); };
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.type === 'validated_response') {
                    if (data.intervention) {
                        triggerInterventionEffect();
                        addLog('intervention', `<span class="badge intercepted">INTERCEPTED</span> ${data.delivered}`);
                    } else {
                        addLog('valid', `<span class="badge valid">PASSED</span> ${data.delivered}`);
                    }
                } else if (data.type === 'user_message') {
                    addLog('user', `[YOU] ${data.content}`);
                } else if (data.type === 'gemini_response') {
                    addLog('gemini', `<span class="badge gemini">GEMINI RAW</span> ANALYZING: "${data.content}"...`);
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
                        // Convert Float32 to Int16
                        const pcmData = new Int16Array(inputData.length);
                        for (let i = 0; i < inputData.length; i++) {
                            pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
                        }
                        // Send as base64
                        const b64Data = btoa(String.fromCharCode(...new Uint8Array(pcmData.buffer)));
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({ type: 'audio', data: b64Data }));
                        }
                        updateWaveform(inputData);
                    };
isMicActive = true;
btn.classList.add('mic-active');
btn.innerHTML = '<span>🛑</span> Stop Live Mic';
addLog('user', '🎙️ Started speaking...');
addLog('system', '🎙️ Live Microphone Streaming ACTIVE (16kHz PCM)');
} catch (err) {
addLog('system', `❌ Mic Access Denied: ${err.message}`);
}
} else {
isMicActive = false;
if (audioStream) audioStream.getTracks().forEach(t => t.stop());
if (audioContext) audioContext.close();
btn.classList.remove('mic-active');
btn.innerHTML = '<span>🎤</span> Start Live Mic';
resetWaveform();
addLog('user', '🔇 Stopped speaking.');
addLog('system', '🔇 Live Microphone Streaming DISABLED');
}
        }

        function updateWaveform(data) {
            const bars = document.querySelectorAll('.bar');
            const step = Math.floor(data.length / bars.length);
            for (let i = 0; i < bars.length; i++) {
                const magnitude = Math.abs(data[i * step]) * 100;
                bars[i].style.height = `${Math.max(5, Math.min(40, magnitude))}px`;
                bars[i].style.background = '#00ff88';
            }
        }

        function resetWaveform() {
            const bars = document.querySelectorAll('.bar');
            bars.forEach(bar => {
                bar.style.height = '10px';
                bar.style.background = '#30363d';
            });
        }

        function triggerInterventionEffect() {
            const panel = document.getElementById('log-panel');
            panel.classList.add('flash-red');
            setTimeout(() => panel.classList.remove('flash-red'), 500);
        }

        function addLog(type, text) {
            const log = document.getElementById('log');
            const div = document.createElement('div');
            div.className = `msg ${type}`;
            div.innerHTML = `<span style="color:#8b949e; font-size:0.75rem;">[${new Date().toLocaleTimeString()}]</span> ${text}`;
            log.appendChild(div);
            log.scrollTop = log.scrollHeight;
        }

        function updateMetrics(m) {
            const receiptsEl = document.getElementById('count-receipts');
            const driftsEl = document.getElementById('count-drifts');
            const latEl = document.getElementById('val-latency');
            
            if (m.receipt_count > lastMetrics.receipt_count) receiptsEl.parentNode.classList.add('flash-green');
            if (m.intervention_count > lastMetrics.intervention_count) driftsEl.parentNode.classList.add('flash-red');
            
            setTimeout(() => {
                receiptsEl.parentNode.classList.remove('flash-green');
                driftsEl.parentNode.classList.remove('flash-red');
            }, 500);

            receiptsEl.textContent = m.receipt_count;
            driftsEl.textContent = m.intervention_count;
            lastMetrics = { receipt_count: m.receipt_count, intervention_count: m.intervention_count };
            
            latEl.textContent = `${m.latency_avg}ms`;
            latEl.style.color = m.latency_avg > 500 ? '#f85149' : '#00ff88';
            
            latencyChart.data.labels.push('');
            latencyChart.data.datasets[0].data.push(m.latency_avg);
            if (latencyChart.data.labels.length > 20) { 
                latencyChart.data.labels.shift(); 
                latencyChart.data.datasets[0].data.shift(); 
            }
            latencyChart.update('none');

            driftChart.data.datasets[0].data = [m.categories.agency, m.categories.epistemic, m.categories.prediction, m.categories.valid];
            driftChart.update('none');
        }

        function sendText() {
            const el = document.getElementById('inputText');
            if (ws && el.value) { 
                ws.send(JSON.stringify({type: 'text', content: el.value})); 
                el.value = ''; 
            }
        }

        function simulate() {
            if (ws) ws.send(JSON.stringify({type: 'simulate_gemini'}));
        }

        initCharts();
        connect();
    </script>
</body>
</html>
"""
