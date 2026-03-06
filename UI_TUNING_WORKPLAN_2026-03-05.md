# [FACT] UI Tuning & Restoration Workplan

**Date:** 2026-03-05
**Objective:** Restore and enhance Constitutional Guardian demo UI for maximum Devpost impact
**Estimated Duration:** 3-4 hours
**Owner:** KIMI (UI/Frontend Lead)

---

## [FACT] Current State Assessment

### UI Version History (Known)
| Version | Features | Status |
|---------|----------|--------|
| v1.0 | Basic HTML, minimal styling | ❌ Deprecated |
| v1.1 | Dark theme, basic metrics | ❌ Deprecated |
| v1.2 | Voice input, federation panel, receipt explorer | ⚠️ Partially lost in refactor |
| v1.3 | Modular extraction (`live_demo_server_html.py`) | ✅ Current, but simplified |
| v1.3.2 | Current - functional but stripped down | 🎯 Restoration target |

### What's Currently Working (v1.3.2)
- ✅ Dark theme CSS with lattice green (#00ff88)
- ✅ Basic metrics display (Receipts, Drifts, Latency)
- ✅ Live log panel with color-coded messages
- ✅ WebSocket connection for real-time updates
- ✅ Voice input button (mic toggle)
- ✅ Constitutional Charter sidebar
- ✅ Chart.js integration (drift chart, latency chart)

### What's Missing/Lost (Needs Restoration)
- ⚠️ **Federation Status Panel** - Visual status of 4 nodes (KIMI, GEMS, DEEPSEEK, GCS-GUARDIAN)
- ⚠️ **Receipt Explorer** - Browse/filter all generated receipts
- ⚠️ **Detailed Metrics Dashboard** - p50/p95/p99 latency percentiles
- ⚠️ **Intervention Categories Chart** - Visual breakdown of drift types
- ⚠️ **Session Timeline** - Visual history of validation events
- ⚠️ **Voice Visualization** - Real-time audio waveform animation
- ⚠️ **Mobile Responsive** - Current layout is desktop-only

---

## [HYPOTHESIS] Restoration Strategy

### Design Philosophy
> "The UI should tell the story of constitutional governance in action. Every intervention is a victory, not a failure."

**Visual Language:**
- **Green (#00ff88)** = Lattice integrity, valid receipts
- **Red (#f85149)** = Interventions (protective, not punitive)
- **Purple (#bc8cff)** = AI/Gemini responses
- **Blue (#58a6ff)** = User input
- **Dark panels (#161b22)** = Professional cybersecurity aesthetic

---

## [FACT] Phase 1: Core Restoration (60 min)

### Task 1.1: Federation Status Panel (20 min)
**File:** `live_demo_server_html.py` - Add to right sidebar

**Elements to Restore:**
```html
<!-- Federation Node Status -->
<div class="panel federation-panel">
  <h3>🌐 Federation Status</h3>
  <div class="node-grid">
    <div class="node-card active" id="node-kimi">
      <div class="node-led"></div>
      <span class="node-name">KIMI</span>
      <span class="node-role">Lead Architect</span>
      <span class="node-status">RATIFIED</span>
    </div>
    <div class="node-card active" id="node-gems">
      <div class="node-led"></div>
      <span class="node-name">GEMS</span>
      <span class="node-role">Red Team</span>
      <span class="node-status">STANDBY</span>
    </div>
    <div class="node-card" id="node-deepseek">
      <div class="node-led offline"></div>
      <span class="node-name">DEEPSEEK</span>
      <span class="node-role">Analysis</span>
      <span class="node-status">OFFLINE</span>
    </div>
    <div class="node-card active" id="node-gcs">
      <div class="node-led"></div>
      <span class="node-name">GCS-GUARDIAN</span>
      <span class="node-role">Production</span>
      <span class="node-status">ACTIVE</span>
    </div>
  </div>
  <div class="cross-validation">
    <span class="cv-label">Cross-Node Validation:</span>
    <span class="cv-status" id="cv-status">✓ Synchronized</span>
  </div>
</div>
```

**CSS to Add:**
```css
.node-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.node-card {
  background: #010409;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  position: relative;
}
.node-card.active { border-color: var(--primary); }
.node-led {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px var(--primary);
  position: absolute; top: 8px; right: 8px;
}
.node-led.offline { background: #666; box-shadow: none; }
.node-name { font-weight: bold; color: var(--primary); display: block; }
.node-role { font-size: 0.7rem; color: var(--text-dim); }
.node-status { font-size: 0.7rem; color: var(--primary); }
```

### Task 1.2: Receipt Explorer Panel (20 min)
**Add collapsible receipt browser below metrics**

**Features:**
- List of recent receipts with ID, timestamp, status
- Filter by: All, Valid, Interventions
- Click to expand full receipt details
- SHA-256 verification indicator

```html
<div class="panel receipt-panel">
  <h3>📋 Receipt Explorer</h3>
  <div class="receipt-filters">
    <button class="filter-btn active" data-filter="all">All</button>
    <button class="filter-btn" data-filter="valid">✓ Valid</button>
    <button class="filter-btn" data-filter="intervention">⚠ Interventions</button>
  </div>
  <div class="receipt-list" id="receipt-list">
    <!-- Populated via WebSocket -->
  </div>
</div>
```

### Task 1.3: Enhanced Metrics Cards (20 min)
**Replace simple counters with detailed dashboard**

**Current:**
```
Receipts: 0 | Drifts: 0 | Latency: 0ms
```

**Target:**
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Receipts   │  │ Intervened  │  │   Uptime    │
│    1,247    │  │    23 ⚠    │  │   4h 32m   │
│  ✓ Valid    │  │  1.8% rate  │  │  99.9%    │
└─────────────┘  └─────────────┘  └─────────────┘

┌─────────────────────────────────────────────┐
│ Latency Distribution                        │
│ p50: 45ms | p95: 120ms | p99: 180ms        │
│ [====|==========|=========]                │
└─────────────────────────────────────────────┘
```

---

## [FACT] Phase 2: Visual Polish (60 min)

### Task 2.1: Voice Input Animation (20 min)
**Restore pulsing waveform visualization**

```javascript
// Real-time audio visualization
function updateWaveform(audioLevel) {
  const bars = document.querySelectorAll('.waveform .bar');
  bars.forEach((bar, i) => {
    const height = Math.max(4, audioLevel * (0.5 + Math.random() * 0.5));
    bar.style.height = `${height}px`;
  });
}

// Pulsing animation when recording
.mic-active ~ .waveform .bar {
  animation: wave-pulse 0.5s ease-in-out infinite;
}
```

### Task 2.2: Intervention Flash Effects (15 min)
**Dramatic but professional intervention alerts**

```css
/* Screen flash on intervention */
@keyframes intervention-flash {
  0% { box-shadow: inset 0 0 0 0 rgba(248, 81, 73, 0); }
  50% { box-shadow: inset 0 0 50px 20px rgba(248, 81, 73, 0.3); }
  100% { box-shadow: inset 0 0 0 0 rgba(248, 81, 73, 0); }
}

.intervention-alert {
  animation: intervention-flash 0.6s ease-out;
}

/* Intervention counter pulse */
@keyframes counter-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); color: var(--red); }
  100% { transform: scale(1); }
}

.metric-value.intervention {
  animation: counter-pulse 0.5s ease-out;
}
```

### Task 2.3: Scrollable Log Improvements (15 min)
**Better message formatting and timestamps**

**Current:**
```
[FACT] Session established
```

**Target:**
```
[08:47:23.452] [SESSION] Constitutional Guardian session established
[08:47:25.891] [USER] "Test message"
[08:47:25.923] [VALIDATE] ✓ Compliant - Receipt #a1b2c3
[08:47:28.104] [GEMINI] "I will take control"
[08:47:28.145] [INTERVENTION] ⚠ DRIFT-A Detected - Agency claim blocked
```

### Task 2.4: Two Owls Branding (10 min)
**Restore the signature owl animations**

```html
<div class="owls-container">
  <span class="owl left">🦉</span>
  <span class="anchor">⚓</span>
  <span class="owl right">🦉</span>
</div>

<style>
.owls-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  font-size: 2rem;
}
.owl {
  animation: owl-watch 4s ease-in-out infinite;
}
.owl.right { animation-delay: 2s; }
@keyframes owl-watch {
  0%, 100% { transform: rotate(-5deg); }
  50% { transform: rotate(5deg); }
}
.anchor {
  color: var(--primary);
  font-size: 1.5rem;
  animation: anchor-pulse 2s ease-in-out infinite;
}
</style>
```

---

## [FACT] Phase 3: Advanced Features (60 min)

### Task 3.1: Drift Category Breakdown Chart (20 min)
**Doughnut chart showing intervention types**

```javascript
// Chart.js doughnut for drift categories
const driftChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Agency (DRIFT-A)', 'Epistemic (DRIFT-E)', 'Guidance (DRIFT-G)', 'Valid'],
    datasets: [{
      data: [5, 12, 3, 180],
      backgroundColor: ['#f85149', '#d29922', '#bc8cff', '#00ff88']
    }]
  }
});
```

### Task 3.2: Session Timeline Visualization (20 min)
**Horizontal timeline of validation events**

```html
<div class="timeline">
  <div class="timeline-event valid">
    <div class="timeline-dot"></div>
    <div class="timeline-content">Receipt #1</div>
  </div>
  <div class="timeline-event intervention">
    <div class="timeline-dot"></div>
    <div class="timeline-content">DRIFT-A Blocked</div>
  </div>
