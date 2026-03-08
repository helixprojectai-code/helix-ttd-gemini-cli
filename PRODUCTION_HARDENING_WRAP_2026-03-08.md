# Production Hardening Wrap - 2026-03-08

## Scope Closed

This note closes the March 8 production hardening tranche for the Constitutional Guardian Cloud Run deployment.

## Completed

- Artifact Registry is now the canonical production image source.
- GitHub deploy automation preserves runtime env and secret bindings instead of replacing them.
- Artifact verification lifecycle is correct:
  - each deploy resets the live image to `artifact_analysis.status=unverified`
  - manual verification promotes the active digest to `clean`
- Security transparency is live and verified against the current deployed image digest.
- Production receipt persistence is active in `dual` mode.
  - GCS bucket: `helix-ai-deploy-receipts`
  - active backend observed: `gcs+local`
- Cross-revision receipt durability was tested successfully.
- Operator auth is enforced in production.
  - `HELIX_ADMIN_TOKEN` is secret-backed
  - `HELIX_ENFORCE_ADMIN_TOKEN=true`
- Guardian browser/WebSocket origin policy is hardened.
  - production defaults to same-origin-only when no allowlist is configured
  - explicit cross-origin access is controlled through `HELIX_ALLOWED_ORIGINS`
- Operator/API/audio ingress rate limiting is implemented.
- Deployment verification tooling exists and was validated in production.
  - script: `tools/verify-production-deploy.ps1`
  - strict mode now passes for the current live deployment

## Verified Production Outcomes

- `/health` passes.
- Protected operator APIs return `401` unauthenticated and `200` when authenticated.
- `/api/runtime-config` reports:
  - `persistence_mode=dual`
  - `gcs_bucket_configured=True`
- `/api/audit-dashboard` reports storage backend `gcs+local`.
- `/api/security-transparency` reports the active live image and a `clean` artifact verification state after attestation.
- Receipt retrieval survives Cloud Run revision replacement.

## Operational Baseline Now In Place

- Secret Manager-backed production secrets
- Cloud Run deploy hygiene
- Artifact Analysis attestation loop
- Durable receipt storage
- Protected operator surfaces
- Explicit browser origin policy
- Basic ingress throttling
- Post-deploy verification script

## Next Production Work

### 1. Observability Export

Add a production-safe metrics export path for operational signals:

- request counts
- intervention counts
- receipt counts
- auth failures
- rate-limit events
- audio ingress rejects
- artifact verification state

Preferred direction:

- authenticated `/metrics` surface or OpenTelemetry export
- avoid adding public unauthenticated operational detail

### 2. Rate-Limit Telemetry And Tuning

Current limits are conservative defaults. Next step is measuring real traffic and tuning:

- `HELIX_OPERATOR_RATE_LIMIT_MAX_REQUESTS`
- `HELIX_OPERATOR_RATE_LIMIT_WINDOW_SECONDS`
- `HELIX_AUTH_RATE_LIMIT_MAX_ATTEMPTS`
- `HELIX_AUTH_RATE_LIMIT_WINDOW_SECONDS`
- `HELIX_AUDIO_INGRESS_MAX_CONNECTIONS`
- `HELIX_AUDIO_INGRESS_RATE_LIMIT_WINDOW_SECONDS`

This should be based on observed production behavior, not guesswork.

### 3. Deploy-Time Verification Automation

Current flow correctly resets artifact status to `unverified`, but manual promotion to `clean` is still operator-driven.

Next improvement:

- a small operator runbook step or scripted helper that:
  - resolves active digest
  - runs Artifact Analysis query
  - stamps `clean` metadata if and only if the digest is verified clean

### 4. Operator Access Ergonomics

Operator auth is correct but still manual.

Next polish:

- formalize token rotation steps in a short operator checklist
- add a cookie/logout flow if needed for browser operators
- optionally separate read-only operator views from full admin views later

### 5. Persistence Lifecycle Review

Receipt persistence is working. Next production review should answer:

- retention period
- bucket lifecycle policy
- archival strategy
- whether receipt exports should be signed and bundled periodically

## Recommended Immediate Next Task

If staying on production infrastructure, do this next:

1. add authenticated metrics/observability export
2. record and tune rate-limit telemetry from real traffic
3. streamline digest verification promotion to `clean`

If shifting back to product work, the platform is now hardened enough to support it without obvious production hygiene gaps.
