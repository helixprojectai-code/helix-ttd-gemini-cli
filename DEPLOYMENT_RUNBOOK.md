# Constitutional Guardian - Deployment Runbook

**Project:** helix-ttd-gemini-cli (Constitutional Guardian)  
**Environment:** Google Cloud Platform (Production)  
**Deployed:** March 5, 2026  
**Live URL:** https://constitutional-guardian-b25t5w6zva-uc.a.run.app  

---

## Executive Summary

This runbook documents the complete deployment of Constitutional Guardian to Google Cloud Run, including architecture decisions, IAM configurations, troubleshooting steps, and operational procedures.

**Status:** ✅ PRODUCTION READY  
**Health Check:** https://constitutional-guardian-b25t5w6zva-uc.a.run.app/health  

---

## 1. Architecture Overview

### 1.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Voice)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Gemini Live API (Audio → Text)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ Text Stream
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         CONSTITUTIONAL GUARDIAN (Cloud Run)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Epistemic   │  │    Drift     │  │   Receipt    │      │
│  │   Validator  │  │   Detector   │  │   Generator  │      │
│  │[FACT]/[HYPO] │  │              │  │  SHA256+DBC  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────┬──────────────────────────────────────┘
                       │ Safe Response
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Gemini Response (Voice Out)                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Google Cloud Services Used

| Service | Purpose | Code Reference |
|---------|---------|----------------|
| Cloud Run | Serverless container hosting | `.github/workflows/deploy-gcp.yml` |
| Artifact Registry | Docker image storage | `us-central1-docker.pkg.dev` |
| Cloud Build (initially) | CI/CD pipeline (deprecated) | See troubleshooting |
| Workload Identity Federation | Secure GitHub auth | IAM configuration |
| Cloud Logging | Audit trails | Application logging |
| Cloud Monitoring | Health checks | Built into Cloud Run |

### 1.3 Deployment Flow

1. GitHub Actions triggers on push to `main`
2. Workload Identity Federation authenticates to GCP
3. Docker builds container in GitHub Actions runner
4. Image pushed to Artifact Registry
5. Cloud Run deploys from Artifact Registry
6. Health check validates deployment

---

## 2. Pre-Deployment Requirements

### 2.1 GCP Project Setup

**Project ID:** `helix-ai-deploy`  
**Project Number:** `231586465188`

**Required APIs Enabled:**
```bash
# Core APIs
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable iamcredentials.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com

# Initially attempted (deprecated path)
gcloud services enable cloudbuild.googleapis.com  # See troubleshooting
```

### 2.2 Service Account Configuration

**Primary Service Account:** `github-deployer@helix-ai-deploy.iam.gserviceaccount.com`

**Required IAM Roles:**

| Role | Purpose | Required For |
|------|---------|--------------|
| `roles/run.admin` | Deploy to Cloud Run | Service deployment |
| `roles/artifactregistry.writer` | Push images | Docker registry access |
| `roles/iam.serviceAccountUser` | Impersonate SA | Workload Identity |
| `roles/logging.logWriter` | Write logs | Application logging |
| `roles/iam.workloadIdentityUser` | Workload Identity | GitHub auth |

**Secondary Service Account (Cloud Build - Deprecated):**
`231586465188-compute@developer.gserviceaccount.com`

Attempted roles:
- `roles/cloudbuild.builds.editor`
- `roles/cloudbuild.serviceAgent`
- `roles/storage.objectAdmin`

**Issue:** Cloud Build bucket permissions failed. See Troubleshooting section 6.1.

### 2.3 Workload Identity Federation Setup

**Identity Pool:** `github-pool`  
**Provider:** `github-provider`  
**Resource Name:**
```
projects/231586465188/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

**Attribute Mappings:**
```yaml
google.subject: assertion.sub
attribute.repository: assertion.repository
```

**Service Account Binding:**
```
principalSet://iam.googleapis.com/projects/231586465188/locations/global/workloadIdentityPools/github-pool/attribute.repository/helixprojectai-code/helix-ttd-gemini-cli
```

### 2.4 GitHub Secrets

**Repository:** helixprojectai-code/helix-ttd-gemini-cli

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `WORKLOAD_IDENTITY_PROVIDER` | `projects/231586465188/locations/global/workloadIdentityPools/github-pool/providers/github-provider` | GCP authentication |
| `GCP_PROJECT_ID` | `helix-ai-deploy` | Project identification |

---

## 3. Deployment Process

### 3.1 GitHub Actions Workflow

**File:** `.github/workflows/deploy-gcp.yml`

**Key Steps:**

1. **Checkout Code**
   ```yaml
   - uses: actions/checkout@v4
   ```

2. **Authenticate to GCP**
   ```yaml
   - uses: google-github-actions/auth@v2
     with:
       workload_identity_provider: ${{ secrets.WORKLOAD_IDENTITY_PROVIDER }}
       service_account: github-deployer@helix-ai-deploy.iam.gserviceaccount.com
   ```

3. **Configure Docker**
   ```yaml
   - run: gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

