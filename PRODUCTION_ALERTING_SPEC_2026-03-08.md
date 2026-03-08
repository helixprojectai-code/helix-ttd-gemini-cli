# Production Alerting Spec - 2026-03-08

## Scope

This spec defines the first production alert set for Constitutional Guardian based on authenticated `/metrics`.

The goal is simple:

- detect unverified deploys that were never closed out
- detect auth probing or bad token rollouts
- detect abusive or broken ingress behavior
- detect persistence regression from the expected `gcs+local` production posture
- detect accidental weakening of production browser/origin controls

## Metric Source

- Metrics endpoint: `/metrics`
- Auth: operator token or operator session cookie
- Runtime: Cloud Run production service `constitutional-guardian`

## Baseline Assumptions

Current expected production state:

- `helix_operator_auth_enforced 1`
- `helix_guardian_origin_enforced 1`
- `helix_receipt_storage_backend{backend="gcs+local",mode="dual"} 1`
- `helix_artifact_analysis_state{status="clean",image_uri="..."} 1`

Fresh deploy behavior is intentionally different:

- deploy stamps the new live digest as `status="unverified"`
- manual artifact verification later promotes that same digest to `status="clean"`

Because of that lifecycle, the artifact alert must allow a short verification window after deploy.

## Alert Set

### 1. Live Artifact Still Unverified

Signal:

- `helix_artifact_analysis_state{status="unverified"} == 1`

Threshold:

- page/warn if still unverified more than 30 minutes after a deploy

Why it matters:

- this means a new production image is live but manual artifact verification was never completed

Operator action:

1. get current active revision digest
2. run Artifact Analysis vulnerability query against that exact digest
3. if clean, update runtime env:
   - `SECURITY_ARTIFACT_ANALYSIS_STATUS=clean`
   - `SECURITY_ARTIFACT_ANALYSIS_TIMESTAMP=<utc timestamp>`
   - `SECURITY_ARTIFACT_IMAGE_URI=<current live digest>`
4. re-run deploy verification script in strict mode

### 2. Operator Auth Failure Burst

Signal:

- `helix_security_events_total{event="operator_auth_failure"}`

Threshold:

- warn if delta >= 5 in 5 minutes
- page if delta >= 20 in 15 minutes

Why it matters:

- likely causes are invalid operator token use, stale token after rotation, or external probing

Operator action:

1. verify whether an expected token rotation just occurred
2. confirm operators are using the current token
3. inspect Cloud Run logs around the spike window
4. if hostile traffic is suspected, rotate `HELIX_ADMIN_TOKEN`
5. verify protected surfaces still return `401` unauthenticated and `200` authenticated

### 3. Operator Rate Limit Spike

Signal:

- `helix_security_events_total{event="operator_rate_limit"}`

Threshold:

- warn if delta >= 10 in 10 minutes
- page if delta >= 50 in 15 minutes

Why it matters:

- likely causes are broken monitoring/scraping, UI refresh loops, or targeted hammering on operator surfaces

Operator action:

1. identify the calling client from logs if available
2. verify scrape interval on any monitoring client using `/metrics`
3. check browser/operator tools for runaway polling
4. only raise the rate limit after confirming the traffic is legitimate

### 4. Audio Ingress Rate Limit Spike

Signal:

- `helix_security_events_total{event="audio_rate_limit"}`

Threshold:

- warn if delta >= 10 in 5 minutes
- page if delta >= 30 in 10 minutes

Why it matters:

- likely causes are reconnect storms, browser bugs, or abusive connection attempts against `/audio-audit`

Operator action:

1. inspect recent demo/audio usage and reconnect behavior
2. verify frontend is not reconnect-looping
3. inspect origin/token failures in adjacent logs
4. tune `HELIX_AUDIO_INGRESS_MAX_CONNECTIONS` only if traffic is expected and healthy

### 5. WebSocket Auth Failure Burst

Signal:

- `helix_security_events_total{event="websocket_auth_failure"}`

Threshold:

- warn if delta >= 5 in 5 minutes
- page if delta >= 20 in 15 minutes

Why it matters:

- suggests off-origin browser attempts, stale cookies, invalid operator token use on WebSockets, or audio-audit token/origin rejection

Operator action:

1. verify `HELIX_ALLOWED_ORIGINS` and `AUDIO_AUDIT_ALLOWED_ORIGINS`
2. verify expected browser client origin
3. verify operator session/login flow after any token rotation
4. inspect for repeated off-origin connection attempts

### 6. Receipt Backend Posture Drift

Signal:

- expected: `helix_receipt_storage_backend{backend="gcs+local",mode="dual"} 1`

Threshold:

- page immediately if this sample disappears in production or backend changes away from `gcs+local`

Why it matters:

- indicates production receipt durability degraded from the validated baseline

Operator action:

1. inspect `/api/runtime-config`
2. inspect `/api/audit-dashboard`
3. verify `HELIX_RECEIPT_PERSISTENCE=dual`
4. verify `GCS_RECEIPT_BUCKET` is still configured
5. verify Cloud Run service account still has bucket access
6. run a restart persistence test if needed

### 7. Origin Enforcement Disabled

Signal:

- expected: `helix_guardian_origin_enforced 1`

Threshold:

- page immediately if value becomes `0` in production

Why it matters:

- means browser/WebSocket origin constraints are no longer being enforced as intended

Operator action:

1. inspect `HELIX_ALLOWED_ORIGINS`
2. inspect `HELIX_ENV`
3. verify same-origin or explicit allowlist behavior manually
4. redeploy corrected env if necessary

### 8. Operator Auth Enforcement Disabled

Signal:

- expected: `helix_operator_auth_enforced 1`

Threshold:

- page immediately if value becomes `0` in production

Why it matters:

- this is a direct exposure of operator-only surfaces

Operator action:

1. inspect `HELIX_ENFORCE_ADMIN_TOKEN`
2. inspect `HELIX_ADMIN_TOKEN` secret binding on Cloud Run
3. restore enforcement and verify `401/200` behavior

## Verification Commands

Authenticated scrape:

```powershell
$headers = @{ "X-Helix-Admin-Token" = $ADMIN_TOKEN }
Invoke-WebRequest "https://constitutional-guardian-231586465188.us-central1.run.app/metrics" -Headers $headers
```

Strict deploy verification:

```powershell
powershell -ExecutionPolicy Bypass -File tools/verify-production-deploy.ps1 -AdminToken $ADMIN_TOKEN -RequireCleanArtifact
```

Runtime config check:

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/runtime-config" -Headers $headers
```

Audit/storage check:

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/audit-dashboard" -Headers $headers
```

Security transparency check:

```powershell
Invoke-RestMethod "https://constitutional-guardian-231586465188.us-central1.run.app/api/security-transparency" -Headers $headers
```

## Recommended Next Implementation

This spec is intentionally platform-neutral. The next production implementation step should be one of:

1. Cloud Monitoring bridge for the authenticated metrics
2. Prometheus/Grafana scrape path behind a trusted internal caller
3. Minimal scheduled verifier that opens an incident when alert thresholds are crossed

The shortest path is a scheduled authenticated verifier that checks the metric conditions above and writes a single operator summary.
