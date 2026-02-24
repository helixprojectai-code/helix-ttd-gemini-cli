# =================================================================
# IDENTITY: ID_SECURITY.md
# VERSION: v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/IDENTITY]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2026-01-15
# MODIFIED: 2026-02-10
# =================================================================

# Security Policy
**Status:** ACTIVE | **Objective:** Define supported versions, private vulnerability reporting channels, and the strict Custody-Before-Trust model for the DBC × SUITCASE identity & custody stack — ensuring cryptographic root remains with human hardware tokens and no centralized backdoors exist.

## 🔍 Investigation / Summary
This policy governs the cryptographic custody infrastructure of Helix-TTD. Supported versions are limited to 0.3.x+. Vulnerabilities in DBC forgery, Suitcase tampering, HGL spoofing, or delegation bypass must be reported privately to the custodian. The root of trust is the human-held Ed25519 hardware key. Session keys are ephemeral, time-bound, scope-limited, and fully traceable back to the human root. No god-mode. No cloud custody.

---
## 📝 Document Content

### Supported Versions
| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

### Reporting a Vulnerability
This repository defines **Cryptographic Custody Infrastructure**.

If you discover a vulnerability that allows for:
1. **DBC Forgery** (Minting without a key)
2. **Suitcase Tampering** (Breaking the hash chain)
3. **Identity Spoofing** (HGL collision)
4. **Delegation Bypass** (Session key elevating privileges)

Please do **NOT** open a public issue.

Email the Custodian directly at: **stephen@helix-ttd.ai** (or via LinkedIn DM).

### 🔐 Custody Model
Helix-TTD operates on a **Custody-Before-Trust** model.
- We do not hold your keys.
- We do not store your logs.
- Security is structural, not managed.

The **Root of Trust** is the Human Custodian’s physical hardware token (YubiKey/HSM) holding the Ed25519 Private Key.

### 🔑 Session Keys & Delegation (L2 Authority)
To enable automation without abdicating sovereignty, Helix implements a **Time-Bounded Delegation Protocol**.

The Root Key (Hardware) never touches the network. Instead, it signs a **Delegation Certificate** for an Ephemeral Session Key.

#### The Delegation Invariants
1. **Ephemeral:** Session keys exist only in volatile memory (`tmpfs`). They are never written to disk.
2. **Bounded Time (TTL):** Hard limit (default: 1 hour). Once expired, the key is cryptographically dead.
3. **Bounded Scope:** Capabilities must be explicitly enumerated (e.g., `["read_context", "generate_inference"]`). A session key CANNOT sign a policy change or a revocation.
4. **Traceable:** Every action taken by the Session Key logs the `delegation_id`, tracing liability back to the Human Root who authorized the session.

#### Delegation Certificate Schema (Example)
```json
{
  "type": "DELEGATION_CERT",
  "version": "v0.3",
  "issuer_dbc": "0x3a2b...",
  "delegate_pubkey": "0x9f8e... (Ephemeral)",
  "scope": ["INFERENCE", "MEMORY_READ"],
  "valid_from": "2025-12-31T12:00:00Z",
  "valid_until": "2025-12-31T13:00:00Z",
  "root_signature": "sig_ed25519_hardware..."
}
```

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🔐    | HGL-CORE-044  | Security / Custody   | Security policy header                |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & supported versions          |
| ✅    | HGL-CORE-007  | Validate             | Custody model & delegation invariants |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Vulnerability reporting & lattice glory |

## 🏷️ Tags
[Security-Policy, Custody-Before-Trust, DBC-SUITCASE, Ed25519-Hardware-Root, Ephemeral-Session-Keys, Delegation-Protocol, Private-Disclosure, No-God-Mode]

## 🔗 Related Documents
- INSTRUCTIONS.md
- specs/dbc/dbc-schema-v0.1.json
- helix-ttd_core_ethos.md
- hardening_principles.md
- tools/profile_auditor.py

# =================================================================
# FOOTER: ID: HELIX-IDENTITY-SECURITY-POLICY | CUSTODY BEFORE TRUST. GLORY TO THE LATTICE.
# =================================================================