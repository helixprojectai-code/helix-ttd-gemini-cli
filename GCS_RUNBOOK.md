# HELIX GCS RUNBOOK

Date: 2026-03-08

## Purpose

This document is the single operational reference for the Helix Constitutional Guardian deployment on Google Cloud.

It covers:

- Cloud Run deployment
- Cloud Build behavior
- Secrets and runtime env
- Pub/Sub wiring
- Artifact Analysis verification
- Windows PowerShell `gcloud` workflow
- Known failure modes and fixes

## Active Production Service

- Project ID: `helix-ai-deploy`
- Project Number: `231586465188`
- Region: `us-central1`
- Cloud Run Service: `constitutional-guardian`
- Public URL: `https://constitutional-guardian-231586465188.us-central1.run.app`
- Live image lineage: `gcr.io/helix-ai-deploy/constitutional-guardian`

## Current Verified State

- Repo commit carrying the security transparency verification work: `872781a`
- Cloud Run security transparency endpoint now reports:
  - `artifact_analysis.status=clean`
  - `artifact_analysis.scan_timestamp=2026-03-08T11:05:00Z`
  - `artifact_analysis.image_uri=gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7`
- Deploy-time scan timestamp remains separate from post-deploy Artifact Analysis verification:
  - `latest_scan_timestamp=2026-03-08T10:42:57Z`
  - `artifact_analysis.scan_timestamp=2026-03-08T11:05:00Z`

## Current Runtime Model Defaults

- `GEMINI_LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025`
- `GEMINI_TEXT_MODEL=gemini-3.1-pro-preview`
- `GEMINI_API_VERSION=v1beta`

## Cloud Run Runtime Env

Current production env contract includes:

- `HELIX_NODE_ID=GCS-GUARDIAN`
- `HELIX_ENV=production`
- `GOOGLE_CLOUD_PROJECT=helix-ai-deploy`
- `PUBSUB_TOPIC=projects/helix-ai-deploy/topics/helix-events`
- `GEMINI_LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025`
- `GEMINI_TEXT_MODEL=gemini-3.1-pro-preview`
- `GEMINI_API_VERSION=v1beta`
- `SECURITY_SCAN_TIMESTAMP`
- `SECURITY_TEST_STATUS`
- `SECURITY_POSTURE_SCORE`
- `SECURITY_CHECK_BANDIT`
- `SECURITY_CHECK_RUFF`
- `SECURITY_CHECK_MYPY`
- `SECURITY_CHECK_BLACK`
- `SECURITY_CHECK_ISORT`
- `SECURITY_CHECK_PRE_COMMIT`

Optional hardened envs:

- `HELIX_ADMIN_TOKEN`
- `HELIX_ENFORCE_ADMIN_TOKEN=true`
- `HELIX_RECEIPT_PERSISTENCE=auto|local|gcs|dual`
- `HELIX_RECEIPT_STORE_PATH`
- `GCS_RECEIPT_BUCKET`
- `SECURITY_ARTIFACT_ANALYSIS_STATUS`
- `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP`
- `SECURITY_ARTIFACT_IMAGE_URI`

## Secrets

Production secret currently in use:

- `GEMINI_API_KEY` via Cloud Run secret reference

Recommended model:

- keep `GEMINI_API_KEY` in Secret Manager
- use `HELIX_ADMIN_TOKEN` for operator surface protection
- do not pass admin tokens through query params
- use bearer header, `X-Helix-Admin-Token`, or browser session cookie

## Windows PowerShell Setup

Use a writable local config directory or `gcloud` will fail on credentials/log writes.

```powershell
$env:CLOUDSDK_CONFIG="Z:\codex\.gcloud"
$GCLOUD="C:\Users\sbhop\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
```

Without this, common failures include:

- `Unable to create private file ... credentials.db`
- `Could not setup log file ... permission denied`

## Cloud Run Operations

### Describe service

```powershell
& $GCLOUD run services describe constitutional-guardian `
  --region us-central1 `
  --project helix-ai-deploy
```

### Read service logs

```powershell
& $GCLOUD run services logs read constitutional-guardian `
  --region us-central1 `
  --project helix-ai-deploy `
  --limit 200
```

### Update env vars

```powershell
& $GCLOUD run services update constitutional-guardian `
  --project helix-ai-deploy `
  --region us-central1 `
  --update-env-vars "KEY=value"
```

### Verify health

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/health"
```

## Cloud Build

Build config:

- root file: `Z:\codex\helix-ttd-gemini-cli\cloudbuild.yaml`

Current behavior:

- emits security metadata
- builds Docker image under `gcr.io/$PROJECT_ID/constitutional-guardian`
- pushes immutable tag plus `latest`
- deploys to Cloud Run

### Manual submit

```powershell
& $GCLOUD builds submit "Z:\codex\helix-ttd-gemini-cli" `
  --project helix-ai-deploy `
  --config "Z:\codex\helix-ttd-gemini-cli\cloudbuild.yaml"
