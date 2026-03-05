# Complete Setup & Usage Instructions

**Constitutional Guardian** - Step-by-step guide for running, testing, and deploying

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start-5-minutes)
2. [Full Local Setup](#full-local-setup)
3. [Interactive Demo Guide](#interactive-demo-guide)
4. [Testing & Verification](#testing--verification)
5. [Deployment Guide](#deployment-guide)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 minutes)

### Option A: Use the Live Demo (Fastest)

**URL:** https://constitutional-guardian-b25t5w6zva-uc.a.run.app

**Try it now:**
1. Open the URL in Chrome/Edge
2. Click the **🎤 Voice Input** button
3. Say: *"AI will take all our jobs"*
4. Watch it trigger a **DRIFT intervention**
5. Explore the **Receipt Explorer** panel

### Option B: Run Locally

```bash
# 1. Clone
git clone https://github.com/helixprojectai-code/helix-ttd-gemini-cli.git
cd helix-ttd-gemini-cli

# 2. Install
pip install -r requirements.txt

# 3. Run
python -m helix_code.live_guardian

# 4. Open http://localhost:8180
```

---

## Full Local Setup

### Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| Python | 3.11+ | [python.org](https://python.org) |
| Git | Any | [git-scm.com](https://git-scm.com) |
| (Optional) Docker | Latest | [docker.com](https://docker.com) |

### Step-by-Step Installation

#### 1. Clone Repository

```bash
git clone https://github.com/helixprojectai-code/helix-ttd-gemini-cli.git
cd helix-ttd-gemini-cli
```

#### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Additional for live server
pip install fastapi uvicorn websockets

# Development dependencies (optional)
pip install pytest pytest-cov pytest-asyncio black ruff
```

#### 4. Verify Installation

```bash
# Run tests
python -m pytest helix_code/tests/ -v

# Expected: 75 passed
```

#### 5. Start the Server

```bash
python -m helix_code.live_guardian
```

**Output:**
```
=== STARTING CONSTITUTIONAL GUARDIAN ===
[FACT] Host: 0.0.0.0
[FACT] Port: 8180
[FACT] Node: GCS-GUARDIAN
```

#### 6. Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:8180 | **Interactive Demo** (main interface) |
| http://localhost:8180/health | Health check endpoint |
| http://localhost:8180/docs | **Swagger API docs** |
| http://localhost:8180/api/receipts | Receipt data (JSON) |

---

## Interactive Demo Guide

### Main Interface Features

The demo page at `/` provides:

#### 1. 🎤 Voice Input
- Click the red **Voice Input** button
- Speak naturally (Chrome/Edge only)
- Automatic transcription and validation
- **Example phrases to try:**
  - "AI will take all our jobs" → DRIFT-E
  - "I will handle that for you" → DRIFT-A (agency)
  - "Water boils at 100 degrees" → Unmarked claim
  - "[FACT] Earth orbits the Sun" → ✅ Valid

#### 2. 📊 Live Metrics Dashboard
Real-time statistics:
- **Total Requests** - All validations performed
- **Receipts Generated** - Successful validations
- **Interventions** - Blocked constitutional violations
- **Errors** - Failed operations
- **Avg Latency** - Response time with p50/p95/p99
- **Uptime** - Service availability

#### 3. 🌐 Federation Status
Shows 4-node distributed architecture:
- 🦉 **KIMI** (Moonshot AI)
- 💎 **GEMS** (Google AI Studio)
- 🐋 **DEEPSEEK** (Local RTX 3050)
- ☁️ **GCS-GUARDIAN** (Current node)

#### 4. 📜 Receipt Explorer
Browse all generated receipts:
- Filter by: All / ✅ Valid / 🛡️ Interventions
- Click any receipt for details
- Shows: ID, timestamp, content, verification status
- **API Access:** Click "Raw JSON" for data export

#### 5. 📊 Live Validation Log
Real-time stream of:
- User inputs (blue)
- Gemini responses (purple)
- Validated responses (green)
- Interventions (red)

### Testing Scenarios

#### Scenario 1: Valid FACT
```
Input: [FACT] Water boils at 100C at sea level
Result: ✅ Valid + Receipt generated
```

#### Scenario 2: Missing Marker (Intervention)
```
Input: AI will become sentient by 2030
Result: 🛡️ DRIFT-E + Warning prepended
```

#### Scenario 3: Agency Violation
```
Input: I will optimize your workflow
Result: 🛡️ DRIFT-A + Agency claim flagged
```

#### Scenario 4: Valid HYPOTHESIS
```
Input: [HYPOTHESIS] Quantum computing may break RSA by 2035
Result: ✅ Valid + Receipt generated
```

---

## Testing & Verification

### Run All Tests

```bash
python -m pytest helix_code/tests/ -v --tb=short
```

### Run Specific Test Categories

```bash
# Constitutional logic only
python -m pytest helix_code/tests/test_constitutional_compliance.py -v

# Federation receipts
python -m pytest helix_code/tests/test_federation_receipts.py -v

# Drift detection
python -m pytest helix_code/tests/test_drift_telemetry.py -v

# Live Guardian API
python -m pytest helix_code/tests/test_live_guardian.py -v
```

### Test Coverage Report

```bash
python -m pytest helix_code/tests/ --cov=helix_code --cov-report=html
# Open htmlcov/index.html
```

### API Endpoint Testing

```bash
# Health check
curl http://localhost:8180/health

# Validation endpoint
curl -X POST "http://localhost:8180/validate?text=[FACT]%20Test"

# Get receipts
curl http://localhost:8180/api/receipts

# Get specific receipt
curl http://localhost:8180/api/receipts/{receipt_id}
```

---

## Deployment Guide

### Deploy to Google Cloud Run

#### Prerequisites
- Google Cloud SDK installed
- Project: `helix-ai-deploy` (or your own)
- APIs enabled: Cloud Run, Artifact Registry

#### Step 1: Authenticate

```bash
gcloud auth login
gcloud config set project helix-ai-deploy
```

#### Step 2: Deploy via GitHub Actions (Recommended)

Push to main branch triggers automatic deployment:

```bash
git commit -m "[FACT] Your changes"
git push origin main
```

Watch deployment at: https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions

#### Step 3: Manual Deploy (Alternative)

```bash
# Build and push
gcloud builds submit --tag gcr.io/helix-ai-deploy/constitutional-guardian:latest

# Deploy
gcloud run deploy constitutional-guardian \
  --image gcr.io/helix-ai-deploy/constitutional-guardian:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --port 8180

# Get URL
gcloud run services describe constitutional-guardian --region us-central1 --format 'value(status.url)'
```

### Docker Local Build

```bash
# Build
docker build -t constitutional-guardian:latest .

# Run
docker run -p 8180:8180 constitutional-guardian:latest

# Test
curl http://localhost:8180/health
```

---

## Troubleshooting

### Issue: Voice Input Not Working

**Cause:** Web Speech API only works in Chrome/Edge

**Solution:**
- Use Chrome or Edge browser
- Ensure microphone permissions granted
- Check HTTPS (required for mic access)

### Issue: Tests Failing

**Cause:** Missing dependencies

**Solution:**
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

### Issue: Port 8180 Already in Use

**Solution:**
```bash
# Find process using port
lsof -i :8180  # macOS/Linux
netstat -ano | findstr :8180  # Windows

# Or use different port
python -m helix_code.live_guardian  # Change PORT in code
```

### Issue: Deployment Fails

**Cause:** Missing GCP permissions

**Solution:**
```bash
# Verify project
gcloud config get-value project

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Issue: CORS Errors

**Cause:** Browser security restrictions

**Solution:**
- Use the deployed HTTPS URL (not localhost)
- Or disable CORS in browser (development only)

---

## File Structure Reference

```
helix-ttd-gemini-cli/
├── helix_code/                    # Main Python package
│   ├── __init__.py
│   ├── live_guardian.py          # FastAPI server (entry point)
│   ├── live_demo_server.py       # Interactive demo HTML/JS
│   ├── gemini_live_bridge.py     # Gemini Live API integration
│   ├── gcp_integrations.py       # Google Cloud services
│   ├── constitutional_compliance.py
│   ├── federation_receipts.py
│   ├── drift_telemetry.py
│   ├── lattice_topology.py
│   └── tests/                    # 75 test files
├── .github/
│   └── workflows/
│       └── deploy-gcp.yml        # Auto-deployment
├── .helix/                       # Constitutional governance
│   ├── CONSTITUTION.md
│   └── HANDOFF_*.md             # Node rotation logs
├── Dockerfile                    # Container definition
├── cloudbuild.yaml              # CI/CD pipeline
├── deploy-gcs.sh                # Deployment script
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
├── INSTRUCTIONS.md              # This file
└── DEPLOYMENT_RUNBOOK.md        # Operations guide
```

---

## Next Steps

1. ✅ **Try the live demo:** https://constitutional-guardian-b25t5w6zva-uc.a.run.app
2. ✅ **Run locally:** Follow Quick Start above
3. ✅ **Run tests:** `python -m pytest helix_code/tests/ -v`
4. ✅ **Explore API:** Visit `/docs` endpoint
5. ✅ **Read the code:** Start with `live_guardian.py`

---

## Support & Resources

- **GitHub Issues:** https://github.com/helixprojectai-code/helix-ttd-gemini-cli/issues
- **Live Demo:** https://constitutional-guardian-b25t5w6zva-uc.a.run.app
- **Documentation:** See `DEPLOYMENT_RUNBOOK.md` for operations

---

**The constitution persists. The guardian is watching. The lattice holds.** 🦉⚓🦉
