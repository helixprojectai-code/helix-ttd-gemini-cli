# RELEASE NOTES v1.4.4

Date: 2026-03-07

## Summary

v1.4.4 promotes the Live Audio pipeline from partial prototype behavior to production-ready turn processing.
This release focuses on reliable Gemini Live connectivity, deterministic turn handling, and constitutional output integrity for spoken interactions.

## Key Changes

- Live audio transport hardening
  - Migrated realtime audio send path to Gemini Live realtime media chunks (`audio/pcm;rate=16000`).
  - Added resilient Live connection config variants and API-version failover for native-audio models.
  - Prioritized audio-first Live config (`cfg=audio_output_tx`) for voice sessions.

- Voice turn lifecycle fixes
  - Added deterministic mic-stop turn finalization and stream-end signaling.
  - Fixed session lifecycle bug where subsequent mic attempts could fail after first successful turn.
  - Reset Live session state correctly after stream close to allow repeat audio turns.

- Transcript quality and governance
  - Coalesced partial streaming transcript fragments into single final turn output.
  - Added spoken epistemic lead normalization (`FACT ...` -> `[FACT] ...`).
  - Applied Live policy/system instruction so voice responses conform to constitutional markers and non-agency rules.

## Validation

- Ruff, Black, isort, mypy, Bandit, and pre-commit checks passing.
- Voice pipeline unit coverage expanded for:
  - realtime audio send path
  - turn-complete transcript coalescing
  - spoken marker normalization
  - post-stream session reset / reusability

## Upgrade Notes

- Package version bumped to `1.4.4` in project metadata and runtime surfaces.
- UI branding updated to `LIVE v1.4.4`.
- README and instructions updated for native-audio live model defaults.