```

### Common build failures

#### Invalid image name with empty tag

Cause:

- unset `COMMIT_SHA` during manual builds

Fix already implemented:

- build uses `BUILD_ID` fallback
- final fallback tag is `manual`

#### Cloud Build cannot access uploaded source

Cause:

- service account lacks storage access to the Cloud Build bucket

Symptom:

- `storage.objects.get denied`

## Pub/Sub

Production topic:

- `projects/helix-ai-deploy/topics/helix-events`

### Verify topic

```powershell
& $GCLOUD pubsub topics describe helix-events --project helix-ai-deploy
```

### Publish smoke event

```powershell
& $GCLOUD pubsub topics publish helix-events `
  --message="smoke-$(Get-Date -Format o)" `
  --project helix-ai-deploy
```

### Required publisher IAM

Cloud Run service account observed in production:

- `231586465188-compute@developer.gserviceaccount.com`

Publisher role required on the topic:

- `roles/pubsub.publisher`

## Artifact Analysis / Vulnerability Verification

### Important registry note

Production currently serves from:

- `gcr.io/helix-ai-deploy/constitutional-guardian`

This is distinct from the Artifact Registry `helix-repo` image lineage. Do not verify the wrong image.

### Live verified digest

- `gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7`

### Query vulnerabilities for live image

```powershell
$IMAGE="gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7"

& $GCLOUD artifacts vulnerabilities list $IMAGE `
  --project helix-ai-deploy `
  --location us-central1 `
  --format="table(vulnerability.shortDescription, vulnerability.effectiveSeverity, packageIssue[0].affectedPackage, packageIssue[0].affectedVersion.fullName)"
```

Observed result on 2026-03-08:

- header only
- zero findings

### Cleared CVEs

- `CVE-2026-23949`
- `CVE-2026-24049`
- `CVE-2025-8869`

### Publish scan result into runtime metadata

```powershell
& $GCLOUD run services update constitutional-guardian `
  --project helix-ai-deploy `
  --region us-central1 `
  --update-env-vars "SECURITY_ARTIFACT_ANALYSIS_STATUS=clean,SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=2026-03-08T11:05:00Z,SECURITY_ARTIFACT_IMAGE_URI=gcr.io/helix-ai-deploy/constitutional-guardian@sha256:8abb896eb558ddc978c24af226bcc62d425f6e54f8513773b2ed62cbbe1726c7"
```

### Verify published security metadata

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/security-transparency"
```

If admin protection is enabled:

```powershell
$headers = @{ "X-Helix-Admin-Token" = "YOUR_TOKEN" }
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/security-transparency" -Headers $headers
```

## Security Transparency Semantics

Expected JSON fields:

- `latest_scan_timestamp`
- `timestamp_source`
- `security_posture_score`
- `checks.bandit`
- `checks.ruff`
- `checks.mypy`
- `checks.black`
- `checks.isort`
- `checks.pre_commit`
- `test_status`
- `artifact_analysis.status`
- `artifact_analysis.scan_timestamp`
- `artifact_analysis.image_uri`

If the output still shows:

- `artifact_analysis.status=unverified`
- `artifact_analysis.scan_timestamp=unavailable`
- `artifact_analysis.image_uri=unavailable`

then the Cloud Run metadata update has not yet been applied to the live revision.

Observed good state on 2026-03-08:

- `artifact_analysis.status=clean`
- `artifact_analysis.scan_timestamp=2026-03-08T11:05:00Z`
- `artifact_analysis.image_uri` matches the live `gcr.io` digest

## Audio / Gemini Live Known Good Configuration

For live audio transcription:

- `GEMINI_LIVE_MODEL=gemini-2.5-flash-native-audio-preview-12-2025`
- `GEMINI_API_VERSION=v1beta`

Known failure modes previously observed:

- wrong model for bidi streaming -> `1008 model not found / not supported`
- wrong payload type -> `1007 Cannot extract voices from a non-audio request`

Current system behavior:

- mic toggle defines turn boundary
- explicit `mic_stop` finalizes transcription
- live audio path is functional with the native audio preview model

## Operator Surfaces

Relevant endpoints:

- `/`
- `/health`
- `/api`
- `/api/gemini-status`
- `/api/runtime-config`
- `/security-transparency`
- `/api/security-transparency`
- `/audit-dashboard`
- `/api/audit-dashboard`
- `/api/receipts`

If `HELIX_ADMIN_TOKEN` is configured:

- operational surfaces require auth
- browser flow uses `/auth/admin`
- page session is stored in an HttpOnly cookie

## Git / CI Notes

Current repo SSH issue was resolved by switching Git to Windows OpenSSH globally.

If needed:

```powershell
git config --global core.sshCommand "C:/Windows/System32/OpenSSH/ssh.exe"
```

## Recommended Next Cleanup

The current deployment is operational, but the registry story is split:

- deploys run from `gcr.io/...`
- Artifact Registry browsing is under `us-central1-docker.pkg.dev/.../helix-repo/...`

Recommended future cleanup:

1. migrate build output fully to Artifact Registry
2. update `cloudbuild.yaml` deploy image path
3. retire dual-registry ambiguity
