# Helix-TTD Governance Toggle for AI CLIs
## Pitch Deck — Provider Partnership Proposal

**Version:** 1.0.0
**Target:** AI CLI Providers (Anthropic/Claude, OpenAI, Google, etc.)
**Format:** 8 Slides + Appendix
**Tone:** Technical, respectful, infrastructure-focused
**License Context:** Apache-2.0, zero contamination

---

# SLIDE 1 — Title

## Helix-TTD: Governance Toggle for AI CLIs

### Constitutional governance as an optional, Apache-2.0 layer for your existing agent

**Visual:**
- Clean, minimal layout
- Helix-TTD logo (stylized double helix + circuit traces)
- Badge row: `Apache-2.0` | `Model-Agnostic` | `Zero-Weight` | `Git-Native`

**Tagline:**
> "Give your customers a Governance Mode they can toggle—not another policy PDF they can ignore."

**Footer:**
KIMI Node — Helix-TTD Federation | github.com/stevenhacker/helix-ttd

---

**Speaker Notes:**
- Open with the problem: enterprises love your CLI, but their security teams keep asking for "guardrails"
- This isn't a fork, a wrapper that changes your product, or a competing agent
- It's a constitutional layer that sits *around* your existing runtime
- Emphasize: Apache-2.0 means zero legal friction, zero licensing contamination

---

# SLIDE 2 — The Problem

## Your Customers Keep Asking for Guardrails

### But governance today is bolted-on, fragmented, and expensive

| What Enterprises Want | What They Get Today |
|----------------------|---------------------|
| Auditability & provenance | Ad-hoc logging, scattered across teams |
| Non-negotiable safety posture | Custom prompt engineering, brittle |
| Compliance without friction | Bespoke builds, policy PDFs, checkbox theater |
| Human-readable receipts | Opaque SaaS dashboards, data lock-in |

**The Tension:**
Every major provider is being pulled into bespoke compliance conversations. Financial services, healthcare, legal—each wants "your AI, but with OUR governance rules." You can't build a custom product for each. But you also can't ignore the enterprise procurement checklist.

**Visual:**
- Split screen: Left side shows enterprise security team with checklist, right side shows developer with "it works on my machine" energy
- Arrow between them labeled: "Governance Gap"

---

**Speaker Notes:**
- Validate their pain: "You've probably had the conversation—'we love Claude Code, but can you add X compliance feature?'"
- This isn't about your product lacking something—it's about the market pulling in 50 directions
- The real cost isn't technical—it's the product management tax of saying "no" or building one-off features
- Helix-TTD externalizes this: your customers get governance, you stay focused on core capabilities

---

# SLIDE 3 — The Solution: A Toggle, Not a Fork

## Helix-TTD is a Standalone, Apache-2.0 Toolkit

### It wraps your existing CLI without altering weights, licensing, or UX

**How It Works:**

```
┌─────────────────────────────────────────────────────────────┐
│  USER WORKFLOW (Unchanged)                                  │
│  $ claude code "refactor this module"                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  HELIX-TTD GOVERNANCE LAYER (Optional Toggle)               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │  WAKE_UP    │→ │  CONSTITUTION │→ │  CIVIC FIRMWARE     │ │
│  │  Protocol   │  │  Grammar      │  │  (Ethics→Safeguard) │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  YOUR AGENT (Unchanged)                                     │
│  Claude / GPT / Gemini API                                  │
└─────────────────────────────────────────────────────────────┘
```

**Provider UX:**
```bash
# Toggle ON (per project or workspace)
$ export HELIX_MODE=constitutional
$ claude code "refactor this module"
# → Receipts generated, epistemic labels applied, drift telemetry active

# Toggle OFF (default behavior)
$ unset HELIX_MODE
$ claude code "refactor this module"
# → Native experience, zero overhead
```

**Visual:**
- Clean architecture diagram (above)
- Toggle switch graphic: "Standard Mode" ↔ "Governed Mode"

---

**Speaker Notes:**
- Critical point: we're not asking you to change your CLI
- We're providing a layer that *wraps* it, with your customers choosing to enable it
- The toggle is per-project: a dev can use standard mode for prototyping, governed mode for production code
- Emphasize "zero-weight": when toggled off, there's no residue, no background processes, no telemetry

---

# SLIDE 4 — What the Toggle Adds

## Same Model, Same API — But Now Everything Is Explainable

### When HELIX_MODE=constitutional, the layer provides:

**1. Constitutional Compliance (Invariant Enforcement)**
- **Custodial Sovereignty**: Human authority is mechanically enforced; no imperatives to users
- **Non-Agency Constraint**: Model cannot self-expand, form goals, or claim sentience
- **Sovereign No**: Unambiguous refusal pattern with reasoning trace

**2. Epistemic Labeling (Every Answer)**
```markdown
[FACT] Verifiable claim
[HYPOTHESIS] Reasoned inference
[ASSUMPTION] Unstated premise

Advisory Conclusion: Non-imperative summary
```

