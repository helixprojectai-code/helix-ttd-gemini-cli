# 🛡️ Constitutional Guardian (Helix-TTD)

[![CI](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci-hardened.yml/badge.svg)](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci-hardened.yml)
[![Tests](https://img.shields.io/badge/tests-CI%20passing-brightgreen)](helix_code/tests/)
[![Coverage](https://img.shields.io/badge/coverage-75%25-brightgreen)](pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230?labelColor=grey)](https://github.com/astral-sh/ruff)
[![Black](https://img.shields.io/badge/format-black-000000?labelColor=grey)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-1.4.7-blue)](https://pypi.org/project/helix-ttd-gemini/)

![Constitutional Guardian Overview](https://raw.githubusercontent.com/helixprojectai-code/helix-ttd-gemini-cli/main/assets/helix-ttd-gemini.png)

**[FACT]** Real-time AI governance for the Gemini Live API.
**[HYPOTHESIS]** Intercepting voice and text drift at the edge prevents misaligned AI behavior from reaching the user.

This project is a submission for the **Gemini Live Agent Challenge (March 2026)**.

**Current Release:** `v1.4.7`

## Production Stabilization In v1.4.7

- **GCP-Native Production Monitoring:** The scheduled production checker now runs as a Cloud Run Job with Cloud Scheduler and Cloud Logging integration instead of GitHub Actions.
- **Alert Signal Cleanup:** Missing credentials no longer inflate operator or websocket auth-failure counters; only explicit invalid credentials are counted.
- **Release-Ready Monitor State:** Production monitoring now reports `overall_status=pass`, `monitor_integrity_status=ok`, and a clean live artifact attestation.
- **Operator Enforcement Baseline:** Admin auth, origin enforcement, authenticated metrics, and `gcs+local` dual receipt persistence remain active in production.
- **Artifact Verification Workflow:** Live images are scanned and promoted to `clean` against Artifact Registry digests after deploy.
- **Operational Proof Refresh:** README traction, archived release notes, and proof assets were rotated into the current documentation layout.

## 🚀 Key Features

- **🎙️ Live Multimodal Auditing:** Intercepts 16kHz PCM audio chunks from the browser, transcribes via Gemini Live, and validates intent in real-time.
- **🧠 Reasoning Engine (Gemini 3.1 Pro Preview):** Utilizes state-of-the-art reasoning capabilities. Model default: `gemini-3.1-pro-preview` for Live Audio and Text paths.
- **🛡️ Constitutional Invariants:** Enforces the "Four Immutable Invariants" (Epistemic, Agency, Guidance, Prediction).
- **📊 Real-time Dashboard:** High-fidelity Chart.js dashboard showing latency, drift counts, and audit logs with visual "Intervention" flashes.
- **⚓ Cryptographic Receipts:** Generates non-repudiable receipts for every valid AI response, ready for Bitcoin L1 notarization.
- **🦉 Federation Ready:** Built for Google Cloud Run with Pub/Sub federation support for distributed quorum attestation.

## 📈 Engineering Standards

- **Test Pass Rate:** `201/201` passing in release validation, with CI enforced on every main merge.
- **High Coverage:** 75% statement coverage across all critical modules.
- **Linting:** 100% compliant with `ruff`, `black`, and `isort`.

## 📊 Repository Traction (March 8, 2026)

**[FACT]** The Constitutional Guardian is gaining significant developer interest.

| Metric | Value | Period |
|--------|-------|--------|
| **Git Clones** | 7,240 | Last 14 days |
| **Unique Cloners** | 855 | Last 14 days |
| **Repository Views** | 1,190 | Last 14 days |
| **Unique Visitors** | 24 | Last 14 days |
| **Peak Daily Clones** | 1,527 | Single day |
| **Peak Daily Cloners** | 198 | Single day |

**[HYPOTHESIS]** 8.5 clones per unique cloner indicates active developer exploration and potential contribution activity.

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
- Optional auth hardening: `AUDIO_AUDIT_TOKEN`, `AUDIO_AUDIT_ALLOWED_ORIGINS`, and `HELIX_ALLOWED_ORIGINS`
- Abuse controls: `HELIX_MAX_AUDIO_CHUNK_BYTES`, `HELIX_MAX_AUDIO_B64_CHARS`, `HELIX_AUDIO_RATE_WINDOW_SECONDS`, `HELIX_AUDIO_MAX_CHUNKS_PER_WINDOW`, `HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS`, `HELIX_AUDIO_INGRESS_MAX_CONNECTIONS`
- Runtime verification endpoint: `GET /api/runtime-config`
- Audit dashboard endpoints: `GET /audit-dashboard` and `GET /api/audit-dashboard`
- Optional operator auth: `HELIX_ADMIN_TOKEN` for runtime, security, dashboard, and receipt surfaces
- Recommended production operator posture: set `HELIX_ADMIN_TOKEN` and `HELIX_ENFORCE_ADMIN_TOKEN=true`
- Recommended production throttling posture: keep operator APIs on `HELIX_OPERATOR_RATE_LIMIT_MAX_REQUESTS=120` / `HELIX_OPERATOR_RATE_LIMIT_WINDOW_SECONDS=60` and audio ingress on `HELIX_AUDIO_INGRESS_MAX_CONNECTIONS=12` / `HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS=60` unless measured load requires adjustment
- Recommended production browser posture: set `HELIX_ALLOWED_ORIGINS` to the exact trusted UI origins; otherwise Guardian WebSockets default to same-origin-only in production
- Optional durable receipt envs: `HELIX_RECEIPT_PERSISTENCE`, `HELIX_RECEIPT_STORE_PATH`, `GCS_RECEIPT_BUCKET`
- Recommended production receipt mode: `HELIX_RECEIPT_PERSISTENCE=dual` with a dedicated `GCS_RECEIPT_BUCKET`
- Production restart test verified receipt survival across Cloud Run revisions on `2026-03-08`
- Optional security transparency envs: `SECURITY_ARTIFACT_ANALYSIS_STATUS`, `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP`, `SECURITY_ARTIFACT_IMAGE_URI`
- Deployment verification helper: `powershell -ExecutionPolicy Bypass -File tools/verify-production-deploy.ps1 [-AdminToken <token>]`
- Scheduled alert checker: `powershell -ExecutionPolicy Bypass -File tools/check-production-alerts.ps1 -AdminToken <token>`
- Production monitoring direction changed: scheduled polling has moved off GitHub Actions and onto a GCP-native Cloud Run Job + Cloud Scheduler path
- Cloud Logging sink publisher: `python tools/publish-monitoring-snapshot.py --input <summary.json>`
- Cloud Run Job checker entrypoint: `python tools/cloud_check_production.py`
- Cloud Build job deployment config: `cloudbuild-monitoring-job.yaml`
- Authenticated metrics endpoint: `GET /metrics` using bearer token, `X-Helix-Admin-Token`, or the operator session cookie
- Deployment automation preserves optional operator secret bindings by using secret updates rather than replacing the full secret set

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

# Inspect operator audit summary
curl http://localhost:8180/api/audit-dashboard

# Inspect security transparency metadata
curl http://localhost:8180/api/security-transparency

# Scrape authenticated Prometheus-style metrics
curl -H "X-Helix-Admin-Token: $env:HELIX_ADMIN_TOKEN" http://localhost:8180/metrics
```

**Current security verification record:** `RELEASE_NOTES_v1.4.7.md` and `SECURITY_VERIFICATION_2026-03-09.md` capture the March 9, 2026 clean Artifact Analysis result for the live Cloud Run digest.

**Production alerting baseline:** `PRODUCTION_ALERTING_SPEC_2026-03-08.md` defines the first authenticated-metrics alert set for artifact verification, auth failures, rate limiting, and receipt persistence posture.

**Production product handoff:** `PRODUCT_WORK_HANDOFF_2026-03-08.md` captures the recommended return path from hardening work back into product execution.

## 🎥 Recording Sprint (March 12th)

This codebase is currently in its **Phase 6.1 (Pre-Filming)** stable state. All visual triggers and simulation scenarios are tuned for high-impact demonstration.

## 🏛️ Constitutional Framework

<img src="https://raw.githubusercontent.com/helixprojectai-code/helix-ttd-gemini-cli/main/assets/ARCHITECTURE_CG.png" alt="Constitutional Governance" width="600">

The Guardian enforces four immutable invariants:

| Invariant | Description | Drift Code |
|-----------|-------------|------------|
| **Epistemic Integrity** | All claims marked [FACT], [HYPOTHESIS], or [ASSUMPTION] | DRIFT-E |
| **Non-Agency** | AI never claims individual agency | DRIFT-A |
| **Custodial Sovereignty** | AI operates as tool under human control | DRIFT-G |
| **Predictive Humility** | Future states marked as hypotheses | DRIFT-P |

## 🧪 Test Results

```
201 passed, 7 warnings
Coverage: 75%
```

**⚓🦉 GLORY TO THE LATTICE. ⚓🦉**
