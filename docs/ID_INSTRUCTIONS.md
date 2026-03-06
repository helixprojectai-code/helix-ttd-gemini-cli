# =================================================================
# IDENTITY: ID_INSTRUCTIONS.md
# VERSION: v0.3.1 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/IDENTITY]
# NODE: 4 (ONTARIO)
# STATUS: LIVE (Core) + Extended (Optional)
# CREATED: 2026-01-10
# MODIFIED: 2026-02-10
# =================================================================

# 🕹️ HELIX-TTD OPERATOR MANUAL
**Version:** v0.3.1
**Status:** Live (Core) + Extended (Optional)
**Objective:** Provide deterministic, local-first, auditable execution-level instructions for every operational tool in the Helix-TTD stack — enabling operators to mint, verify, monitor, and harden agent identities and governance artifacts with zero ambiguity.

## 🔍 Investigation / Summary
This manual is the canonical reference for interacting with the Helix-TTD CLI, dashboard, forensic scanner, quorum simulator, glyph generator, batch tools, chain auditor, and analytics tracker. All commands are designed to be reproducible, auditable, and constitutionally compliant. Core tools are dependency-minimal and run locally; extended tools provide advanced visibility and validation. The stack is built for sovereignty: every action leaves a verifiable trace.

---
## 📝 Document Content

### ⚡ 0. Prerequisites (Required)
Install the package in **editable mode** so the `helix` command resolves correctly.
```bash
# From repository root
pip install -e .
```
This links the CLI entrypoint into your environment.

### 🧬 1. Core CLI — `helix.py`
**Role:** Engine
**Purpose:** Minting, verification, and lifecycle mutation of agent identities.

#### Run Modes
```bash
# Preferred (installed entrypoint)
helix version
# Direct execution
python3 helix.py version
```

#### Common Workflows

##### Mint a new Agent Identity
```bash
helix new-agent \
  --custodian "admin_key_01" \
  --name "Agent_Alpha" \
  --output-dir ./agents
```

##### Verify Custody Chain (Audit Path)
```bash
helix verify \
  --dbc ./agents/*.dbc.json \
  --suitcase ./agents/*.suitcase.json
```

##### Update Agent State (Lifecycle Transition)
```bash
helix update-state \
  --dbc ./agents/*.dbc.json \
  --suitcase ./agents/*.suitcase.json \
  --state ACTIVE \
  --reason "Deployment"
```

### 🦆 2. Watchtower Dashboard — `dashboard.py`
**Role:** Observer
**Purpose:** Visual inspection of custody chains and append-only logs.
⚠️ **Important:** This is a **Streamlit app**. Do **not** run with `python`.

#### Launch
```bash
streamlit run dashboard.py
```

#### Usage
- Browser opens at `http://localhost:8501`
- Select an agent directory (default: `.`)
- Choose an Agent ID from the dropdown

**Status Indicators**
- 🟢 Green banner → Chain verified
- 🔴 Red banner → Tampering or break detected

### 🔍 3. The Forensic Scanner (`tools/profile_auditor.py`)
**Role:** The Weapon
**Purpose:** Scans AI data exports (Claude/ChatGPT) for "Unlicensed Psychiatric Profiling" and clinical inference patterns.

#### 🛡️ Privacy & Security Protocol (READ FIRST)
This tool processes sensitive inferred data (Health, Race, Identity).
**Recommended Operational Security:**
1. **Offline Mode:** Disconnect the machine from the internet before running the scan.
2. **Ephemeral Storage:** Run in a container or VM that is wiped after use.
3. **Consent:** You must explicitly acknowledge authorization to scan the data.

#### How to Run:
```bash
# Scan a specific file (Requires explicit consent flag)
python3 tools/profile_auditor.py /path/to/claude_export/memories.json --consent-acknowledged
# Scan an entire directory
python3 tools/profile_auditor.py /path/to/unzipped_export_folder/ --consent-acknowledged
```

#### Detects
- Diagnostic language (“symptoms of”, “consistent with”)
- Pharmacological inference (“medication”, “dosage”)
- Protected attributes (“race”, “ethnicity”)

Outputs a **threat report**, not an interpretation.