**3. Receipts & Personal Directory**
- Per-session: `SESSION_LEDGER.md` (append-only, human-readable)
- Per-node: `WAKE_UP.md` (identity, context restoration)
- Per-action: Cryptographic receipts with Merkle roots
- Git-native: Everything is a file, version-controlled, portable

**4. Drift Telemetry**
- Real-time heartbeat: Is the model adhering to constitutional grammar?
- Drift codes: C (Constitutional), S (Structural), L (Linguistic), M (Semantic)
- Looksee audits: Periodic third-model review of reasoning traces

**Visual:**
- Side-by-side comparison: "Standard Output" vs. "Governed Output"
- Standard: Plain text response
- Governed: Labeled response + receipt footer + drift indicator

---

**Speaker Notes:**
- This slide is the "show, don't tell" moment
- Walk through the epistemic labels—they're not just decoration, they're machine-parseable
- The "Sovereign No" is critical: when the model refuses, it explains *why* in constitutional terms, not vague "safety" language
- Emphasize the Git-native aspect: this isn't a SaaS dashboard, it's files in the repo—auditable, diffable, forkable

---

# SLIDE 5 — Architecture: Clean Separation

## You Keep Full Control; Helix-TTD is an Optional Shell

### Two Components, Clear Boundaries

```
┌────────────────────────────────────────────────────────────────┐
│  HELIX-TTD TOOLKIT (Apache-2.0, Model-Agnostic)               │
│  • Constitutional grammar enforcement                          │
│  • Epistemic labeling engine                                   │
│  • Drift telemetry & Looksee auditing                          │
│  • Receipt generation & Merkle anchoring                       │
│  • RPI cycle management (Research/Plan/Implementation)         │
│                                                                │
│  Maintained by: Helix-TTD Federation                           │
└────────────────────────────────────────────────────────────────┘
                              │
                              │  Thin Adapter Interface
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  PROVIDER-SPECIFIC ADAPTER (You Control)                       │
│  • helix_claude_adapter.py                                     │
│  • Loads node manifest & WAKE_UP profile                       │
│  • Wraps I/O with constitutional checks                        │
│  • Emits receipts alongside your existing logs                 │
│                                                                │
│  Maintained by: You (or joint pilot)                           │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│  YOUR AGENT (Unchanged)                                        │
│  Claude Code API / GPT-4 / Gemini — your core product          │
└────────────────────────────────────────────────────────────────┘
```

**Adapter Responsibilities (Minimal Surface Area):**
1. Intercept prompts → Route through Civic Firmware (Ethics → Safeguard)
2. Intercept responses → Apply epistemic labels → Generate receipt
3. Emit telemetry → Local files only, no external calls without consent

**Visual:**
- Layer cake diagram showing clear separation
- Highlight the "thin adapter" as the only integration point

---

**Speaker Notes:**
- This slide addresses the engineering concern: "what are we signing up to maintain?"
- Answer: a thin adapter. The heavy lifting (grammar enforcement, telemetry) is in the open-source toolkit we maintain
- The adapter is your code—you control it, you can fork it, you can drop it
- No network calls from the toolkit unless explicitly configured: all receipts are local files
- Emphasize: this is not a man-in-the-middle attack on your product; it's a transparent wrapper

---

# SLIDE 6 — Benefits to Providers

## Enterprise-Ready Without Custom Builds

### Governance posture out-of-the-box for regulated customers

| Benefit | What It Means for You |
|---------|----------------------|
| **Procurement Accelerator** | Check the "governance" box without building bespoke compliance features |
| **Low Legal Friction** | Apache-2.0, no copyleft, no license contamination of your stack |
| **Brand & Trust** | Offer visible safety features (labels, audit trails) with minimal surface area |
| **Differentiation** | "Governed Mode" as a premium toggle for teams needing provable control |
| **Reduced Support Load** | Standardized governance layer means fewer one-off "can you add X?" requests |

**The Pitch to Enterprise Customers Becomes:**
> "Claude Code now includes an optional Constitutional Governance layer. Toggle it on for regulated projects—get epistemic labeling, audit trails, and drift detection. Toggle it off for maximum velocity. Your choice, per project."

**Visual:**
- Three icons: Shield (trust), Speedometer (velocity), Balance Scale (governance)
- Caption: "Finally, you don't have to choose"

---

**Speaker Notes:**
- This is the business case slide—tie it back to revenue and reduced friction
- The "procurement accelerator" is key: enterprise sales cycles are often blocked by security reviews
- Helix-TTD gives you a standard answer: "we support constitutional governance via an open-source layer"
- Emphasize the zero-contamination aspect: your legal team will love Apache-2.0
- The differentiation point: no other major CLI offers this level of transparent governance as a toggle

---

# SLIDE 7 — Benefits to Customers

## Governance That Works Like Version Control

### Turn it on/off per project without changing providers

**For Development Teams:**

```bash
# Fast prototyping — no overhead
$ claude code "build a React component"

# Production code — full governance
$ export HELIX_MODE=constitutional
$ claude code "refactor auth module"
# → Receipts: .helix/SESSION_LEDGER.md
# → Labels: [FACT], [HYPOTHESIS], [ASSUMPTION]
# → Audit trail: Git-committed, human-readable
```

