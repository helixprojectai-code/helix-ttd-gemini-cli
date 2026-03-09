# RELEASE NOTES v1.4.3

## Date
March 7, 2026

## Summary
Production patch focused on reliable live voice pipeline behavior before transcript quality optimization.

## Highlights
- Standardized default model baseline to `gemini-3.1-pro-preview` for live audio and text paths.
- Added optional `/audio-audit` WebSocket auth controls (`AUDIO_AUDIT_TOKEN`, `AUDIO_AUDIT_ALLOWED_ORIGINS`).
- Added payload/rate protections for audio ingest:
  - `HELIX_MAX_AUDIO_CHUNK_BYTES`
  - `HELIX_MAX_AUDIO_B64_CHARS`
  - `HELIX_AUDIO_RATE_WINDOW_SECONDS`
  - `HELIX_AUDIO_MAX_CHUNKS_PER_WINDOW`
- Added deployment verification endpoint: `GET /api/runtime-config`.
- Added focused PR CI workflow for audio checks: `.github/workflows/audio-security.yml`.
- Added ownership guardrails via `.github/CODEOWNERS`.

## Voice Pipe Stabilization
- Disabled random transcript fallback by default.
- Added explicit `NO_TRANSCRIPT_AVAILABLE` flow when Gemini Live is unavailable and simulation is off.
- Added deterministic simulation transcript only when `HELIX_AUDIO_SIMULATION` is explicitly enabled.
- Added turn-boundary telemetry (`turn_reason`, chunk rate, silence streak) and connection lifecycle stats.
- Added WebSocket voice-pipe metrics (`ws_connect_count`, `ws_disconnect_count`, `turn_boundary_count`).

## CI/Quality
- Full `pre-commit --all-files` passing.
- Full pytest suite passing (`168 passed`).

## Operator Notes
- Verify post-deploy runtime state at `GET /api/runtime-config`.
- Confirm expected values for model, auth, and audio limits in production.
