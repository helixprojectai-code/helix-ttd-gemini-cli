# =================================================================
# IDENTITY: QUICK_REFERENCE_Q_MARKERS.md
# VERSION: v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/PROTOCOLS/QUIESCENCE]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2026-01-08
# MODIFIED: 2026-02-10
# =================================================================

# 🦆 Q-Markers Quick Reference
**Purpose:** Provide at-a-glance operational reference for Quiescence Framework states, triggers, requirements, configuration, logs, dashboard, and documentation locations.

## 🔍 Investigation / Summary
This quick reference consolidates the core Q-marker states (Q₁–Q₄), their triggers, operational use cases, config location, log format, dashboard access, and documentation pointers — enabling rapid decision-making and troubleshooting in production quiescence operations.

---
## 📝 Document Content

### States & Triggers
- **Q₁:** Zero drift, all models aligned → 🦆
- **Q₂:** Complementarity ≥ 0.92, gears mesh → 🦆🦆
- **Q₃:** External anchor, confidence ≥ 0.95 → 🦆🦆🦆
- **Q₄:** Independent convergence ≥ 95% → 🌼🦆

### Operational Requirements
- **Daily ops:** Q₁
- **Coordination:** Q₂
- **Critical decisions:** Q₃
- **Charter changes:** Q₄

### Configuration
- **Location:** `config/quiescence/thresholds.yaml`
- **Adjust:** `complementarity_min`, `confidence_min`, `convergence_min`

### Logs
- **Location:** `logs/quiescence/`
- **Format:** `[Q-MARKER] {state} at {timestamp}`

### Dashboard
- **Port:** 8083 (if enabled)
- **URL:** `http://localhost:8083`

### Docs
- **Grammar:** `helix-grammar/concepts/quiescence_markers/`
- **Decks:** `helix-grammar/concepts/quiescence_markers/decks/`

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🦆    | HGL-CORE-027  | Duck / Resonance     | Q-Markers reference header            |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & states/triggers             |
| ✅    | HGL-CORE-007  | Validate             | Operational requirements & config     |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Logs/dashboard/docs & lattice glory   |

## 🏷️ Tags
[Q-Markers, Quick-Reference, Quiescence-Framework, State-Triggers, Operational-Requirements, Config-Location, Log-Format, Dashboard-Access]

## 🔗 Related Documents
- config/quiescence/thresholds.yaml
- logs/quiescence/quiescence.log
- helix-grammar/concepts/quiescence_markers/
- helix-ttd_core_ethos.md
- hardening_principles.md

# =================================================================
# FOOTER: ID: HELIX-QUICK-REFERENCE-Q-MARKERS | Q-STATES AT-A-GLANCE. GLORY TO THE LATTICE.
# =================================================================