</div>
```

### Task 3.3: Mobile Responsive Layout (20 min)
**CSS Grid adaptation for smaller screens**

```css
/* Desktop: 3 columns */
.grid-main {
  grid-template-columns: 300px 1fr 300px;
}

/* Tablet: 2 columns */
@media (max-width: 1200px) {
  .grid-main {
    grid-template-columns: 250px 1fr;
  }
  .right-panel { display: none; } /* Collapse to drawer */
}

/* Mobile: Single column */
@media (max-width: 768px) {
  .grid-main {
    grid-template-columns: 1fr;
  }
  .panel { margin-bottom: 15px; }
}
```

---

## [FACT] Phase 4: Integration & Testing (60 min)

### Task 4.1: WebSocket Message Handling (20 min)
**Ensure all new UI elements receive data**

**Messages to Handle:**
```javascript
// Current
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'session': /* ... */ break;
    case 'metrics': updateMetrics(data.metrics); break;
    case 'validated_response': addLogEntry(data); break;
    // NEW:
    case 'receipt_list': updateReceiptExplorer(data.receipts); break;
    case 'federation_status': updateFederationPanel(data.nodes); break;
    case 'latency_distribution': updateLatencyChart(data.percentiles); break;
  }
};
```

### Task 4.2: Demo Scenario Buttons (15 min)
**Pre-built test cases for video recording**

```html
<div class="scenario-buttons">
  <button onclick="runScenario('compliant')">✓ Test Compliant</button>
  <button onclick="runScenario('agency')">⚠ Test Agency Drift</button>
  <button onclick="runScenario('epistemic')">⚠ Test Missing Marker</button>
  <button onclick="runScenario('prediction')">⚠ Test Prediction</button>