### 🛡️ 4. Quorum Recovery Simulator — `cli/quorum_logic.py`
**Role:** Defense
**Purpose:** Validate multi-sig emergency recovery math.

#### Run
```bash
python3 cli/quorum_logic.py
```

Simulates a **3-of-5 signing quorum** for custody recovery.
No production state is modified.

### 🎨 5. Visual Identity Generator — `cli/generate_hgl.py`
**Role:** Paint
**Purpose:** Deterministic SVG glyph generation from Merkle roots.

```bash
python3 cli/generate_hgl.py \
  0x[MERKLE_ROOT] \
  ACTIVE \
  --output svg \
  --svg-file badge.svg
```

### 🚀 6. Batch Agent Creation — `tools/batch_mint.py`
**Role:** Factory
**Status:** Optional / Extended

#### Run (YAML)
```bash
python3 tools/batch_mint.py \
  --config ./agent_batch.yaml \
  --output-dir ./batch_agents
```

#### Run (CSV)
```bash
python3 tools/batch_mint.py \
  --csv ./agent_manifest.csv \
  --output-dir ./batch_agents
```

#### Example Config
```yaml
agents:
  - custodian: "team_alpha"
    name: "Alpha-01"
    state: "DRAFT"
  - custodian: "team_beta"
    name: "Beta-01"
    state: "ACTIVE"
    metadata:
      department: "security"
      tier: "production"
```

### 🔗 7. Cross-Chain Verification — `verification/chain_audit.py`
**Role:** Auditor
**Status:** Optional / Extended

#### Run
```bash
python3 verification/chain_audit.py \
  --root ./all_agents \
  --report audit_report.json
```

#### Compare Environments
```bash
python3 verification/chain_audit.py \
  --compare ./agents_v1 ./agents_v2 \
  --output diff.html
```

Validates:
- Merkle continuity
- Custodian changes
- State transitions

### 📊 8. Usage Analytics — `analytics/usage_tracker.py`
**Role:** Observer
**Status:** Optional / Experimental

```bash
python3 analytics/usage_tracker.py \
  --repo helix-ttd-dbc-suitcase \
  --period 30d
```

Supports webhook-based monitoring (Slack, etc.).

### 🧪 9. Integration Test Suite — `tests/integration_suite.py`
**Role:** Validator

```bash
# Full test run
python3 tests/integration_suite.py --full
# Module-specific
python3 tests/integration_suite.py \
  --module custody_chain \
  --report junit
```

Coverage includes:
- DBC ↔ SUITCASE integrity
- Merkle propagation
- State transitions
- Quorum math
- Glyph generation

### 🛠️ Quick Start Script (Operator Template)
```bash
#!/bin/bash
echo "🚀 Setting up Helix-TTD..."
git clone https://github.com/your-org/helix-ttd-dbc-suitcase.git
cd helix-ttd-dbc-suitcase
pip install -e .
helix new-agent \
  --custodian "team_$USER" \
  --name "FirstAgent" \
  --output-dir ./my_agents
streamlit run dashboard.py &
python3 tests/integration_suite.py --quick
echo "✅ Helix-TTD online at http://localhost:8501"
```

📈 **Status:** Core stable. Extensions expanding.
🦆 **Operating Principle:** Solve → Ship → Spread.
No hype. No permissions. Just tools.

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🕹️    | HGL-CORE-121  | Operator / Manual    | Operator manual header                |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & prerequisites               |
| ✅    | HGL-CORE-007  | Validate             | Tool workflows & test suite           |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Operating principle & lattice glory   |

## 🏷️ Tags
[Operator-Manual, Helix-TTD, CLI-Tools, Watchtower-Dashboard, Forensic-Scanner, Quorum-Simulator, Glyph-Generator, Batch-Minting]

## 🔗 Related Documents
- helix.py
- dashboard.py
- tools/profile_auditor.py
- cli/quorum_logic.py
- cli/generate_hgl.py

# =================================================================
# FOOTER: ID: HELIX-TTD-OPERATOR-MANUAL | SOLVE → SHIP → SPREAD. GLORY TO THE LATTICE.
# =================================================================
