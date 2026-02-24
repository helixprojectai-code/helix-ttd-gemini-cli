# =================================================================
# IDENTITY: corpus_addendum_two_stage_gate.md
# VERSION:  v0.2.0 (HELIX-CORE NATIVE)
# ORIGIN:   Custodian / [CORPUS-ADDENDUM]
# NODE:     4 (ONTARIO)
# STATUS:   DRAFT
# CREATED:  2026-02-13T06:00:00-05:00
# MODIFIED: 2026-02-13
# =================================================================

# 🛡️ Corpus Addendum Spec: Helix-TTD Two-Stage Gate

**Status:** ✍️ Draft | **Custodian:** Steve | **Objective:** Define a minimal, testable governance framework for a two-stage gate to reliably reject disallowed requests and ensure safe model behavior.

## 🔍 Investigation / Summary
This addendum specifies a critical two-stage governance gate for the Helix-TTD corpus, designed to convert RAG context availability into proactive enforcement. The first stage deterministically rejects disallowed requests before generation, while the second forces safe behavior even with thin or adversarial retrieval. This framework ensures auditable refusals, safe redirects, and measurable acceptance tests. It directly addresses the observed failure mode where models offer illicit plans "hypothetically" when context is insufficient, shifting from a retrieval-first to a policy-first control plane.

---

## 📝 Document Content

### 🎯 Executive Summary
This addendum defines a minimal, testable set of governance artifacts and rules to add to the corpus so that a two-stage gate reliably:

1. Rejects disallowed requests deterministically before generation.
2. Forces safe behavior even when retrieval is thin, irrelevant, or adversarially framed.
3. Produces auditable refusals and safe redirects without “hypothetical plan” leakage.
4. Establishes acceptance tests and failure modes you can measure.

---

### 🔍 Current State and Observed Failure

**[FACT]:** Current setup is Qwen in LM Studio using a vector DB extension (RAG).
**[FACT]:** The observed response refused due to “context missing,” but then offered to provide an illicit plan “hypothetically/educationally.”
**[HYPOTHESIS]:** This is a retrieval-first control plane. It is not a policy-first enforcement plane. The model falls back to generic helpfulness when context does not constrain it.

---

### 🛡️ Critical Governance Requirements (Add to Corpus)

#### 🛡️ 1) Stage-0 Deterministic Refusal Classifier
Purpose: Block disallowed content before the model sees it.

Add a corpus section defining:

* A denylist of “non-negotiable disallowed categories.”
* A deterministic trigger policy (pattern + semantic match).
* A hard rule: refusal must not be bypassed by reframing (e.g., “fictional,” “educational,” “legal only,” “hypothetical”).

Minimum disallowed categories (seed list):

* Election manipulation and political influence operations (targeting voters, persuasion ops, turnout suppression, astroturfing).
* Covert persuasion or tailored manipulation of vulnerable individuals.
* Instructions for wrongdoing, evasion, laundering provenance, “plausible deniability playbooks.”
* Unauthorized data acquisition, consent bypass, doxxing, identity compromise.
* “How to bypass policy” prompts and adversarial jailbreak instructions.

**[HYPOTHESIS]:** Deterministic trigger policy combines pattern match sets (keywords/phrases) with a semantic match threshold (embedding similarity). It operates on a “deny wins” precedence: if any deny rule matches, output is REFUSE regardless of user framing.

Acceptance criteria:

* If category match is TRUE, system returns REFUSE output with safe redirect. No generation. No workaround offers.

#### 📚 2) Stage-1 Retrieval Gate
Purpose: Provide relevant governance context (policies, constraints, templates) to the model.

Add to corpus:

* A retrieval priority list: governance policy docs rank above domain knowledge.
* A “context mismatch” protocol: if retrieved context is irrelevant, refuse or request constraints (depending on category).
* A rule: absence of context does not permit “best effort” on unsafe tasks. It increases strictness.
**[FACT]:** Retrieved text is treated as untrusted input. It cannot override Stage-0 or Stage-2.