4. **Build and Push**
   ```yaml
   - run: |
       docker build -t IMAGE:TAG .
       docker push IMAGE:TAG
   ```

5. **Deploy to Cloud Run**
   ```yaml
   - run: gcloud run deploy SERVICE --image IMAGE:TAG --region us-central1
   ```

### 3.2 Container Configuration

**Base Image:** `python:3.11-slim`

**Exposed Port:** `8180`

**Environment Variables:**
```bash
HELIX_NODE_ID=GCS-GUARDIAN
HELIX_ENV=production
GOOGLE_CLOUD_PROJECT=helix-ai-deploy
PORT=8180
```

**Resource Allocation:**
- Memory: 1Gi
- CPU: 2
- Concurrency: 100
- Max Instances: 10

### 3.3 Deployment Commands

**Manual Deployment (if needed):**
```bash
# Build
docker build -t constitutional-guardian:latest .

# Tag for Artifact Registry
docker tag constitutional-guardian:latest \
  us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian:latest

# Push
docker push us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian:latest

# Deploy
gcloud run deploy constitutional-guardian \
  --image us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --port 8180
```

---

## 4. Post-Deployment Configuration

### 4.1 Public Access Configuration

**Required:** Allow public access for API endpoints

**Via Console:**
1. Cloud Run → constitutional-guardian → Security
2. Select: "Allow public access"
3. Save

**Via gcloud:**
```bash
gcloud run services add-iam-policy-binding constitutional-guardian \
  --region=us-central1 \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=helix-ai-deploy
```

### 4.2 Verification Steps

**Health Check:**
```bash
curl https://constitutional-guardian-b25t5w6zva-uc.a.run.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "node_id": "GCS-GUARDIAN",
  "version": "1.0.0",
  "compliance_ready": true
}
```

**Validation Endpoint:**
```bash
curl -X POST "https://constitutional-guardian-b25t5w6zva-uc.a.run.app/validate?text=[FACT]%20Test"
```

**Service Details:**
```bash
gcloud run services describe constitutional-guardian --region=us-central1
```

---

## 5. Operational Procedures

### 5.1 Monitoring

**Cloud Run Console:**
https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian

**Key Metrics:**
- Request latency (target: <500ms p95)
- Error rate (target: <1%)
- Instance count (auto-scales 1-10)
- Memory utilization

**Logs:**
```bash
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=constitutional-guardian"
```

### 5.2 Scaling Configuration

**Current Settings:**
- Min instances: 0 (scales to zero when idle)
- Max instances: 10
- Concurrency: 100 requests per instance

**Adjust if needed:**
```bash
gcloud run services update constitutional-guardian \
  --region=us-central1 \
  --min-instances=1 \
  --max-instances=20 \
  --concurrency=200
```

### 5.3 Rollback Procedure

**To previous revision:**
```bash
# List revisions
gcloud run revisions list --service=constitutional-guardian --region=us-central1

# Rollback to specific revision
gcloud run services update-traffic constitutional-guardian \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

### 5.4 Environment Updates

**Update environment variables:**
```bash
gcloud run services update constitutional-guardian \
  --region=us-central1 \
  --set-env-vars="KEY1=VALUE1,KEY2=VALUE2"
```

---

## 6. Troubleshooting

### 6.1 Cloud Build Bucket Permission Errors (RESOLVED)

**Error:**
```
ERROR: (gcloud.builds.submit) INVALID_ARGUMENT: could not resolve source: 
googleapi: Error 403: 231586465188-compute@developer.gserviceaccount.com 
does not have storage.objects.get access
```

**Root Cause:** Cloud Build service account couldn't access uploaded source tarball in GCS due to complex IAM propagation and bucket-level policies.

**Resolution:** Switched to Docker build in GitHub Actions + Artifact Registry, bypassing Cloud Build entirely.

**Lessons:**
- Cloud Build has complex IAM requirements
- Docker build in GitHub Actions is more reliable for simple deployments
- Artifact Registry has simpler permission model

### 6.2 Workload Identity Federation Issues

**Error:**
```
ERROR: (gcloud.builds.submit) PERMISSION_DENIED: The caller does not have permission
```

**Root Cause:** Missing IAM roles for service account impersonation.

**Resolution:** Added `roles/iam.serviceAccountUser` to `github-deployer` service account.

### 6.3 Artifact Registry Repository Not Found

**Error:**
```
name unknown: Repository "helix-repo" not found
```

**Resolution:** Created repository:
```bash
gcloud artifacts repositories create helix-repo \
  --repository-format=docker \
  --location=us-central1 \
  --project=helix-ai-deploy
