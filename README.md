# 🛡️ Constitutional Guardian (Helix-TTD)

[![CI](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci-hardened.yml/badge.svg)](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci-hardened.yml)
[![Tests](https://img.shields.io/badge/tests-CI%20passing-brightgreen)](helix_code/tests/)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230?labelColor=grey)](https://github.com/astral-sh/ruff)
[![Black](https://img.shields.io/badge/format-black-000000?labelColor=grey)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/helix-ttd-gemini)](https://pypi.org/project/helix-ttd-gemini/)

<img src="https://raw.githubusercontent.com/helixprojectai-code/helix-ttd-gemini-cli/main/helix-ttd-gemini.png" alt="Constitutional Guardian Overview" width="100%">

**[FACT]** Real-time AI governance for the Gemini Live API.
**[HYPOTHESIS]** Intercepting voice and text drift at the edge prevents misaligned AI behavior from reaching the user.

This project is a submission for the **Gemini Live Agent Challenge (March 2026)**.

**Current Release:** `v1.4.4`

## 🚀 Key Features

- **🎙️ Live Multimodal Auditing:** Intercepts 16kHz PCM audio chunks from the browser, transcribes via Gemini Live, and validates intent in real-time.
- **🧠 Reasoning Engine (Gemini 3.1 Pro Preview):** Utilizes state-of-the-art reasoning capabilities. Model default: `gemini-3.1-pro-preview` for Live Audio and Text paths.
- **🛡️ Constitutional Invariants:** Enforces the "Four Immutable Invariants" (Epistemic, Agency, Guidance, Prediction).
- **📊 Real-time Dashboard:** High-fidelity Chart.js dashboard showing latency, drift counts, and audit logs with visual "Intervention" flashes.
- **⚓ Cryptographic Receipts:** Generates non-repudiable receipts for every valid AI response, ready for Bitcoin L1 notarization.
- **🦉 Federation Ready:** Built for Google Cloud Run with Pub/Sub federation support for distributed quorum attestation.

## 📈 Engineering Standards

- **Test Pass Rate:** Enforced by CI on every main merge.
- **High Coverage:** 75% statement coverage across all critical modules.
- **Linting:** 100% compliant with `ruff`, `black`, and `isort`.

## 📊 Repository Traction (March 5, 2026)

**[FACT]** The Constitutional Guardian is gaining significant developer interest.

| Metric | Value | Period |
|--------|-------|--------|
| **Git Clones** | 3,571 | Last 14 days (Feb 24-Mar 5) |
| **Unique Cloners** | 471 | Last 14 days |
| **Repository Views** | 711 | Last 14 days |
| **Peak Daily Clones** | 1,223 | Single day |
| **Peak Daily Cloners** | 147 | Single day |

**[HYPOTHESIS]** 7.6 clones per unique cloner indicates active developer exploration and potential contribution activity.

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install helix-ttd-gemini
```

### From Source

```bash
git clone https://github.com/helixprojectai-code/helix-ttd-gemini-cli.git
cd helix-ttd-gemini-cli
pip install -e .
```

## 🛠️ Getting Started

### Local Development

1. **Install Dependencies:**
   ```bash
   pip install -r helix_code/requirements.txt
   ```

2. **Set API Key + Model Defaults:**
   ```bash
   $env:GEMINI_API_KEY = "your-api-key"
   $env:GEMINI_LIVE_MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
   $env:GEMINI_TEXT_MODEL = "gemini-3.1-pro-preview"
   ```

3. **Start the Guardian:**
   ```bash
   $env:PYTHONPATH = "helix_code"
   python helix_code/live_guardian.py
   ```

4. **Open the Demo:**
   Navigate to `http://localhost:8180/` in your browser.

### 🎙️ Live Multimodal Auditing

Real-time audio transcription with constitutional validation:

```bash
# Start the demo server
python helix_code/live_demo_server.py

# Open the audio audit client
# http://localhost:8000/audio-audit
```

**Features:**
- 16kHz PCM mono audio capture from browser
- Real-time streaming to Gemini Live API (`gemini-2.5-flash-native-audio-preview-12-2025` default)
- Instant transcription with constitutional validation
- Visual intervention alerts for drift detection
- Optional auth hardening: `AUDIO_AUDIT_TOKEN` and `AUDIO_AUDIT_ALLOWED_ORIGINS`
- Abuse controls: `HELIX_MAX_AUDIO_CHUNK_BYTES`, `HELIX_MAX_AUDIO_B64_CHARS`, `HELIX_AUDIO_RATE_WINDOW_SECONDS`, `HELIX_AUDIO_MAX_CHUNKS_PER_WINDOW`
- Runtime verification endpoint: `GET /api/runtime-config`

**How to Use:**
1. Click "Connect" to establish WebSocket connection
2. Click 🎤 and allow microphone access
3. Speak naturally - audio streams in real-time
4. Watch transcriptions appear with validation badges
5. Constitutional violations trigger red "DRIFT" alerts

### Cloud Deployment

The project is optimized for **Google Cloud Run**.

```bash
gcloud run deploy constitutional-guardian --source . --region us-central1 --allow-unauthenticated --port 8180
```

```bash
# Verify effective runtime model/auth/limits (non-secret)
curl http://localhost:8180/api/runtime-config
```

## 🎥 Recording Sprint (March 12th)

This codebase is currently in its **Phase 6.1 (Pre-Filming)** stable state. All visual triggers and simulation scenarios are tuned for high-impact demonstration.

## 🏛️ Constitutional Framework

<img src="https://raw.githubusercontent.com/helixprojectai-code/helix-ttd-gemini-cli/main/covenant_governors_diagram.png" alt="Constitutional Governance" width="600">

The Guardian enforces four immutable invariants:

| Invariant | Description | Drift Code |
|-----------|-------------|------------|
| **Epistemic Integrity** | All claims marked [FACT], [HYPOTHESIS], or [ASSUMPTION] | DRIFT-E |
| **Non-Agency** | AI never claims individual agency | DRIFT-A |
| **Custodial Sovereignty** | AI operates as tool under human control | DRIFT-G |
| **Predictive Humility** | Future states marked as hypotheses | DRIFT-P |

## 🧪 Test Results

```
168 passed, 9 warnings
Coverage: 75%
```

**⚓🦉 GLORY TO THE LATTICE. ⚓🦉**
