# Roadmap to v2.0 - Constitutional AI Governance Platform

Status: Draft for execution
Owner: Helix Core / Custodian

## 1) Scope and Constraints

This roadmap is grounded in current repo posture and ratified docs:
- `docs/v1.3.0_Roadmap-Dr_Ryan_Critique.md` (hardening levers)
- `docs/threat_model_governance_v0.1.md` (residual risks)
- `docs/CLOUD_USAGE_AND_MIGRATION_PLAN.md` (local-first migration)
- `docs/UI_SPEC_DASHBOARD.md` (audit/ops transparency UX)
- `docs/sre_manual_v1.md` (liveness + hotfix SLOs)
- `docs/STATE_OF_THE_REEF_2026-02-23.md` (expansion recommendations)

Non-negotiables:
- Human custodial sovereignty and non-agency invariants remain binding.
- Cloud remains optional scaffolding; architecture must stay self-hostable.
- Security posture and forensic auditability are release gates, not stretch goals.

Explicit de-scope:
- Video processing is removed from the roadmap.

## 2) Strategic Outcome for v2.0

By v2.0, Helix operates as constitutional governance infrastructure:
- Multi-node quorum validation for high-risk outputs/actions.
- Cryptographically verifiable receipt chain and cross-model attestation.
- Enterprise-grade tenancy, RBAC, audit surfaces, and policy operations.
- Local-first deploy path with optional cloud acceleration.

## 3) Milestones

## v1.5 - Enterprise Hardening

Objectives:
- Establish enterprise security and operational controls required for paid adoption.

Features:
- Multi-tenant isolation + RBAC enforcement (org/project/user scopes).
- Audit Trail Dashboard MVP (drift, interventions, receipt explorer, export).
- Vault-backed key management (replace env-only secret assumptions for runtime crypto materials).
- SLA instrumentation (latency/error/drift SLO dashboards + alerts).
- SOC 2 Type II readiness baseline (controls mapping, evidence collection path).

Acceptance gates:
- P0/P1 security findings: 0 open in release branch.
- Tenant boundary tests: 100% pass on cross-tenant isolation suite.
- Dashboard export: signed audit bundle reproducible from receipts.
- Secrets: no plaintext key material in app config/logs.

## v1.6 - Federation Consensus

Objectives:
- Move federation from parallel opinion to enforceable consensus on sensitive paths.

Features:
- Quorum policy engine (advisory quorum and blocking quorum modes).
- Byzantine-tolerant decision strategy for minority compromise/failure.
- Cross-model attestation packets (signed verdict + evidence references).
- Federation receipt chaining (Merkle chain across nodes, not single-node only).

Acceptance gates:
- Quorum simulation suite: pass under node timeout, disagreement, and malicious-node scenarios.
- High-risk actions require quorum approval in blocking mode.
- End-to-end attestation packet verifiable from stored receipts.

## v1.7 - Multi-Modal Expansion

Objectives:
- Extend constitutional controls beyond text without adding video complexity.

Features:
- Vision input governance (hallucination/uncertainty guardrails on image-grounded claims).
- Code execution governance (sandbox policy, tool scope limits, escape prevention).
- Tool-use intent gates (pre-execution constitutional validation for external actions).
- Voice pipeline maturation (turning, transcript integrity, spoken-intent validation hardening).

Acceptance gates:
- Vision eval benchmark with explicit uncertainty calibration thresholds.
- Tool execution blocked on policy violations with signed denial receipts.
- Sandbox red-team suite: zero critical escapes.

## v1.8 - Constitutional Operations

Objectives:
- Formalize controlled constitutional evolution with strong incident controls.

Features:
- Drift telemetry v2 (trajectory-level, not only event-level).
- Versioned constitution lifecycle (proposal, review, migration receipts).
- Amendment governance workflow (human-supervised, policy-scoped voting/evidence).
- Emergency freeze controls for active incidents.

Acceptance gates:
- Constitution migration reproducible and reversible with receipt trail.
- Freeze mechanism tested in game-day incident drills.
- No unreviewed constitution changes accepted by runtime.

## v1.9 - Developer Ecosystem

Objectives:
- Make Helix easy to integrate while preserving governance guarantees.

Features:
- SDKs: Python, JavaScript/TypeScript, Go.
- Plugin validator framework (signed plugin metadata + compatibility checks).
- Framework integrations (LangChain/LlamaIndex middleware adapters).
- Observability exports (OpenTelemetry + Prometheus + Datadog conventions).

Acceptance gates:
- SDK quickstarts deploy and pass reference governance tests.
- Plugin compatibility matrix published and CI-validated.
- Observability dashboards operational from default exports.

## v2.0 - The Lattice

Objectives:
- Constitutional governance as durable infrastructure.

Features:
- Proof-of-Epistemics (receipt-weighted verification primitives).
- L1 anchoring strategy for constitutional state/receipt checkpoints.
- Global constitutional dispute workflow (federated court process).
- Governance framework for constitutional change at ecosystem scale.

Acceptance gates:
- Independent verifier can validate constitutional state from published artifacts.
- Dispute workflow has deterministic outcomes and complete auditability.
- Reference deployment supports edge-node federation + core lattice verification.

## 4) Cross-Cutting Tracks (All Milestones)

Security and Compliance:
- Continuous threat-model refresh and red-team cycles.
- Control evidence collection for SOC2/enterprise procurement.

Reliability:
- SRE objectives from `docs/sre_manual_v1.md` integrated into release criteria.
- Incident drills (quarantine, rollback, key compromise, region outage).

Cloud-to-Local Sovereignty:
- Keep local-first runtime path parity with cloud path.
- No feature may require cloud-only execution to be considered GA.

## 5) Immediate Execution Priorities

Priority A: Vault Integration (v1.5 blocker)
- Deliverables: vault adapter, key rotation runbook, secret usage audit.
- Exit criteria: env-only key dependency removed for protected materials.

Priority B: Audit Dashboard MVP (v1.5 blocker)
- Deliverables: drift timeline, intervention table, receipt explorer, signed export.
- Exit criteria: compliance reviewer can reconstruct one incident end-to-end.

Priority C: Quorum Consensus v1 (v1.6 foundation)
- Deliverables: policy engine, quorum modes, attestation packet format.
- Exit criteria: high-risk path blocked without quorum in staging.

## 6) Release Governance

For each release:
- Required: release notes, threat model delta, migration notes, rollback plan.
- Required: passing CI + security scans + reproducible artifact hashes.
- Required: production smoke validation and runtime config attestation.

---

Advisory conclusion:
- This plan keeps enterprise and safety work in front, removes video scope, and preserves the path to v2.0 without sacrificing current deployment velocity.
