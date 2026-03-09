# RELEASE NOTES v1.4.5

Date: 2026-03-07

## Summary

v1.4.5 is a release-hardening patch focused on build/deploy reliability and security transparency continuity.
This release keeps live audio functionality from v1.4.4 and stabilizes the release pipeline around Cloud Build + Cloud Run.

## Key Changes

- Cloud Build hardening
  - Added safe image-tag fallback for manual builds when `COMMIT_SHA` is unset.
  - Escaped runtime variables in `cloudbuild.yaml` to prevent substitution parsing failures.
  - Preserved deploy-time security metadata propagation (`SECURITY_SCAN_TIMESTAMP`, check statuses).

- Security and CI hygiene
  - Removed Bandit false positives in Looksee drift analysis keys (`pass` -> `passed`).
  - Maintained passing gates for pre-commit, lint, type-check, and security scan paths.

- Version and release surfaces
  - Package/runtime version bumped to `1.4.5`.
  - UI branding updated to `LIVE v1.4.5`.
  - README release marker updated to `v1.4.5`.
  - PyPI badge updated to explicit `1.4.5` release marker.

## Operator Notes

- Manual Cloud Build submits now produce a valid image tag even outside Git-triggered contexts.
- Keep the Cloud Build service account scoped for:
  - `roles/artifactregistry.writer`
  - `roles/run.admin`
  - `roles/iam.serviceAccountUser`
  - `roles/logging.logWriter`
  - `roles/storage.admin`
