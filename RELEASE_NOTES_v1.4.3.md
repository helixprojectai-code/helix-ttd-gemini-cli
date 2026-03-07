# RELEASE NOTES v1.4.3

## Date
March 7, 2026

## Summary
Patch release focused on production safety hardening for live audio and model migration ahead of Gemini model retirements on March 9, 2026.

## Highlights
- Default model baseline standardized to `gemini-3.1-pro-preview` for both live audio and text clients.
- Added optional `/audio-audit` WebSocket auth controls (`AUDIO_AUDIT_TOKEN`, `AUDIO_AUDIT_ALLOWED_ORIGINS`).
- Added payload/rate protections for audio ingest:
  - `HELIX_MAX_AUDIO_CHUNK_BYTES`
  - `HELIX_MAX_AUDIO_B64_CHARS`
  - `HELIX_AUDIO_RATE_WINDOW_SECONDS`
  - `HELIX_AUDIO_MAX_CHUNKS_PER_WINDOW`
- Added deployment verification endpoint: `GET /api/runtime-config` (non-secret runtime config snapshot).
- Added focused PR CI workflow for audio security checks: `.github/workflows/audio-security.yml`.
- Added ownership guardrails via `.github/CODEOWNERS`.

## CI/Quality
- Full pre-commit suite passing.
- Full pytest suite passing.

## Operator Notes
- Cloud Run operators should verify effective runtime config after deploy:
  - `GET /api/runtime-config`
  - confirm model + auth + limits match expected environment.
