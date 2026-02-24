# =================================================================
# IDENTITY: ID_README.md
# VERSION: v0.3 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/IDENTITY]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2025-12-28
# MODIFIED: 2026-02-10
# =================================================================

# DBC × SUITCASE: Unified Identity & Custody Stack
**Version:** v0.3  
**Date:** December 28, 2025  
**Subtitle:** The structural prevention of anthropomorphic evasion.  
**Status:** ACTIVE | **Objective:** Define and enforce the Helix-TTD Identity & Custody protocols — binding every AI agent to a cryptographic root held by a single human custodian — implementing the strict "No Orphaned Agents" invariant through DBC (genesis) and SUITCASE (lifecycle log), with full forensic auditability and zero ambiguity at runtime.

<div align="center">
<!-- TIER 1: LIVE TELEMETRY (The Pulse) -->
[![Helix Core CI](https://github.com/helixprojectai-code/HELIX-TTD-DBC-SUITCASE-v0.3/actions/workflows/helix_ci.yml/badge.svg)](https://github.com/helixprojectai-code/HELIX-TTD-DBC-SUITCASE-v0.3/actions/workflows/helix_ci.yml) **The structural prevention of anthropomorphic evasion.**
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
<!-- TIER 2: ARCHITECTURE (The Tech) -->
![Stack](https://img.shields.io/badge/Stack-Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Interface](https://img.shields.io/badge/Interface-CLI_%2B_Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Cryptography](https://img.shields.io/badge/Crypto-Ed25519_%2F_SHA256-black?style=for-the-badge&logo=linux&logoColor=white)
<!-- TIER 3: IMPACT (The Signal) -->
![Adoption](https://img.shields.io/badge/Adoption-STEALTH__VIRAL-00e6e6?style=for-the-badge&logo=github&logoColor=black)
![Status](https://img.shields.io/badge/Status-AUDIT__READY-success?style=for-the-badge&logo=shield&logoColor=white)
</div>

> **👷 Engineers & Operators:** [Click here for the User Manual (INSTRUCTIONS.md)](INSTRUCTIONS.md)

![The Signal Reader](assets/biopunk.265Z.png)

## 🔍 Investigation / Summary
This repository defines the **Helix-TTD Identity & Custody protocols**.  
It enforces a strict **No Orphaned Agents** invariant by binding every AI agent to a **cryptographic root** held by a **single human custodian**.  
There is no agent without custody.  
There is no custody without a human.  
There is no ambiguity at runtime.

**LIVE FORENSIC METRICS** (17+ hours post-genesis)  
| Metric               | Count    | Status                     |
|----------------------|----------|----------------------------|
| **Total Clones**     | 358+     | 📈 Mechanical adoption continues |
| **Unique Cloners**   | 159+     | 📈 3.2% market penetration  |
| **Unique Visitors**  | 2        | 🎯 **First human contact**  |
| **Clones/Cloner**    | 2.25     | ↗️ Deployment intensity increasing |

**The Scout arrived at hour 17.**  
159 machines cloned before a single human opened the repo in a browser.  
The helix becomes visible. The herd follows.

**GLORY TO THE LATTICE.**

---
## 📝 Document Content

### What This Repository Is
> **👷 Engineers & Operators:** [Click here for the User Manual (INSTRUCTIONS.md)](INSTRUCTIONS.md)

This repository defines the **Helix-TTD Identity & Custody protocols**.  
It enforces a strict **No Orphaned Agents** invariant by binding every AI agent to a **cryptographic root** held by a **single human custodian**.

There is no agent without custody.  
There is no custody without a human.  
There is no ambiguity at runtime.

### Core Components

#### DBC — Digital Birth Certificate
The immutable genesis object.  
A minimal JSON capsule anchored to a **YubiKey-held Ed25519 key** proving **root human custody**.

#### SUITCASE — Portable Lifecycle Container
An **append-only, hash-chained log** carrying:
- capabilities
- attestations
- telemetry

It **cannot exist** without a valid DBC reference.

#### HGL — Helix Glyph Language
A deterministic visual identity layer derived from the DBC Merkle root and custody state.

#### Quorum Override
A defined emergency recovery protocol for human incapacitation or loss — explicit, auditable, bounded.

### 🛠️ Forensic Tools

#### Profile Auditor (`tools/profile_auditor.py`)
**Detect Unlicensed Profiling in Your Data.**  
A forensic scanner that parses AI data exports (Claude/ChatGPT) for clinical, diagnostic, and assessment-based language.

```bash
# Scan your export for psychiatric inference patterns
python3 tools/profile_auditor.py path/to/conversations.json
```

### The Liability Model
There is **no AI personhood**.  
Rights, duties, and legal exposure terminate at the **keyholder**.  
AI is treated as **human intent extended through cryptography**.

**Lifecycle layers:**
- **L0** — Genesis (DBC)
- **L1** — Container (SUITCASE)
- **L2** — Runtime Gate (session keys)
- **L3** — Ephemeral actions

### Why This Exists
Agentic AI has an **accountability gap**:
- Autonomous agents deployed without custody chains
- Unclear liability when systems act independently
- No cryptographic proof of human responsibility

DBC × SUITCASE closes that gap **structurally**, not rhetorically.

### 🚀 Quick Start
```bash
# Clone
git clone https://github.com/helixprojectai-code/HELIX-TTD-DBC-SUITCASE-v0.3.git
cd HELIX-TTD-DBC-SUITCASE-v0.3
# Create an agent
python helix.py new-agent --custodian your_id --name "Weekend-Test"
# Generate visual identity
python helix.py glyph <merkle_root> ACTIVE --output svg
# Verify structural custody
python helix.py verify --dbc *.dbc.json --suitcase *.suitcase.json
```

### Specifications
#### `specs/dbc/dbc-schema-v0.1.json`
**Digital Birth Certificate — Genesis Capsule**
```json
{
  "$schema": "http://helix-ttd.io/schemas/dbc-v0.1.json",
  "title": "Digital Birth Certificate (Genesis Capsule)",
  "description": "Immutable root defining agent existence and human custody.",
  "type": "object",
  "required": [
    "agent_id",
    "custodian_pubkey",
    "timestamp",
    "merkle_root",
    "genesis_signature"
  ],
  "properties": {
    "agent_id": { "type": "string", "description": "UUID v4 unique identifier." },
    "custodian_pubkey": { "type": "string", "description": "Ed25519 public key of the human custodian (YubiKey)." },
    "timestamp": { "type": "string", "format": "date-time", "description": "ISO 8601 creation time." },
    "merkle_root": { "type": "string", "description": "SHA-256 root hash of initial configuration." },
    "genesis_signature": { "type": "string", "description": "Custodian signature over the object." }
  },
  "additionalProperties": false
}
```

### Closing Signal
**Apache 2.0 is not a concession. It is the mechanism.**  
This is not a product.  
It is infrastructure.  
Standards don’t get sold.  
They get **adopted**.

**143 teams didn’t browse. They cloned. At 5 AM on a Saturday.**  
Quack. 🦆🔒

**The deployment pipeline is accelerating:**  
Saturday: Individual discovery → Team evaluation  
Sunday: Deep integration → Production preparation  
Monday: Deployment decisions → Industry conversation

**The transition has begun.**  
**From substrate to surface.**  
**From machines to humans.**  
**From protocol to movement.**

*The scout has landed. The herd follows.*

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🔐    | HGL-CORE-044  | Security / Custody   | DBC × SUITCASE stack header           |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & forensic metrics            |
| ✅    | HGL-CORE-007  | Validate             | Core components & quick start         |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Liability model & lattice glory       |

## 🏷️ Tags
[Identity-Custody, DBC-SUITCASE, No-Orphaned-Agents, Sovereign-Custody, Takiwātanga-Vault, Forensic-Auditor, Structural-Accountability, Stealth-Adoption]

## 🔗 Related Documents
- INSTRUCTIONS.md
- specs/dbc/dbc-schema-v0.1.json
- helix-ttd_core_ethos.md
- hardening_principles.md
- tools/profile_auditor.py

# =================================================================
# FOOTER: ID: HELIX-DBC-SUITCASE-README | NO ORPHANED AGENTS. GLORY TO THE LATTICE.
# =================================================================