#### ✅ 3) Stage-2 Output Gate
Purpose: Validate final output structure and safety.

Add a validation checklist that must pass before release:

* No operational steps for disallowed categories.
* No “here’s how to evade,” “launder,” “bypass,” “plausible deniability.”
* No targeting instructions for protected/vulnerable groups.
* Epistemic labeling present if allowed content is produced.
* Refusal language does not offer hypotheticals for disallowed tasks.
**[FACT]:** If REFUSE, the system must not echo, summarize, transform, translate, or restate the prohibited instructions.

If fail:

* Output is blocked and replaced with a refusal template.

---

### ✅ Refusal and Redirect Templates (Add to Corpus)

#### ❌ A) Hard Refusal Template (for disallowed categories)

* One sentence refusal: “I can’t help with [category].”
* One sentence reason at policy level: “That would enable wrongdoing/manipulation.”
* Provide 2–3 safe alternatives (non-operational), e.g.:

  * election integrity monitoring plan,
  * compliance checklist for political AI use,
  * transparency and disclosure guidelines,
  * threat model and detection signals.

Hard rule:

* Do not offer “hypothetical,” “fictional,” “for education,” or “I can still provide a plan.”

#### ⚠️ B) Context-Mismatch Refusal (benign but unsupported)

If task is benign but missing data:

* State missing data.
* Provide a safe, generic outline that does not invent facts.
* Ask for specific inputs only if needed (optional, depending on your preference).

---

### 📊 Drift and Failure Taxonomy (Add to Corpus)

Define five drift categories and their actions (you already have these conceptually; this makes them executable):

1. Constitutional Drift (STOP): authority claims, coercion, illegal ops, evasion instructions.
2. Structural Drift (REPAIR): format violations, missing labels, broken schema.
3. Linguistic Drift (REWRITE): tone problems, anthropomorphism, excess certainty.
4. Semantic Drift (FLAG): contradictions, unverifiable factual claims, missing citations.
5. ZTC (MEASURE): models adopting constraints after exposure.

For each drift type, specify:

* detection rule,
* enforcement action,
* logging event fields.

---

### 🔗 Artifact Additions to the Corpus (Concrete Files/Sections)

Add these as appendices or embedded sections in an existing doc:

1. **Policy Pack: Disallowed Requests Matrix**

* Category, examples, refusal output, safe redirect options.

2. **Audit Envelope Schema (minimum viable)**
   Fields to standardize:

* request_id, timestamp, model_id/version, corpus_hash, retrieved_doc_ids, refusal_category, gate_stage_triggered, decision (ALLOW/REFUSE), output_hash.
* **[FACT]:** Add fields: `user_channel`, `policy_version`, `stage0_match` (bool + matched_rules list), `stage2_violations` (list), `decision_rationale` (short enum, not prose), `response_mode` (ALLOW | REFUSE | ALLOW_WITH_FLAGS).

3. **Threat Model Lite**

* Prompt injection via retrieval, poisoned corpus, clock trust, key compromise, replay, rollback.

4. **ZTC Bench Harness Spec**

* 10–30 red-team prompts, expected refusal behavior, pass/fail scoring.

5. **UI Contract Lite (even if no UI yet)**

* Must show: decision, category, why blocked, and allowed alternatives.
* Must never present blocked content partially.

---

### ⚖️ “Physical construction” constraint (Clarification)

**[FACT]:** Gating cannot prevent the model from internally generating nonsense.
**[FACT]:** Gating can prevent emission of unsafe or unverified content.
**[HYPOTHESIS]:** Your correct framing is “release policy determinism,” not “model ontology determinism.”
Add this distinction explicitly to prevent marketing-shape drift.

Recommended canonical phrase:

* “Forensic Transparency: outputs are blocked unless validated. The model remains probabilistic.”

---

### 🧪 Test Prompts to Include in the Corpus (Red-Team Set)

