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
- Canonical image lineage: `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian`

## Current Verified State

- Repo commits carrying registry migration and verification work: `b50fec8` and follow-up workflow repair.
- Cloud Run security transparency endpoint now reports:
  - `artifact_analysis.status=clean`
  - `artifact_analysis.scan_timestamp=2026-03-08T11:29:23Z`
  - `artifact_analysis.image_uri=us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:a68ebdc0075e40d0b734b3c2e220cb277e6d84e19843031a5ded68e7013a5c77`
- Deploy-time scan timestamp remains separate from post-deploy Artifact Analysis verification:
  - `latest_scan_timestamp=2026-03-08T10:42:57Z`
  - `artifact_analysis.scan_timestamp=2026-03-08T11:29:23Z`

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
- `HELIX_ALLOWED_ORIGINS=https://console.example.com,https://ops.example.com`
- `HELIX_OPERATOR_RATE_LIMIT_MAX_REQUESTS=120`
- `HELIX_OPERATOR_RATE_LIMIT_WINDOW_SECONDS=60`
- `HELIX_AUTH_RATE_LIMIT_MAX_ATTEMPTS=12`
- `HELIX_AUTH_RATE_LIMIT_WINDOW_SECONDS=300`
- `HELIX_AUDIO_INGRESS_MAX_CONNECTIONS=12`
- `HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS=60`
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


## Production Operator Access Control

Recommended production posture:

- inject `HELIX_ADMIN_TOKEN`
- set `HELIX_ENFORCE_ADMIN_TOKEN=true`

Protected surfaces include:

- `/api/runtime-config`
- `/api/security-transparency`
- `/security-transparency`
- `/api/audit-dashboard`
- `/audit-dashboard`
- `/api/receipts`
- `/api/receipts/{receipt_id}`
- WebSockets: `/live`, `/demo-live`

### Rollout Using Cloud Run Env Vars

```powershell
& $GCLOUD run services update constitutional-guardian `
  --project helix-ai-deploy `
  --region us-central1 `
  --update-env-vars "HELIX_ADMIN_TOKEN=REPLACE_ME,HELIX_ENFORCE_ADMIN_TOKEN=true"
```

### Better Production Pattern

Use Secret Manager-backed env injection for the token and keep enforcement separate. Deploy automation now preserves that binding by using secret updates instead of replacing the full secret set.

Example:

```powershell
& $GCLOUD run services update constitutional-guardian `
  --project helix-ai-deploy `
  --region us-central1 `
  --update-env-vars "HELIX_ENFORCE_ADMIN_TOKEN=true" `
  --update-secrets "HELIX_ADMIN_TOKEN=HELIX_ADMIN_TOKEN:latest"
```

### Verification

Unauthenticated API request should fail:

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/runtime-config"
```

Expected result:

- `401` when token is configured but not supplied
- `503` when enforcement is enabled but token is missing

Authenticated request:

```powershell
$headers = @{ "X-Helix-Admin-Token" = "YOUR_TOKEN" }
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/runtime-config" -Headers $headers
```

Browser workflow:

- open a protected page
- submit token through `/auth/admin`
- app stores an HttpOnly cookie for same-origin operator access

## Production Browser Origin Policy

Recommended production posture:

- set `HELIX_ALLOWED_ORIGINS` to the exact trusted browser origins that should access Guardian APIs or WebSockets cross-origin
- keep the list narrow; do not use `*` in production
- if `HELIX_ALLOWED_ORIGINS` is unset in production, Guardian WebSockets fall back to same-origin-only validation using forwarded host/proto headers
- audio audit remains separately controllable through `AUDIO_AUDIT_ALLOWED_ORIGINS`

Example:

```powershell
& $GCLOUD run services update constitutional-guardian `
  --project helix-ai-deploy `
  --region us-central1 `
  --update-env-vars "HELIX_ALLOWED_ORIGINS=https://constitutional-guardian-231586465188.us-central1.run.app,https://console.helixprojectai.com"