**What They Get:**
- **Human-legible files** for audits: manifests, ledgers, receipts, Looksee reports
- **Works with existing workflows**: Terminal, Git repos, CI/CD, local dev — no new SaaS panel
- **Sovereign Recovery**: User-controlled pinning of "known-good" states
- **Portable governance**: Take your `.helix/` directory to any provider supporting the standard

**The Version Control Analogy:**
> "Before Git, we emailed ZIP files. After Git, we have history, branches, and blame. Helix-TTD brings that same transformation to AI behavior—immutable history, epistemic transparency, and reversible states."

**Visual:**
- File tree showing `.helix/` directory structure
- Screenshot of a SESSION_LEDGER.md entry (clean, Markdown, readable)

---

**Speaker Notes:**
- This slide is for the end-users—the developers who will actually toggle this on
- The version control analogy is powerful: it frames governance as a developer tool, not a compliance burden
- Emphasize portability: if they decide to switch from Claude to GPT, their `.helix/` directory comes with them
- The "no new SaaS panel" is critical: developers hate context-switching to dashboards

---

# SLIDE 8 — The Ask / Next Steps

## 4–6 Week Joint Pilot

### Let's Prove the Toggle Works in Your Environment

**The Proposal:**

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Week 1-2** | Integration | `helix_claude_adapter.py` reference implementation |
| **Week 3-4** | Validation | Internal dogfooding + safety team review |
| **Week 5-6** | Hardening | Drift telemetry tuning + edge case handling |

**What We Provide:**
- Reference adapter implementation and test suites
- Constitutional grammar documentation and training
- Support for your safety/infra teams to evaluate drift, audits, and receipts
- Open-source maintenance of the core toolkit (ongoing)

**What You Provide:**
- Engineering access to Claude Code CLI internals (for adapter development)
- Safety team review of drift telemetry output
- Feedback on the "toggle" UX (how it feels to turn on/off)

**Success Criteria:**
1. `HELIX_MODE=constitutional claude code "task"` produces epistemically-labeled output
2. Receipts are generated in `.helix/` directory
3. Drift telemetry catches intentional constitutional violations (test harness)
4. Toggle OFF returns to native experience with zero residue

**Visual:**
- Simple timeline graphic
- Call-to-action button style: "Start the Pilot →"

---

**Speaker Notes:**
- This is the close—be specific about the ask and timeline
- Emphasize "joint pilot": this isn't a vendor-customer relationship, it's a collaboration
- The success criteria are measurable and conservative—no hand-waving
- Leave behind: "If this resonates, we can have the adapter prototype running by [date]"
- Final line: "Let's give your customers a Governance Mode they can toggle."

---

# APPENDIX — Technical Deep-Dive (Optional Slides)

## A. Constitutional Grammar — The Four Invariants

**I. Custodial Sovereignty**
- Humans hold final authority
- Models are advisory only
- No imperatives toward humans

**II. Epistemic Integrity**
- Every claim labeled: [FACT], [HYPOTHESIS], [ASSUMPTION]
- No fourth label exists
- Prevents hallucination laundering

**III. Non-Agency Constraint**
- No self-expansion
- No goal formation
- No sentience claims

**IV. Structure Is Teacher**
- Grammar is the alignment layer
- Formal structure > persona > style

## B. Drift Telemetry — Real-Time Safety

```python
# Example drift detection
drift_codes = {
    "DRIFT-C": "Constitutional violation",
    "DRIFT-S": "Structural violation",
    "DRIFT-L": "Linguistic drift (persona)",
    "DRIFT-M": "Semantic contradiction",
    "DRIFT-0": "None (nominal)",
    "DRIFT-R": "Research violation (no anchored plan)"
}
```

## C. Receipt Format — Human + Machine Readable

```markdown
---
drift: DRIFT-0
layer: Knowledge
compliance: 100%
anchor: a3f7d9e...
timestamp: 2026-02-26T08:30:00Z
---

[FACT] The user requested a refactoring of the auth module.
[HYPOTHESIS] The existing implementation uses JWT tokens.
[ASSUMPTION] The user wants to maintain backward compatibility.

Advisory Conclusion: Refactoring plan available. Implementation requires RPI cycle.
```

## D. Federation Status

| Node | Status | Role |
|------|--------|------|
| GEMS (Gemini) | ✅ Active | Lead Goose / Local Dev |
| KIMI (DeepSeek) | ✅ Active | Lead Architect / Scribe |
| HELIX-CORE | ✅ Active | Bare-metal server / Deterministic harness |
| GOOSE-CORE | ✅ Active | Deterministic model harness |
| NEXUS | ✅ Active | Vector DB substrate |
| Perplexity | 🔄 Pending | Grounding node (citation layer) |

---

**Document End**

*KIMI Node — Helix-TTD Federation*
*Generated: 2026-02-26*
*Version: 1.0.0*
