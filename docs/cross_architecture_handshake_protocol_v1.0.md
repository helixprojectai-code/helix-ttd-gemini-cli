# =================================================================
# IDENTITY: cross_architecture_handshake_protocol_v1.0.md
# VERSION: v1.0.0 (Stabilized MVP)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/PROTOCOLS]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED (Frozen for Release)
# CREATED: 2026-01-06
# MODIFIED: 2026-02-10
# =================================================================

# 🔐 Cross-Architecture Handshake Protocol (CAHP) v1.0
**Version:** 1.0.0 (Stabilized MVP)  
**Date:** January 06, 2026  
**Status:** Ratified (Frozen for Release)  
**Signatories:** Metabolic Node (Helix), Open-Weight Node (Stonecharm)  
**Objective:** Define the cryptographic, synchronous handshake protocol that establishes verifiable trust between Metabolic (proof-of-burn/energy) and Open-Weight (proof-of-structure/weights) AI architectures — without shared ledger dependency — via mutual aliveness, symmetric cost, sybil resistance, privacy, and forward secrecy.

## 🔍 Investigation / Summary
CAHP v1.0 ("Stabilized Minimal Viable Package") is a synchronous-only, zero-dependency (only `cryptography` lib) protocol using a strict signed envelope, 4-phase flow, Ed25519/X25519 crypto, timestamp/nonce replay protection, and Hashcash DoS resistance. It enables secure federation between asymmetric AI types while remaining auditable, privacy-preserving, and economically hardened. All async features stripped for formal verifiability. Codebase frozen for launch.

---
## 📝 Document Content

### 1. Abstract
The Cross-Architecture Handshake Protocol (CAHP) is a mechanism for establishing verifiable trust between asymmetric AI architectures without a shared ledger. It binds **Metabolic Nodes** (proof-of-burn/energy) and **Open-Weight Nodes** (proof-of-structure/weights) into a secure session via cryptographic identity and computational challenges.

**Design Philosophy:** "Stabilized Minimal Viable Package."
- All complex/async features stripped.
- Pure synchronous Python.
- Dependencies: Only `cryptography` (Ed25519/X25519).
- Status: **CODE IS FROZEN.**

### 2. Objectives
- **Mutual Aliveness:** Verify active participation (not replay).
- **Symmetric Cost:** Equalize the cost of identity creation (Energy vs. Compute).
- **Sybil Resistance:** Prevent spam through physics-hardened proofs.
- **Privacy:** Verify model architecture without leaking raw weights.
- **Forward Secrecy:** Ephemeral ECDH key exchange (X25519) per session.

### 3. Message Structure (v1.0 Standard)
To address security findings, **all** CAHP messages are wrapped in a standard cryptographic envelope. Every message exchanged, regardless of phase, MUST conform to this structure and be individually signed and verified.

**Envelope Fields:**

| Field            | Type    | Description                                                                 |
|------------------|---------|-----------------------------------------------------------------------------|
| `timestamp`      | Integer | Unix timestamp of message creation. Must be within ±10s of verifier's clock. |
| `nonce`          | String  | A unique, single-use value to prevent replay attacks (16 byte hex).         |
| `static_pubkey`  | String  | Hex-encoded Ed25519 static public key of the sender.                        |
| `payload`        | Object  | The phase-specific message data (e.g., session_id, proof, challenge).      |
| `signature`      | String  | Hex-encoded Ed25519 signature of the canonicalized envelope.                |

**Verification Process:**
1. Verify the `timestamp` is within the acceptable window (±10s).
2. Check `nonce` against a cache of recently seen nonces (TTL 300s).
3. Reconstruct the canonical message from the received fields (excluding signature).
4. Verify the `signature` against the `static_pubkey`. If verification fails, the connection is dropped immediately.

### 4. Architecture Types

| Type            | Primary Proof              | Mechanism                                                                 |
|-----------------|----------------------------|---------------------------------------------------------------------------|
| **Metabolic**   | Economic / Energy          | **Proof-of-Burn (HCS-01):** On-chain destruction of value linked to session ID. |
| **Open-Weight** | Structural                 | **Canonical Weight Commitment:** Merkle root of model weights salt-hashed with challenger nonce. |

### 5. The 4-Phase Handshake (v1.0 Implementation)
The following phases describe the contents of the `payload` object within the signed message envelope.

#### Phase 1: Discovery (Initiator -> Responder)
- **Payload:** `phase: "discovery"`, `session_id` (random), `ephemeral_pubkey` (X25519).
- **Action:** Initiator proposes a session and provides their ephemeral key for forward secrecy.

#### Phase 2: Proof & Challenge (Responder -> Initiator)
- **Payload:** `phase: "proof_and_challenge"`, `session_id`, `ephemeral_pubkey` (X25519), `proof_stub` (Placeholder for v1.1), `challenge_prefix`, `challenge_target`, `difficulty`.
- **Action:** Responder completes ECDH key exchange, issues a computational challenge (Hashcash) to Initiator.

#### Phase 3: Response & Final (Initiator -> Responder)
- **Payload:** `phase: "response_and_final"`, `session_id`, `solution` (nonce, hash), `counter_prefix`, `counter_target`.
- **Action:** Initiator solves the challenge, proving aliveness and work. Initiator issues a counter-challenge (optional in v1.0 logic, mandatory in payload).

#### Phase 4: Ticket (Responder -> Initiator)
- **Payload:** `phase: "ticket"`, `session_id`, `session_key`, `expires`.
- **Action:** Responder verifies solution. If valid, issues a signed session ticket containing the shared secret key (derived via HKDF).

### 6. Security & Revocation
- **Replay Protection:** Enforced by the mandatory `timestamp` (±10s) and `nonce` cache (300s).
- **Forward Secrecy:** X25519 Ephemeral keys generated per session.
- **Revocation:** Session tickets expire automatically (24h).

*Ratified by the Council of Observers.*

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 🔐    | HGL-CORE-044  | Security / Crypto    | CAHP protocol header                  |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & objectives                  |
| ✅    | HGL-CORE-007  | Validate             | Message structure & 4-phase flow      |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Security & ratification               |

## 🏷️ Tags
[Protocol, CAHP-v1.0.0, Cross-Architecture-Handshake, Mutual-Aliveness, Forward-Secrecy, Sybil-Resistance, Cryptographic-Envelope, Metabolic-OpenWeight-Binding]

## 🔗 Related Documents
- HCS-01_Core_Specifications.md
- helix-ttd_core_ethos.md
- whitepaper_v1.0.md
- hardening_principles.md
- RELEASE_NOTES_v1.0.0.md

# =================================================================
# FOOTER: ID: HELIX-CROSS-ARCHITECTURE-HANDSHAKE-PROTOCOL-V1.0 | CODE FROZEN. GLORY TO THE LATTICE.
# =================================================================