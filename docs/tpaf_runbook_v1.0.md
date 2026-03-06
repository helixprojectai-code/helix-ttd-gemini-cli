# =================================================================
# IDENTITY: tpaf_runbook_v1.0.md
# VERSION:  v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN:   HELIX-TTD-GRAMMAR / [DOCS/CONSTITUTION]
# NODE:     4 (ONTARIO)
# STATUS:   RATIFIED-CANONICAL
# CREATED:
# MODIFIED: 2026-02-10
# =================================================================

# 🤝 TPAF Runbook v1.0

**Status:** ✅ Active & Enforced | **Objective:** Implement a structured protocol for preventing irreversible actions in Helix-TTD without explicit human consent.

## 🔍 Investigation / Summary
This document defines the Two-Party Approval Flow (TPAF), a structural constraint mechanism that enforces shared agency before executing high-impact actions. By rigidly separating the roles of Requester, Approver, and Executor, TPAF ensures no action—especially irreversible ones—can proceed without positive consensus. It details the four-phase approval workflow, emphasizing cryptographic signature verification and audit logging. By establishing the requirement for human review and authorization, this runbook aims to mitigate any risk to governance by requiring the human to be the check and balance.

---

## 📝 Document Content

### 1. 📚 Overview
The Two-Party Approval Flow (TPAF) is a structural constraint mechanism designed to prevent irreversible actions without explicit human consent. It strictly separates the roles of **Requester**, **Approver**, and **Executor**.

### 2. ⚖️ Role Definitions
| Role | Definition | Permissions |
| :--- | :--- | :--- |
| **Requester** | The agent (human or AI) initiating a state change. | `READ`, `DRAFT_INTENT` |
| **Approver** | The designated human custodian with authority to sign off. | `REVIEW`, `SIGN_APPROVAL` |
| **Ops Engineer** | The entity (system or human) that executes the signed intent. | `EXECUTE`, `WRITE_LEDGER` |

### 3. ✅ The Approval Workflow
#### 🔍 Phase 1: Initiation
1.  **Requester** generates an **Intent Block** containing:
    *   Proposed Action
    *   Target Resource
    *   Impact Assessment (Reversible/Irreversible)
    *   Rollback Plan
2.  System locks the Intent Block in `PENDING_REVIEW` state.

#### ❓ Phase 2: Compliance Verification
The **Approver** must validate the following (see `templates/compliance_checklist.json`):
*   [ ] **Purpose Limitation:** Does intent match stated purpose?
*   [ ] **Data Minimization:** Is PII usage minimal?
*   [ ] **Consent:** Is explicit consent present?
*   [ ] **Risk Rating:** Is the risk acceptable?

#### 🤝 Phase 3: Authorization
1.  If **Approved**:
    *   Approver signs the block with their cryptographic key.
    *   State transitions to `AUTHORIZED`.
2.  If **Rejected**:
    *   Reason is logged.
    *   State transitions to `ABORTED`.

#### 📝 Phase 4: Execution & Audit
1.  **Ops Engineer** verifies the signature.
2.  Action is executed.
3.  **Audit Log** records: `Timestamp`, `RequesterID`, `ApproverID`, `ActionHash`, `Outcome`.

### 4. 🛡️ Irreversible Action Prevention
**Constraint:** Any action flagged `IRREVERSIBLE` (e.g., data deletion, model weight update, financial transaction) that lacks a valid Approver Signature will be structurally blocked by the Execution Engine.

---

## 📖 Glyph Reference
| Glyph | Code | Meaning | Use-Case |
| :--- | :--- | :--- | :--- |
| 🤝 | HGL-CORE-015 | Collaborate | Two-Party Approval Flow |
| 🛡️ | HGL-CORE-010 | Safeguard | Irreversible Action Prevention |
| 📚 | HGL-CORE-005 | Knowledge | Role Definitions |
| 🔍 | HGL-CORE-001 | Investigate | Phase 1: Initiation and Intent Block |
| ✅ | HGL-CORE-007 | Validate | Phase 3: Authorization Signature |
| 💬 | HGL-CORE-014 | Dialogue | Justification of Rejection |
| ⚖️ | HGL-CORE-011 | Ethics | Compliance Verification checklist |

## 🏷️ Tags
[TPAF, Runbook, Two-Party-Approval, Governance, Protocol, Immutability, Signature, Human-Oversight]

## 🔗 Related Documents
- whitepaper_custody_before_trust.md
- constitutional_invariants.md
- accountability_principle.md

# =================================================================
# FOOTER: ID: HELIX-TPAF-BP | VALIDATION BEFORE EXECUTION.
# =================================================================
