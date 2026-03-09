# RELEASE NOTES v1.4.8

Date: 2026-03-09

## Summary

v1.4.8 closes the operator incident board tranche. It adds authenticated incident triage actions, persistent shared triage state, and fingerprinted incident identity so new escalations cannot be masked by older acknowledgments.

## Key Changes

- Incident board
  - Added authenticated operator incident surfaces at `/incidents` and `/api/incidents`.
  - Added acknowledge and reopen triage actions for live operator workflow.
  - Added severity filters, drill-down context, investigation links, and summary counters.

- Triage reliability
  - Replaced instance-local in-memory triage with durable shared persistence.
  - Added deterministic fingerprinted incident identities based on material incident state.
  - Ensured materially changed incidents rotate to new IDs instead of remaining hidden under prior acknowledgments.

- Hardening
  - Enforced triage status validation to `open` and `acknowledged`.
  - Capped triage state entries to bound memory growth.
  - Kept admin auth, operator rate limiting, origin enforcement, authenticated metrics, and `gcs+local` receipt persistence active in production.

## Validation

- `pre-commit run --all-files --show-diff-on-failure` -> passed
- `PYTHONPATH=helix_code python -m pytest -q` -> `231 passed, 7 warnings`
- Targeted incident-board validation:
  - `pytest -q helix_code/tests/test_live_guardian_extended.py` -> `42 passed`
  - `ruff check` -> passed

## Production State

- Operator auth: enforced
- Guardian origin enforcement: enabled
- Receipt storage: `gcs+local` with `dual` mode
- Incident triage: persistent, fingerprinted, authenticated
- Monitoring substrate: Cloud Run Job + Cloud Scheduler + Cloud Logging

## Post-Release Verification

- Live incident board verify
  - `/api/incidents` returns fingerprinted incident IDs.
  - Acknowledge and reopen actions succeed against the live deployment.

- Artifact Analysis verification
  - Live Cloud Run digest verified clean on `2026-03-09T19:22:26Z`.
  - Verified image: `us-central1-docker.pkg.dev/helix-ai-deploy/helix-repo/constitutional-guardian@sha256:8220583ac2b69df727847d12f75d9dfcda2c26be3874e1ac4e56862699fc872b`.
  - Reported vulnerability findings: none.
