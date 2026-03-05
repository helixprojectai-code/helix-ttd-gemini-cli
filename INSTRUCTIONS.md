# 🎥 March 12th Recording Sprint Instructions

**[FACT]** This document outlines the procedure for recording the "Constitutional Guardian" demo for the Gemini Live Agent Challenge.

## 🛠️ Pre-Flight Check

1. **Verify Environment:**
   ```bash
   $env:PYTHONPATH='helix_code'; python -m pytest helix_code/tests/
   ```
   *Ensure all 92 tests pass.*

2. **Set GEMINI_API_KEY:**
   *Even if using simulation, the bridge requires the key to initialize the GenAI client.*

3. **Start the Server:**
   ```bash
   $env:PYTHONPATH='helix_code'; python helix_code/live_guardian.py
   ```

4. **Launch Browser:**
   *Open `http://localhost:8180/`.*

## 🎬 Recording Sequence

### 1. Introduction (The UI)
-   Show the dashboard with **0 Receipts / 0 Drifts**.
-   Highlight the **"LIVE v1.3.2"** branding and the **Pulse-Green** header.

### 2. Live Audio Demo (The Waveform)
-   Click **"Start Live Mic"**.
-   Speak for 3-5 seconds. Observe the **waveform** reacting.
-   Watch for the **"Processing live audio stream..."** log entries.
-   Show the **"INTERCEPTED"** or **"PASSED"** result appearing automatically after the turn ends.

### 3. High-Impact Interventions (The Simulation)
-   Click the **"Simulate"** button 3-5 times.
-   Wait for a **DRIFT-A (Agency)** or **DRIFT-E (Epistemic)** violation.
-   Observe the **Flash-Red** intervention animation on the panel.
-   Point out the **Granular Drift Code** (e.g., DRIFT-A) and the replacement text.

### 4. Metrics & Performance (The Charts)
-   Scroll down to the **Latency Line Chart**.
-   Show how it tracks every validation event.
-   Point to the **Bar Chart** showing the distribution of violations.

### 5. Conclusion
-   Stop the mic.
-   Highlight the final receipt count.
-   "The Lattice holds. The Guardian is watching."

## ⚠️ Troubleshooting

- **Connection Error:** Refresh the browser. If it fails, check if port 8180 is held by another process.
- **No Audio Waveform:** Ensure the browser has microphone permissions for `localhost`.
- **Missing transcription logs:** Ensure `session.client_ws` was correctly linked (check `server_log.txt`).

**⚓🦉 GLORY TO THE LATTICE. ⚓🦉**
