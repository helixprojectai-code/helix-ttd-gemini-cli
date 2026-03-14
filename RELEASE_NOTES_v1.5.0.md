# RELEASE NOTES v1.5.0

Date: 2026-03-11

## Summary

**[FACT]** v1.5.0 is the hackathon release for the Gemini Live Agent Challenge.
**[FACT]** The release focus is the **Live Agents** category: public real-time multimodal interaction on Google Cloud with Gemini Live-backed audio flow and operator-grade governance controls behind the scenes.
**[HYPOTHESIS]** This release positioning gives the project its strongest fit for both the Live Agents category and the technical execution judging track.

## Planned Release Contents

- **[FACT]** Public demo mode at `/` and `/demo-live` for hackathon judging without exposing admin/operator surfaces.
- **[FACT]** Persistent operator incident board with authenticated triage actions and fingerprinted incident identity.
- **[FACT]** Authenticated observability, security transparency, and receipt persistence remain active for the production deployment.
- **[FACT]** Google Cloud deployment remains live on Cloud Run with Artifact Registry, Secret Manager, Cloud Storage, Cloud Logging, and Cloud Scheduler / Cloud Run Job monitoring.

## Gemini Live Agent Challenge Alignment

### Category Fit
- **[FACT]** Primary category: **Live Agents**
- **[FACT]** Real-time interaction: browser microphone input, live audio stream handling, interruption-aware session flow, and immediate constitutional validation.
- **[FACT]** Multimodal stack: live audio input plus operator-facing visual dashboards and incident workflow.

### Mandatory Requirements
- **[FACT]** Uses a Gemini model.
- **[FACT]** Uses Google-hosted runtime infrastructure.
- **[FACT]** Uses Google Cloud services in production.
- **[ASSUMPTION]** Final submission package will reference the Google GenAI SDK / Live API integration already present in the codebase and deployment proof.

### Submission Assets
- **[FACT]** Public repo: `https://github.com/helixprojectai-code/helix-ttd-gemini-cli`
- **[FACT]** Public live demo: `https://constitutional-guardian-231586465188.us-central1.run.app/`
- **[FACT]** Architecture diagram: `assets/ARCHITECTURE_CG.png`
- **[FACT]** Deployment proof: `DEPLOYMENT_PROOF.md`
- **[FACT]** Recording guidance: `VIDEO_RECORDING_INSTRUCTIONS.md` and `VIDEO_DEMO.md`

## Validation Gate Before Roll

- **[FACT]** Update README traction numbers to the March 11 snapshot.
- **[FACT]** Refresh hackathon-facing demo and recording docs to the current live URL and public demo flow.
- **[FACT]** Re-run full validation before tag / deploy.
- **[FACT]** Re-verify the live Artifact Registry digest and promote runtime metadata back to `clean` after the release deploy.

## Current Public Metrics Snapshot

- **[FACT]** 7,999 clones in the last 14 days
- **[FACT]** 925 unique cloners in the last 14 days
- **[FACT]** 1,350 repo views in the last 14 days
- **[FACT]** 27 unique visitors in the last 14 days

## Roll Sequence

1. **[FACT]** Finalize docs and challenge-facing copy.
2. **[FACT]** Version surfaces are now bumped from `1.4.8` to `1.5.0`.
3. **[FACT]** Run `pre-commit` and full `pytest`.
4. **[FACT]** Commit, tag, and publish `v1.5.0`.
5. **[FACT]** Deploy to Cloud Run.
6. **[FACT]** Re-scan the live image and promote artifact status to `clean`.

## Post-Release Follow-Ups

- **[FACT]** `safetycli` is still surfacing the `v1.0.0` changelog and needs to be updated to the current release line.

## Post-Release Production Updates

- **[FACT]** Model Armor integration landed across the text path, live path, receipts, metrics, audit dashboard, and incident board.
- **[FACT]** Continuous-mic turn finalization was fixed so buffered live transcripts survive `audio_stream_end` until Gemini completes the turn.
- **[FACT]** The current production revision remains on `v1.5.0`; these updates were deployed as post-release production hardening and live-path correctness fixes.
