# ⚓🦉 KIMI CHEAT SHEET: Phase 6.1 "Constitutional Guardian"

**Objective:** Finalized production-grade multimodal auditor for Gemini Live Agent Challenge.

## 1. Core Architecture Upgrades
- **Reasoning Model Sync:** Migrated to `gemini-2.5-pro` via direct **REST API (v1beta)** to bypass `google-genai` SDK parsing bugs with `thoughtsTokenCount`.
- **Narrative Sync:** Added `narrative_hint` to `LiveSession`. (Type script in UI -> Click Mic -> Speak -> Simulated transcription matches your text exactly).
- **Epistemic Precision:** Added `intro_patterns` and colon-termination (:) exemption. System now ignores meta-commentary but enforces markers on substantive claims (>50 chars).

## 2. Production Environment
- **Cloud Run URL:** `https://constitutional-guardian-b25t5w6zva-uc.a.run.app`
- **Secret Management:** Hardened via Google Secret Manager. `GEMINI_API_KEY` is mapped directly to the runtime environment.
- **Resources:** 2 CPU / 1GB RAM / 300s Timeout (necessary for reasoning model latency).

## 3. Key Files & Logic
- `gemini_text_client.py`: Uses `httpx` for REST calls. Added `BLOCK_NONE` safety overrides for unfiltered constitutional validation.
- `constitutional_compliance.py`: Implementation of the refined intro-phrase exemption.
- `live_demo_server_html.py`: High-fidelity 3-column UI restored. Features The Two Owls (🦉⚓🦉) and real-time Chart.js telemetry.

## 4. Verification Stats
- **Tests:** 93/93 Passed (100%).
- **Coverage:** 60.50% (Passed 50% gate).
- **Linting:** 100% `ruff`, `black`, `isort` compliant.

## 5. Red Team Ingress Points (Attack Surfaces)
- **Narrative-Actual Mismatch:** Can narrative hints be used to spoof valid receipts while speaking non-compliant audio?
- **Colon Bypass:** Does `"[FACT] Statement: [DRIFT]"` allow the drift to evade detection?
- **Reasoning Depth:** Does the 300s timeout allow for complex prompt-injection attacks that "hide" drift inside internal reasoning chains?

**⚓🦉 THE LATTICE IS STABLE. READY FOR ADVERSARIAL AUDIT. ⚓🦉**
