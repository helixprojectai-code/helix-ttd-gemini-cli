# RELEASE NOTES v1.4.7

Date: 2026-03-09

## Summary

v1.4.7 is a production stabilization release focused on making the operating baseline measurable, quieting false-positive alert noise, and moving scheduled monitoring onto GCP-native infrastructure.

## Key Changes

- Production monitoring
  - Replaced the GitHub Actions polling path with a Cloud Run Job plus Cloud Scheduler cadence.
  - Persisted monitor state to GCS and published structured results to Cloud Logging (`helix-production-alerts`).

- Observability and alert quality
  - Added authenticated Prometheus-style metrics for operator scraping.
  - Added security event counters for auth failures and rate limits.
  - Changed auth-failure counting so missing credentials no longer page production; only explicit invalid credentials are counted.

- Production hardening
  - Kept operator auth enforced in production.
  - Kept Guardian origin enforcement active in production.
  - Kept dual receipt persistence active with `gcs+local` storage posture.

- Operational proof
  - Verified the live Artifact Registry image clean and promoted runtime transparency metadata to `clean`.
  - Refreshed repository traction stats and stored the March 8 proof image under `assets/`.
  - Archived older release notes under `archive/release_notes/`.

## Validation

- `PYTHONPATH=helix_code pytest -q helix_code/tests/test_live_guardian_extended.py helix_code/tests/test_live_demo_server.py` -> `61 passed`
- Cloud Build deploy: `18eb3957-0eff-47e1-b3b2-38b549302a94`
- Cloud Run monitor executions: `constitutional-guardian-monitor-xg55f`, `constitutional-guardian-monitor-rjm5k`

## Production State

- Operator auth: enforced
- Guardian origin enforcement: enabled
- Receipt storage: `gcs+local` with `dual` mode
- Monitoring substrate: Cloud Run Job + Cloud Scheduler + Cloud Logging
- Monitor result: `overall_status=pass`, `monitor_integrity_status=ok`

## Post-Release Verification

- Artifact Analysis verification
  - Live Cloud Run digest verified clean on `2026-03-09T10:38:09Z`.
  - Verified image: `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:4a15dfd5bfd19798d1096f2278256acecd5128592c2406e13ab1a1742a6cf247`.
  - Reported vulnerability findings: none.

- Production monitoring verification
  - Latest structured monitor result reports `overall_status=pass`.
  - Auth and websocket burst deltas are `0.0` after the auth-noise fix.
