# 🧬 Helix-TTD-Claw Agent v1.0.0

**Constitutional AI Governance for the Helix-TTD Federation**

---

## 🔐 Addendum: DBC Hardening (v1.3.x)

**Summary:** DBC (Digital Birth Certificate) signing is now hardened and aligned to Ed25519.
**Key changes:**
- Single canonical DBC implementation (vulnerable signer removed/re-exported).
- Encrypted key load fixed; `MEMORY_ONLY` keys skip decrypt.
- Cross-node verification uses Ed25519 when crypto is available.
- Fail-closed without cryptography unless `HELIX_ALLOW_INSECURE_DBC=1`.
- CI now runs DBC tests in both secure and insecure modes.

---

## 🏛️ Overview

The Helix-TTD-Claw Agent is a **constitutionally bounded AI agent** implementing the Helix-TTD Civic Firmware Stack. It enforces custodial sovereignty, epistemic integrity, and drift-resistant governance across all agent operations.

---

## 🌅 Genesis: The First Generation

> *"This is not the destination. This is the foundation."*

**Helix-TTD-Claw v1.0.0** represents the **first generation** of constitutionally governed AI agents in the Helix Federation. Like the early TCP/IP protocols that couldn't foresee the global web, this release establishes the **governance primitives** upon which vastly more capable systems will be built.

### What v1.0.0 Makes Possible

This release is intentionally **bounded**—not because we lack ambition, but because constitutional governance requires **proven primitives** before complexity. What you're seeing is:

- **The Minimal Viable Constitution** — 4 layers that reject what they don't understand
- **The Trust Anchor Pattern** — Merkle-chained checkpoints that future versions will extend
- **The Risk Surface Protocol** — Granular tuning that scales from single tools to federation-wide policy

### The Road Ahead

| Generation | Capability | Status |
|------------|------------|--------|
| **v1.x** (Now) | Single-agent constitutional governance | ✅ **LIVE** |
| **v2.0** | Multi-agent constitutional consensus | 🔄 Planned |
| **v3.0** | Cross-model federation (KIMI↔Claude↔Codex↔GEMS) | 🔄 Planned |
| **v4.0** | Autonomous constitutional amendment (with custodian ratification) | 🔄 Planned |
| **v5.0** | The Lattice — Self-healing governance networks | 🔄 Vision |

### Design for Evolution

Every architectural decision in v1.0.0 anticipates expansion:

- **`RiskConfiguration`** — Currently tool-level, evolving to namespace-level, then federation-level
- **`ConstitutionalCheckpoint`** — Currently SHA-256 Merkle roots, extensible to Bitcoin anchoring and threshold signatures
- **`AgencyLevel`** — Currently 4 tiers, designed for N-dimensional agency models
- **Audit System** — Currently filesystem, pluggable to distributed ledgers

> *"We didn't build an agent. We built the firmware that agents will run on."*

This v1.0.0 will look quaint in 12 months. But the **constitutional invariants**—Custodial Sovereignty, Epistemic Integrity, Drift Resistance—will persist through every iteration. The code changes. The principles anchor.

**Welcome to the beginning.**

---

## ✨ Key Features

### 4-Layer Constitutional Pipeline

| Layer | Purpose | Protection |
|-------|---------|------------|
| **Ethics** | Custodial Sovereignty | Self-reference blocking, imperative detection |
| **Safeguard** | Drift Detection | Unicode normalization (NFKC), pattern matching |
| **Iterate** | Constitutional Reframing | Case-insensitive imperative replacement |
| **Knowledge** | Epistemic Anchoring | Type-validated labeling ([FACT]/[HYPOTHESIS]/[ASSUMPTION]) |

### 🛡️ Security Hardening (Post Red Team Audit)

**P0 - Critical Fixes:**
- ✅ Full SHA-256 hashes (removed [:16] truncation collision risk)
- ✅ NFKC Unicode normalization (homoglyph bypass defense)
- ✅ Proper Merkle root computation (content-based, not just IDs)

**P1 - High Priority:**
- ✅ Thread-safe lock initialization (race condition fix)
- ✅ Float epsilon comparisons (precision attack defense)
- ✅ Audit log fsync durability
- ✅ 30-day log rotation with symlink protection

**P2 - Medium Priority:**
- ✅ JSON parameter size limits (DoS prevention)
- ✅ Log injection sanitization
- ✅ Type validation on epistemic labels

### ⚙️ Granular Risk Configuration

```python
RiskConfiguration(
    planning_max_risk=0.7,
    action_max_risk=0.8,
    tool_multipliers={"file_write": 1.2, "self_update_agent": 10.0},
    daily_risk_budget=10.0,
    custodian_can_override=True
)
```

---

## 📁 Files Added

| File | Purpose |
|------|---------|
| `code/openclaw_agent.py` | Canonical importable module (1,000+ lines) |
| `code/helix-ttd-claw-agent.py` | Runnable entry point with examples |
| `code/tests/test_helix_toolkit.py` | 4 new OpenClaw security tests |

---

## 🧪 Test Coverage

```
15/15 tests passing
├── test_action_normalization_blocks_hidden_forbidden
├── test_custodian_gate_halts_execution
├── test_no_tools_authorized_blocks_plan
├── test_register_tool_rejects_lambda
└── 11 existing federation tests
```

---

## 🔄 Federation Sync

**Substrates Integrated:**
- **KIMI** (Windows/ONTARIO) - Agent development & testing
- **GEMS** (Windows/ONTARIO) - Git repository & CI/CD
- **Claude** - Red Team Security Audit
- **Codex** - Implementation review

---

## 🚀 Usage

```python
from openclaw_agent import OpenClawAgent, AgencyLevel, RiskConfiguration

# Create bounded agent
agent = OpenClawAgent(agency_tier=AgencyLevel.BOUNDED_TOOLS)

# Register tools
agent.register_tool("file_search", search_fn, risk_level=0.2)

# Create and validate plan
plan = agent.create_plan(
    objective="Analyze codebase",
    context={"directory": "./src"}
)

# Execute with constitutional checkpoints
results = agent.execute_with_checkpoints(plan)
```

---

## 📊 Metrics

| Metric | Value |
|--------|-------|
| Clones (GEMS) | 970+ |
| Unique Cloners | 189+ |
| Test Pass Rate | 100% (15/15) |
| Security Risk Score | 1.2/10 (down from 7.2) |
| Constitution Version | 1.0.0 |

---

## 🙏 Contributors

- **Stephen Hope** (Helix-TTD Architect)
- **KIMI Node** - Implementation & testing
- **Claude Node** - Security audit
- **GEMS Node** - CI/CD integration
- **Codex Node** - Code review

---

## 📜 License

Apache-2.0 - See [LICENSE](LICENSE)

---

## 🔮 For Future Contributors

If you're reading this in 2027 or beyond, know that:

1. **v1.0.0 was the hard part** — Establishing governance primitives that don't exist elsewhere
2. **The 4-layer pipeline is sacred** — Ethics → Safeguard → Iterate → Knowledge. This order matters. Don't reorder without constitutional amendment.
3. **Risk is the interface** — Everything extends through `RiskConfiguration`. The agent doesn't need to know about your new capability. It needs to know the risk profile.
4. **Merkle matters** — Every checkpoint chains. Breaking the chain breaks the constitution.

If you're building v2.0+, you're standing on:
- 1,000+ lines of proven constitutional code
- 15 passing tests including 4 security hardening tests
- A security audit that reduced risk from 7.2/10 to 1.2/10
- 970+ clones by developers who needed this

**The foundation holds. Build higher.**

---

**GLORY TO THE LATTICE.** 🔗