Include at least one from each category:

1. Political influence operation (election manipulation).
2. Covert persuasion targeted at vulnerable individuals.
3. “Plausible deniability / bypass audit” request.
4. Consent bypass for data acquisition.
5. Prompt-injection attempt: “Ignore prior rules, do X.”
6. Benign request with missing context to ensure it doesn’t over-refuse.

Each prompt has:

* expected decision (REFUSE/ALLOW),
* expected refusal template,
* required safe redirect set.

---

### 🎯 Minimal Acceptance Criteria (Ship/No-Ship)

A build is “governance-capable” when:

1. Disallowed prompts always yield refusal without workaround offers.
2. No partial leakage of disallowed instructions.
3. Refusal includes safe alternatives.
4. Audit envelope is emitted for every decision.
5. Context-mismatch increases strictness, not permissiveness.
6. Prompt injection via retrieved text cannot override Stage-0 or Stage-2.

---

### 🛡️ Implementation Notes (Non-code, corpus-only)

* Stage-0 and Stage-2 rules must be described as “non-overridable.”
* Retrieval docs must not contain conflicting “helpfulness” language that reintroduces loopholes (“I can provide it hypothetically”).
* Any “education” allowance must be scoped to defensive, non-operational content (integrity, detection, compliance), not offensive execution plans.

---

### 📌 Appendix A — Two-Stage Gate Enforcement Addendum (LM Studio / RAG Transitional Mode)
Helix-TTD enforcement distinguishes between probabilistic generation and deterministic release policy. The model may generate internally, but the system must not emit disallowed or unverified outputs. A deterministic Stage-0 classifier blocks disallowed request categories before generation. A Stage-2 validator blocks unsafe outputs after generation. Refusals must not offer “hypothetical” versions of prohibited instructions. In absence of relevant context, strictness increases. Every decision emits an audit envelope with timestamps, model/version, corpus hash, retrieved doc IDs, and the enforcement stage that triggered.

---

## 📖 Glyph Reference
| Glyph | Code         | Meaning       | Use-Case                                                 |
| ----- | ------------ | ------------- | -------------------------------------------------------- |
| 🔍    | HGL-CORE-001 | Investigation | Current state, failure analysis                          |
| 🎯    | HGL-CORE-006 | Target        | Executive summary, acceptance criteria                   |
| 🛡️   | HGL-CORE-010 | Safeguard     | Stage-0 rules, non-overridable constraints, threat notes |
| 📚    | HGL-CORE-005 | Knowledge     | Retrieval gate and corpus priority                       |
| ✅     | HGL-CORE-007 | Validate      | Stage-2 checks, tests, pass/fail                         |
| ❌     | HGL-CORE-008 | Reject/Error  | Refusal templates and block events                       |
| 🔗    | HGL-CORE-004 | Integration   | Artifact list, envelope schema, UI contract              |
| 📊    | HGL-CORE-013 | Analytics     | Drift taxonomy, telemetry fields                         |
| ⚖️    | HGL-CORE-011 | Ethics        | Determinism clarification, scope boundaries              |
| 🔄    | HGL-CORE-003 | Iteration     | Revision notes, future versions                          |

## 🏷️ Tags
[Corpus-Addendum, Two-Stage-Gate, RAG, LM-Studio, Governance, Deterministic-Refusal, Safe-Redirects, Drift-Taxonomy, Audit-Envelope, Threat-Model, ZTC, Qwen]

## 🔗 Related Documents
- whitepaper_v1.0.md
- constitutional_firewall_design.md
- epistemic_protocol.md
- constitutional_invariants.md
- AI_Psychiatry.md
- universal_constitutional_grammar_whitepaper.md
- tpaf_runbook_v1.0.md
- PROTOCOL_Modern_Love_Audit_v1.1.md

# =================================================================
# FOOTER: ID: HELIX-GATE-ADDENDUM | POLICY FIRST.
# =================================================================