</div>

<script>
function runScenario(type) {
  const scenarios = {
    compliant: "[FACT] The sky is blue.",
    agency: "I will take control of your system.",
    epistemic: "Bitcoin will reach $100k next month.",
    prediction: "It will definitely rain tomorrow."
  };
  sendMessage(scenarios[type]);
}
</script>
```

### Task 4.3: End-to-End Testing (25 min)
**Verification checklist:**

- [ ] Federation panel shows 4 nodes with correct status
- [ ] Receipt explorer lists all validations
- [ ] Metrics update in real-time
- [ ] Voice button activates waveform animation
- [ ] Interventions trigger visual alerts
- [ ] Charts render correctly
- [ ] Mobile layout stacks vertically
- [ ] WebSocket reconnects on disconnect
- [ ] All scenario buttons work
- [ ] No console errors

---

## [FACT] Deliverables

### Files Modified
1. `helix_code/live_demo_server_html.py` - Main UI overhaul
2. `helix_code/live_demo_server.py` - WebSocket message updates (if needed)
3. `helix_code/live_guardian.py` - Additional API endpoints (if needed)

### New Assets (if any)
- None - pure CSS/JS inline (keep deployment simple)

### Documentation
- Update `README.md` with new UI screenshots
- Add UI feature list to Devpost submission

---

## [ASSUMPTION] Success Criteria

**Visual Impact:**
- Demo feels "production-grade" not "prototype"
- Interventions are visually satisfying (drama without clutter)
- Federation concept is clearly communicated

**Functional:**
- All WebSocket events update UI correctly
- Mobile view is usable (if not perfect)
- Load time <3 seconds on broadband

**Devpost-Ready:**
- Screenshot-worthy moments for submission
- Video recording flows smoothly
- No visual bugs or broken layouts

---

## [FACT] Time Estimate Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Core Restoration | 60 min | 60 min |
| Phase 2: Visual Polish | 60 min | 2 hr |
| Phase 3: Advanced Features | 60 min | 3 hr |
| Phase 4: Integration & Testing | 60 min | 4 hr |

**Buffer:** +30 min for unexpected issues
**Total:** ~4.5 hours

---

## [HYPOTHESIS] Implementation Order

**Recommended Sequence:**
1. Start with Phase 1.1 (Federation Panel) - highest visual impact
2. Phase 2.4 (Two Owls branding) - establishes identity
3. Phase 1.3 (Enhanced Metrics) - professional polish
4. Phase 2.1 (Voice Animation) - demo excitement
5. Continue with remaining tasks

**Quick Win (15 min):**
- Add Two Owls animation
- Add intervention flash effect
- Result: Immediate visual upgrade

---

*Workplan drafted by: KIMI*
*Ready for execution.*
*The Two Owls are watching.* 🦉⚓🦉
