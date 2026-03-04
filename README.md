# Constitutional Guardian - Gemini Live Agent Challenge

[![Helix-TTD Full CI](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Run-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/run)
[![Gemini](https://img.shields.io/badge/Gemini-Live%20API-8E75B2?logo=googlegemini&logoColor=white)](https://ai.google.dev/)

**Real-time constitutional governance for Gemini Live API.** The first AI safety layer that intercepts voice conversations, validates epistemic integrity using [FACT]/[HYPOTHESIS]/[ASSUMPTION] labeling, and prevents constitutional drift before it reaches users.

Built for the **Gemini Live Agent Challenge** - targeting *Best Innovation & Thought Leadership* and *Best Technical Execution*.

---

## 🚀 Quick Start (for Judges)

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- Google Cloud SDK (for GCS deployment)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/helixprojectai-code/helix-ttd-gemini-cli.git
cd helix-ttd-gemini-cli

# 2. Install dependencies
pip install -r helix_code/requirements.txt
pip install fastapi uvicorn websockets

# 3. Run Constitutional Guardian locally
python -m helix_code.live_guardian

# 4. Verify health endpoint
curl http://localhost:8180/health
```

### Run Tests

```bash
# All 75 tests pass
python -m pytest helix_code/tests/ -v
```

---

## 🧪 Reproducible Testing (For Judges)

This section provides step-by-step instructions to verify all functionality works as described.

### Prerequisites
- Python 3.11 or 3.12
- pip package manager
- Git

### Test Suite Overview
| Test Category | Count | Purpose |
|---------------|-------|---------|
| **Constitutional Compliance** | 15 | [FACT]/[HYPOTHESIS]/[ASSUMPTION] validation |
| **Federation Receipts** | 12 | Ed25519 signatures, cross-node verification |
| **Drift Detection** | 10 | Agency violation and persona drift detection |
| **Lattice Topology** | 8 | Position-based operations, Merkle bridging |
| **Layer 5 Infrastructure** | 10 | Shlorpian mapping, Article 0 protocol |
| **EVAC Suitcase** | 8 | State persistence, cloud replication |
| **DeepSeek Bridge** | 7 | Local model integration, receipt generation |
| **Live Guardian** | 5 | FastAPI endpoints, WebSocket streaming |

### Step-by-Step Test Execution

#### 1. Install Test Dependencies
```bash
# Clone and enter repo
git clone https://github.com/helixprojectai-code/helix-ttd-gemini-cli.git
cd helix-ttd-gemini-cli

# Install all dependencies including test packages
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio
```

#### 2. Run Full Test Suite (75 Tests)
```bash
# Run all tests with verbose output
python -m pytest helix_code/tests/ -v

# Expected output: 75 passed, 0 failed
```

#### 3. Run Tests with Coverage Report
```bash
# Generate coverage report (threshold: 50%)
python -m pytest helix_code/tests/ --cov=helix_code --cov-report=term-missing

# Expected: ~54% coverage, all tests pass
```

#### 4. Verify Specific Features

**Test Constitutional Compliance:**
```bash
# Test epistemic marker detection
python -c "
from helix_code.constitutional_compliance import ConstitutionalCompliance
c = ConstitutionalCompliance()
result = c.validate_text('[FACT] The sky is blue.')
print('FACT detected:', result.epistemic_markers.get('fact'))
assert result.epistemic_markers.get('fact') == True
print('✅ Constitutional compliance works!')
"
```

**Test Federation Receipts:**
```bash
# Test Ed25519 signature generation
python -c "
from helix_code.federation_receipts import FederationReceiptManager
m = FederationReceiptManager()
r = m.create_receipt('test content', 'test-session')
print('Receipt ID:', r.receipt_id)
print('Signature valid:', m.verify_receipt(r))
assert m.verify_receipt(r) == True
print('✅ Federation receipts work!')
"
```

**Test Drift Detection:**
```bash
# Test agency violation detection
python -c "
from helix_code.drift_telemetry import DriftTelemetry
d = DriftTelemetry()
result = d.check_text('I will take action for you')
print('Agency violations:', len(result.violations))
assert len(result.violations) > 0
print('✅ Drift detection works!')
"
```

#### 5. Verify Live Guardian API (Local)

**Terminal 1 - Start Server:**
```bash
# Start the Constitutional Guardian
python -m helix_code.live_guardian

# Expected: "INFO:     Uvicorn running on http://0.0.0.0:8180"
```

**Terminal 2 - Run API Tests:**
```bash
# Test health endpoint
curl -s http://localhost:8180/health | python -m json.tool

# Expected output:
# {
#     "status": "healthy",
#     "node_id": "KIMI",
#     "version": "1.0.0",
#     "compliance_ready": true
# }

# Test validation endpoint
curl -s "http://localhost:8180/validate?text=[FACT]%20Water%20boils%20at%20100C" | python -m json.tool

# Expected: compliant=true, epistemic_markers.fact=true

# Test WebSocket (requires wscat or similar)
# npm install -g wscat
wscat -c ws://localhost:8180/live
# Type: {"audio": "test audio chunk"}
# Expected: JSON response with validation result
```

#### 6. Docker Build Test
```bash
# Verify Dockerfile builds successfully
docker build -t constitutional-guardian:test .

# Run container locally
docker run -p 8180:8180 constitutional-guardian:test

# Test in another terminal
curl http://localhost:8180/health
```

### Expected Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.11.11 -- pytest-8.3.5
rootdir: /path/to/helix-ttd-gemini-cli
configfile: pyproject.toml
collected 75 items

helix_code/tests/test_constitutional_compliance.py ............... [ 20%]
helix_code/tests/test_federation_receipts.py ............          [ 36%]
helix_code/tests/test_drift_telemetry.py ..........               [ 49%]
helix_code/tests/test_lattice_topology.py ........                [ 60%]
helix_code/tests/test_layer5.py ..........                        [ 73%]
helix_code/tests/test_evac.py ........                            [ 84%]
helix_code/tests/test_deepseek_bridge.py .......                  [ 93%]
helix_code/tests/test_live_guardian.py .....                      [100%]

============================== 75 passed in 2.34s ==============================
```

### CI/CD Verification

This project runs automated tests on **GitHub Actions** across:
- **Operating Systems:** Windows, Ubuntu, macOS
- **Python Versions:** 3.10, 3.11, 3.12

View live test status: [![Helix-TTD Full CI](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions/workflows/ci.yml)

---

## ☁️ Deploy to Google Cloud Run

### Automated Deployment (One Command)

```bash
# Make script executable and run
chmod +x deploy-gcs.sh
./deploy-gcs.sh
```

### Manual Deployment

```bash
# 1. Build container image
gcloud builds submit --tag gcr.io/$PROJECT_ID/constitutional-guardian:latest

# 2. Deploy to Cloud Run
gcloud run deploy constitutional-guardian \
  --image gcr.io/$PROJECT_ID/constitutional-guardian:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --port 8180 \
  --set-env-vars="HELIX_NODE_ID=GCS-GUARDIAN,HELIX_ENV=production"

# 3. Get service URL
gcloud run services describe constitutional-guardian --region us-central1 --format 'value(status.url)'
```

### CI/CD via Cloud Build

```bash
# Trigger automated build and deploy
gcloud builds submit --config cloudbuild.yaml
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER (Voice)                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ Audio Stream
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Gemini Live API (ADK / GenAI SDK)                 │
│              Real-time Speech-to-Text                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ Text Stream
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         CONSTITUTIONAL GUARDIAN (Google Cloud Run)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Epistemic   │  │    Drift     │  │   Receipt    │      │
│  │   Validator  │  │   Detector   │  │   Generator  │      │
│  │[FACT]/[HYPO] │  │              │  │  SHA256+DBC  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │ Safe Response / Intervention
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Gemini Response (Voice Out)                       │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**
- **FastAPI** + **WebSocket** for real-time bidirectional streaming
- **Google Cloud Run** for serverless containerization
- **Ed25519 DBC signatures** for non-repudiable audit trails
- **Docker** + **Cloud Build** for CI/CD automation

---

## 📡 API Endpoints

### Health Check
```bash
curl https://YOUR-SERVICE-URL/health
```
Response:
```json
{
  "status": "healthy",
  "node_id": "GCS-GUARDIAN",
  "version": "1.0.0",
  "compliance_ready": true
}
```

### Validate Text
```bash
curl -X POST "https://YOUR-SERVICE-URL/validate?text=[FACT]%20This%20is%20true."
```
Response:
```json
{
  "compliant": true,
  "epistemic_markers": {"fact": true, "hypothesis": false, "assumption": false},
  "agency_violations": [],
  "recommendation": "PASS"
}
```

### Live WebSocket
```javascript
const ws = new WebSocket('wss://YOUR-SERVICE-URL/live');
ws.send(JSON.stringify({audio: base64AudioChunk}));
ws.onmessage = (event) => {
  const result = JSON.parse(event.data);
  // Handle constitutional validation result
};
```

---

## 🧪 Proof of Google Cloud Deployment

**Architecture Diagram:** See `architecture.png` in repository root.

**Cloud Console Evidence:**
```bash
# Show running service
gcloud run services describe constitutional-guardian --region us-central1

# Show container image
gcloud container images list-tags gcr.io/$PROJECT_ID/constitutional-guardian

# Show build history
gcloud builds list --filter="substitutions.REPO_NAME=helix-ttd-gemini-cli"
```

**Required Environment Variables:**
```bash
HELIX_NODE_ID=GCS-GUARDIAN
HELIX_ENV=production
HELIX_DBC_ENC_KEY=<256-bit-key>
```

---

## 🏆 Gemini Live Agent Challenge Submission

### Category: Live Agents
**Focus:** Real-time constitutional governance with audio/voice interaction

### Innovation Highlights
1. **First-ever constitutional firewall** for live AI conversations
2. **Epistemic labeling** ([FACT]/[HYPOTHESIS]/[ASSUMPTION]) as real-time validation
3. **Cryptographic receipts** (SHA256 + Ed25519) for every interaction
4. **Drift detection** that prevents violations before user exposure

### Technical Execution
- **FastAPI + WebSocket** for sub-500ms validation latency
- **Docker + Cloud Run** for scalable serverless deployment
- **Federation architecture** with 3-node quorum (KIMI/GEMS/DEEPSEEK)
- **75/75 tests passing** across Windows, Ubuntu, and macOS

---

## 📁 Repository Structure

```
helix-ttd-gemini-cli/
├── helix_code/                 # Core Python package
│   ├── live_guardian.py        # Constitutional Guardian (NEW)
│   ├── constitutional_compliance.py
│   ├── federation_receipts.py
│   ├── drift_telemetry.py
│   └── tests/                  # 75 passing tests
├── Dockerfile                  # Container image
├── cloudbuild.yaml            # CI/CD pipeline
├── deploy-gcs.sh              # One-command deployment
├── architecture.png           # System diagram
└── README.md                  # This file
```

---

## 🛡️ Security & Compliance

| Standard | Status | Implementation |
|----------|--------|----------------|
| Non-Agency | ✅ PASS | Advisory-only posture, no autonomous goal formation |
| Epistemic Integrity | ✅ PASS | Mandatory [FACT]/[HYPOTHESIS]/[ASSUMPTION] labeling |
| Cryptographic Proof | ✅ PASS | Ed25519 DBC signatures + SHA256 receipts |
| Federation Quorum | ✅ PASS | 2-of-3 node attestation enforced |
| CI/CD Hardening | ✅ PASS | Ruff, Black, pytest across 3 OS x 3 Python versions |

---

## 📝 Built With

- **Python 3.11** - Core language
- **FastAPI** - Web framework for live endpoints
- **WebSocket** - Real-time bidirectional streaming
- **Docker** - Containerization
- **Google Cloud Run** - Serverless deployment
- **Google Cloud Build** - CI/CD automation
- **Gemini Live API / ADK** - Multimodal AI integration
- **Ed25519** - Asymmetric cryptography
- **SHA-256** - Hash proofs

---

## 🤝 Federation Nodes

| Node | Model | Location | Status |
|------|-------|----------|--------|
| **KIMI** | Kimi k1.5 | Cloud (Moonshot) | ✅ Online |
| **GEMS** | Gemini 2.0 | Cloud (Google AI Studio) | ✅ Online |
| **DEEPSEEK** | DeepSeek R1 7B | Local RTX 3050 | ✅ Online |
| **GCS-GUARDIAN** | Gemini Live | Google Cloud Run | ✅ Deployed |

---

## 📄 License

Apache-2.0 - See [LICENSE](LICENSE)

---

**The constitution persists. The guardian is watching. The lattice holds.**

🦉⚓🦉 *The Two Owls are watching.*