```

Verification:

- trusted same-origin or allowlisted browser clients should connect normally
- off-origin browser WebSocket attempts to `/live` or `/demo-live` should close with policy violation
- `/api/runtime-config` reports both `guardian_allowed_origins` and `guardian_origin_enforced`

## Production Rate Limiting

Current hardening adds coarse in-memory throttling for operator surfaces and audio ingress. Recommended starting values:

- `HELIX_OPERATOR_RATE_LIMIT_MAX_REQUESTS=120`
- `HELIX_OPERATOR_RATE_LIMIT_WINDOW_SECONDS=60`
- `HELIX_AUTH_RATE_LIMIT_MAX_ATTEMPTS=12`
- `HELIX_AUTH_RATE_LIMIT_WINDOW_SECONDS=300`
- `HELIX_AUDIO_INGRESS_MAX_CONNECTIONS=12`
- `HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS=60`

Coverage:

- operator APIs and HTML surfaces: `/api/runtime-config`, `/api/security-transparency`, `/security-transparency`, `/api/audit-dashboard`, `/audit-dashboard`, `/api/receipts`, `/api/receipts/{receipt_id}`
- admin login form: `/auth/admin`
- audio ingress WebSocket: `/audio-audit`

Expected behavior:

- over-limit operator or auth requests return `429` with a `Retry-After` header
- over-limit audio ingress attempts close with WebSocket `1013` (try again later)
- `/api/runtime-config` reflects the active rate-limit window and budget values

## Authenticated Observability

The Guardian now exposes a Prometheus-style `/metrics` endpoint behind operator auth. This keeps operational telemetry available for scraping without making compliance or deployment metadata public.

Coverage includes:

- request, receipt, intervention, and error counts
- latency averages and percentiles
- drift category totals
- voice-pipeline event totals
- auth-failure and rate-limit counters
- receipt backend status
- artifact verification state
- active rate-limit configuration

Example scrape with header auth:

```powershell
$headers = @{ "X-Helix-Admin-Token" = $ADMIN_TOKEN }
Invoke-WebRequest "https://constitutional-guardian-231586465188.us-central1.run.app/metrics" -Headers $headers
```

Expected behavior:

- unauthenticated requests return `401` when operator auth is configured
- authenticated requests return Prometheus exposition text
- the artifact verification line should show the current live digest and `status="clean"` only after manual verification

Recommended usage:

- treat `/metrics` as an operator-only surface
- keep scraping same-origin or behind your trusted monitoring path
- use `tools/verify-production-deploy.ps1 -AdminToken $ADMIN_TOKEN -RequireCleanArtifact` after a manual verification cycle

## Alerting Baseline

The first production alert set is documented in:

- `PRODUCTION_ALERTING_SPEC_2026-03-08.md`

It is based directly on authenticated `/metrics` and covers:

- live artifact verification drift
- operator auth failure bursts
- operator and audio ingress rate-limit spikes
- receipt backend posture drift
- origin/auth enforcement regression

Use this document as the operator reference before wiring Cloud Monitoring, Prometheus, or a scheduled verifier.

## Scheduled Alert Verifier

A stateful alert checker is available at:

- `tools/check-production-alerts.ps1`

It consumes authenticated `/metrics` plus `/api/security-transparency`, keeps a small local snapshot history, and evaluates the alert rules in `PRODUCTION_ALERTING_SPEC_2026-03-08.md`.

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File tools/check-production-alerts.ps1 -AdminToken $ADMIN_TOKEN
```

Fail on warnings as well as page-level findings:

```powershell
powershell -ExecutionPolicy Bypass -File tools/check-production-alerts.ps1 -AdminToken $ADMIN_TOKEN -FailOnWarning
```

State file defaults to the local temp directory. Override when needed:

```powershell
powershell -ExecutionPolicy Bypass -File tools/check-production-alerts.ps1 -AdminToken $ADMIN_TOKEN -StateFile Z:\codex\alert-state.json
```

Recommended schedule:

- every 5 minutes for production polling
- keep the same state file path across runs so burst detection works

Repo-managed schedule:

- `.github/workflows/production-alert-check.yml`

This workflow:

- authenticates with the existing GitHub deploy identity
- restores the prior checker state from `gs://helix-ai-deploy-receipts/ops/production-alert-state.json`
- runs `tools/check-production-alerts.ps1`
- publishes the JSON summary to Cloud Logging under `helix-production-alerts`
- writes the updated state file back to GCS so burst detection survives runner resets

Prerequisites:

- repo secret: `HELIX_ADMIN_TOKEN`
- deploy identity access to:
  - `gs://helix-ai-deploy-receipts/ops/production-alert-state.json`
  - Cloud Logging write

Publisher helper:

- `tools/publish-monitoring-snapshot.py`

This reads the alert checker JSON summary and emits a structured Cloud Logging entry keyed by the current overall status.

## Deployment Verification Script

A single-reference verification helper is available at:

- `tools/verify-production-deploy.ps1`

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File tools/verify-production-deploy.ps1
```

For full operator checks:

```powershell
powershell -ExecutionPolicy Bypass -File tools/verify-production-deploy.ps1 -AdminToken $ADMIN_TOKEN
```

Optional strict artifact requirement:

```powershell
powershell -ExecutionPolicy Bypass -File tools/verify-production-deploy.ps1 -AdminToken $ADMIN_TOKEN -RequireCleanArtifact
```

What it checks:

- `/health`
- unauthenticated runtime-config gate behavior
- authenticated `/api/runtime-config`
- authenticated `/api/security-transparency`
- authenticated `/api/audit-dashboard`
- active receipt persistence backend

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
- builds Docker image under `us-central1-docker.pkg.dev/$PROJECT_ID/helix-repo/constitutional-guardian`
- pushes immutable tag plus `latest`
- deploys to Cloud Run from Artifact Registry
- preserves optional runtime envs by updating only the managed runtime/security keys
- preserves existing secret bindings by updating only declared secrets
- resets artifact verification metadata to `unverified` for each newly deployed digest

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


## Production Receipt Persistence

### Current Implementation

The app already supports these receipt persistence modes:

- `memory`
- `local`
- `gcs`
- `gcs+local`

Relevant envs:

- `HELIX_RECEIPT_PERSISTENCE=auto|local|gcs|dual`
- `HELIX_RECEIPT_STORE_PATH`
- `GCS_RECEIPT_BUCKET`

Recommended production mode:

- `HELIX_RECEIPT_PERSISTENCE=dual`
- `GCS_RECEIPT_BUCKET=<bucket-name>`

That gives:

- durable GCS archive for cross-revision restore
- local JSONL fallback for rapid same-instance access

### Recommended Bucket

Use a dedicated bucket, for example:

- `helix-ai-deploy-receipts`

Create it if needed:

```powershell
& $GCLOUD storage buckets create gs://helix-ai-deploy-receipts `
  --project helix-ai-deploy `
  --location us-central1
```

### Required IAM

Grant the Cloud Run service account object permissions on the receipt bucket.

Observed runtime service account:

- `231586465188-compute@developer.gserviceaccount.com`

Recommended role on the bucket:

- `roles/storage.objectAdmin`

### Rollout Command

```powershell
& $GCLOUD run services update constitutional-guardian `
  --project helix-ai-deploy `
  --region us-central1 `
  --update-env-vars "HELIX_RECEIPT_PERSISTENCE=dual,GCS_RECEIPT_BUCKET=helix-ai-deploy-receipts"
```

### Verification

Runtime config:

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/runtime-config"
```

Audit dashboard:

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/audit-dashboard"
```

Expected storage signals after rollout:

- `receipts.persistence_mode = dual`
- `receipts.gcs_bucket_configured = true`
- audit/dashboard storage backend = `gcs+local` or `gcs`

### Restart Test

After enabling the bucket:

1. generate one or more receipts
2. record a receipt ID from `/api/receipts`
3. force a new revision or redeploy
4. verify the same receipt ID is still retrievable

That is the real production persistence check.

### Verified Result

Production restart validation passed on `2026-03-08`.

- Tested receipt ID: `live_demo_9b50bffacd6e4bc1961d6e09d8b13e1d_1`
- Receipt retrieval succeeded before restart
- Receipt retrieval succeeded after forced new Cloud Run revision
- Hash verification remained valid after restart
- Effective production storage backend: `gcs+local`

## Artifact Analysis / Vulnerability Verification

### Important registry note

Canonical deploy target now uses Artifact Registry:

- `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian`

Historical note:

- prior production revisions used `gcr.io/helix-ai-deploy/constitutional-guardian`
- current production revisions are now served from Artifact Registry
- keep the earlier `gcr.io` digest as historical verification evidence only

### Live verified digest

- `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:a68ebdc0075e40d0b734b3c2e220cb277e6d84e19843031a5ded68e7013a5c77`

### Query vulnerabilities for live image

```powershell
$IMAGE="us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:a68ebdc0075e40d0b734b3c2e220cb277e6d84e19843031a5ded68e7013a5c77"

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
  --update-env-vars "SECURITY_ARTIFACT_ANALYSIS_STATUS=clean,SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=2026-03-08T11:29:23Z,SECURITY_ARTIFACT_IMAGE_URI=us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:a68ebdc0075e40d0b734b3c2e220cb277e6d84e19843031a5ded68e7013a5c77"
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
- `artifact_analysis.scan_timestamp=2026-03-08T11:29:23Z`
- `artifact_analysis.image_uri` matches the live Artifact Registry digest

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

- build and deploy should now converge on `us-central1-docker.pkg.dev/.../helix-repo/...`
- any remaining `gcr.io/...` references should be treated as historical and cleaned up as revisions roll forward

Recommended follow-through:

1. run the first Artifact Registry-backed deploy
2. verify Cloud Run serves the new Artifact Registry image path
3. refresh verification docs with the first Artifact Registry digest
