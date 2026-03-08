# RELEASE NOTES v1.4.6

Date: 2026-03-08

## Summary

v1.4.6 is an operational hardening release focused on secure operator surfaces, durable audit state, and production-safe secret handling.

## Key Changes

- Secret management
  - Added Vault-backed Gemini secret resolution with environment fallback.
  - Exposed non-secret secret-backend posture through runtime config.

- Operator protection
  - Added optional `HELIX_ADMIN_TOKEN` protection for runtime config, security transparency, audit dashboard, and receipts endpoints.
  - Accepted auth via bearer token, `X-Helix-Admin-Token`, or query token.

- Audit and receipts
  - Added audit dashboard HTML/API surfaces for compliance review.
  - Added durable receipt persistence hooks with local JSONL backing and optional GCS archival/restore integration.
  - Surfaced receipt storage diagnostics in runtime and audit APIs.

- Runtime cleanup
  - Replaced deprecated FastAPI startup hooks with lifespan initialization.

- Release/documentation surfaces
  - Package/runtime/UI version bumped to `1.4.6`.
  - README and instruction documents updated for the hardened operator/deploy flow.
  - PyPI badge updated to explicit `1.4.6`.

## Validation

- `pre-commit run --all-files --show-diff-on-failure`
- `pytest -q` -> `201 passed, 7 warnings`

## Operator Notes

- Set `HELIX_ADMIN_TOKEN` in production if runtime and audit surfaces should not remain publicly readable.
- Enable durable receipts with one of:
  - `HELIX_RECEIPT_PERSISTENCE=local`
  - `HELIX_RECEIPT_PERSISTENCE=gcs`
  - `HELIX_RECEIPT_PERSISTENCE=dual`
- Optional envs:
  - `HELIX_RECEIPT_STORE_PATH`
  - `GCS_RECEIPT_BUCKET`
