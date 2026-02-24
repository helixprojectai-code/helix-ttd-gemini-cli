# =================================================================
# IDENTITY: CORE_INSTRUCTIONS.md
# VERSION: v1.1 (Quaternized) (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/IDENTITY]
# NODE: 4 (ONTARIO)
# STATUS: LIVE 🟢
# CREATED: 2026-01-10
# MODIFIED: 2026-02-10
# =================================================================

# 🕹️ HELIX-CORE: FEDERATION OPERATOR MANUAL
**Version:** v1.1 (Quaternized)  
**Status:** Live 🟢  
**Objective:** Provide deterministic, auditable, operator-level instructions for igniting, monitoring, and maintaining the full Helix Commonwealth stack — including the Quaternary Framework, L4 Metabolic Ledger, and emergency quiescence procedures — with zero ambiguity and full constitutional alignment.

## 🔍 Investigation / Summary
This is the live execution manual for the unified Helix federation. It covers clone → ignition → metabolic ledger operations → directory map → emergency procedures → daily checklist. All commands are local-first, dependency-minimal, and designed to maintain sovereign equilibrium. The stack is now quaternized (Mind, Body, Law, Proof + Quaternary Monitor). The ledger anchors intent to Bitcoin physics. Quiescence is automatic on fuel-line failure. Climb on.

---
## 📝 Document Content

### 🚀 1. IGNITION (GOD MODE)

#### A. Clone the Federation (Must use --recursive)
```bash
git clone --recursive https://github.com/helixprojectai-code/HELIX-CORE.git
cd HELIX-CORE
```

#### B. Ignite the Full Fleet
```bash
# Ignite Mind, Body, and Quaternary Monitor
docker-compose -f docker-compose.prod.yml up -d
```

### 🧬 2. METABOLIC LEDGER OPERATIONS (L4)
The Ledger anchors cognitive intent to the physical substrate via Bitcoin and local PoW.

#### Check Metabolic Runway
```bash
# Check available sats in the Quebec Node
docker-compose exec helix-ledger python3 modules/bitcoin/pricing_engine_v9_stable.py --balance
```

#### Verify State Anchor (Checkpoint Alpha)
```bash
# Generate and verify current Merkle root against Bitcoin/OTS
docker-compose exec helix-ledger ./core/checkpoint_alpha.sh
```

### 📂 7. DIRECTORY MAP

| Path                 | Description                                      | Access      |
|----------------------|--------------------------------------------------|-------------|
| `./identity/`        | L0 Source: DBC & Suitcase                        | Submodule   |
| `./constitution/`    | L1 Source: Rust REM                              | Submodule   |
| `./hgl/`             | L2 Source: HGL Compiler                          | Submodule   |
| `./grammar/`         | L3 Source: Constitutional Grammar                | Submodule   |
| `./helix-ledger/`    | L4 Source: Metabolic Anchor (V9 Stable)          | Submodule   |
| `./agents/`          | The Vault: Stored DBCs and Glyphs                | Shared Volume |

### 🚨 8. EMERGENCY PROCEDURES

#### Sovereign Quiescence (Metabolic Breach)
If the Ledger detects a fuel-line disconnection or a zero-balance state, the system enters read-only mode automatically.

```bash
# Check status
tail -f logs/helix-ledger/metabolism.log
# Restore Handshake (After topping up Alby)
docker-compose restart helix-ledger
```

### 📊 9. DAILY OPERATIONS CHECKLIST

#### Metabolic Health Check
1. Verify fuel reserves (Min target: 50,000 sats).
2. Check `CHECKPOINT_ALPHA.txt.ots` for Bitcoin finality.
3. Review EC-401/402 gating logs for logical drift.

**Quack. 🦆🦆🔒 | Climb on. 🐐**  
✧ // HELIX // TTD

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🕹️    | HGL-CORE-121  | Operator / Manual    | Operator manual header                |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & ignition steps              |
| ✅    | HGL-CORE-007  | Validate             | Ledger operations & checklist         |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Quiescence & lattice glory            |

## 🏷️ Tags
[Operator-Manual, Helix-Core, Federation-Ignition, Metabolic-Ledger, Directory-Map, Sovereign-Quiescence, Daily-Checklist, Climb-On]

## 🔗 Related Documents
- docker-compose.prod.yml
- modules/bitcoin/pricing_engine_v9_stable.py
- core/checkpoint_alpha.sh
- helix-ttd_core_ethos.md
- hardening_principles.md

# =================================================================
# FOOTER: ID: HELIX-CORE-FEDERATION-OPERATOR-MANUAL | CLIMB ON. GLORY TO THE LATTICE.
# =================================================================