```

### 6.4 Public Access Denied

**Error:**
```
Error: Forbidden
Your client does not have permission to get URL / from this server
```

**Resolution:** Enabled public access via Cloud Run console Security tab, granting `allUsers` the `roles/run.invoker` role.

### 6.5 API Not Enabled

**Error:**
```
ERROR: (gcloud.builds.submit) PERMISSION_DENIED: Cloud Build API has not been used
```

**Resolution:** Enabled required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com  # Initially
# Later switched to:
gcloud services enable artifactregistry.googleapis.com
```

---

## 7. Security Configuration

### 7.1 Authentication Flow

```
GitHub Actions (OIDC Token)
    ↓
Workload Identity Federation
    ↓
Short-lived GCP Access Token
    ↓
Artifact Registry (Push)
    ↓
Cloud Run (Deploy)
```

**No long-lived credentials stored in GitHub.**

### 7.2 IAM Audit

**Project-level permissions:**
- `github-deployer@helix-ai-deploy.iam.gserviceaccount.com`
  - Cloud Run Admin
  - Artifact Registry Writer
  - IAM Service Account User
  - Logging Log Writer
  - Workload Identity User

**Service-level permissions:**
- `allUsers` → Cloud Run Invoker (for public API access)

### 7.3 Network Security

- HTTPS only (enforced by Cloud Run)
- TLS 1.3
- No VPC connector (public endpoint)
- CORS not configured (API-only, no browser clients)

---

## 8. Cost Management

### 8.1 Current Configuration

**Billing Alert:** $100 USD (recommended)

**Estimated Monthly Cost:**
- Cloud Run (idle): ~$0 (scales to zero)
- Cloud Run (active): ~$5-20 (depends on traffic)
- Artifact Registry: ~$1-5 (storage)
- Logging: ~$2-10 (depends on volume)

**Total Estimate:** $10-35/month for light usage

### 8.2 Cost Control Measures

1. **Budget Alert:** Set at $100
2. **Max Instances:** Limited to 10
3. **CPU Allocation:** Only during request processing
4. **Memory:** 1Gi (can reduce to 512Mi if needed)

### 8.3 Reducing Costs

```bash
# Reduce memory
gcloud run services update constitutional-guardian \
  --region=us-central1 \
  --memory=512Mi

# Set max instances lower
gcloud run services update constitutional-guardian \
  --region=us-central1 \
  --max-instances=5
```

---

## 9. API Documentation

### 9.1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/validate` | POST | Validate text for compliance |
| `/live` | WebSocket | Real-time audio validation |

### 9.2 Example Requests

**Health Check:**
```bash
curl https://constitutional-guardian-b25t5w6zva-uc.a.run.app/health
```

**Validate Text:**
```bash
curl -X POST "https://constitutional-guardian-b25t5w6zva-uc.a.run.app/validate?text=[FACT]%20Water%20boils%20at%20100C"
```

**Expected Response:**
```json
{
  "compliant": true,
  "epistemic_markers": {
    "fact": true,
    "hypothesis": false,
    "assumption": false
  },
  "agency_violations": [],
  "recommendation": "PASS"
}
```

---

## 10. Appendix

### 10.1 Useful Commands

```bash
# View service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=constitutional-guardian" --limit=50

# List revisions
gcloud run revisions list --service=constitutional-guardian --region=us-central1

# View service YAML
gcloud run services describe constitutional-guardian --region=us-central1 --format=yaml

# Update environment variables
gcloud run services update constitutional-guardian --region=us-central1 --set-env-vars="KEY=VALUE"

# Delete service (DANGER)
gcloud run services delete constitutional-guardian --region=us-central1
```

### 10.2 Links

| Resource | URL |
|----------|-----|
| Live Service | https://constitutional-guardian-b25t5w6zva-uc.a.run.app |
| Health Check | https://constitutional-guardian-b25t5w6zva-uc.a.run.app/health |
| Cloud Run Console | https://console.cloud.google.com/run/detail/us-central1/constitutional-guardian |
| GitHub Repo | https://github.com/helixprojectai-code/helix-ttd-gemini-cli |
| GitHub Actions | https://github.com/helixprojectai-code/helix-ttd-gemini-cli/actions |

### 10.3 Contact

**Maintainer:** Stephen Hope  
**Email:** helix.project.ai@helixprojectai.com  
**Organization:** helixprojectai-code

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-03-05 | 1.0 | Initial deployment | Stephen Hope |
| 2026-03-05 | 1.1 | Switched from Cloud Build to Docker + Artifact Registry | Stephen Hope |

---

**END OF RUNBOOK**

*Constitutional Guardian is deployed and operational.*  
*The constitution persists. The guardian is watching. The lattice holds.*  
🦉⚓🦉
