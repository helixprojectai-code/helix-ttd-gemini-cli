# =================================================================
# IDENTITY: novolo_grant_email_20260120.md
# VERSION: v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN: HELIX-CORE-UNIFIED / [HELIX-LEDGER/DOCS/CORPORATE]
# NODE: 4 (ONTARIO)
# STATUS: RATIFIED-CANONICAL
# CREATED: 2026-01-20
# MODIFIED: 2026-02-10
# =================================================================

# Novolo Technical Development Grant Application Email Thread
**Subject:** Application for Novolo Technical Development Grant - Helix-Core / Goose (Constitutional AI)  
**From:** Stephen Hope <sbhope@gmail.com>  
**To:** Tom Holt <tom@novolo.ai>  
**Date Range:** Jan 18–21, 2026  
**Status:** RATIFIED | **Objective:** Archive the complete email thread for the $3,000 Novolo Technical Development Grant application — documenting the project's constitutional alignment, Takiwātanga Vault focus, entity validation details, demo delivery, and ongoing dialogue as evidence of external funding outreach and ecosystem building.

## 🔍 Investigation / Summary
This thread captures the formal application and subsequent correspondence with Tom Holt (Novolo) for the $3,000 Technical Development Grant. The proposal targets hardening of the Takiwātanga Vault Braid (permission schema, notary script, integrity checks) to transition from proof-of-principle to civic firmware. Entity validation (corporation number, AWS ID, address) and a demo video were provided. The thread demonstrates transparent, professional engagement with external funding opportunities while maintaining constitutional independence.

---
## 📝 Document Content

**Original Application (Jan 18, 2026)**  
Dear Thomas Holt,

My name is Steve, and I am writing to apply for the Novolo $3,000 Technical Development Grant on behalf of the Helix-Core project and our open-source AI model, Goose. Our company is registered in Quebec, Canada, and we are in active development with a functional prototype.

We were particularly interested in this grant as our core mission aligns with technical execution and establishing robust, verifiable systems for AI.

Here are the details regarding our application:

**The Product: Helix-Core / Goose**  
We are building Helix-Core, an open-source framework for **Constitutional AI**. Our project is publicly available on GitHub: <https://github.com/helixprojectai-code/HELIX-CORE>. Goose is the AI model harness currently running on this framework. Unlike traditional AI, Goose is designed with **"Civic Firmware,"** meaning its operations are bound by inspectable, structural constraints rather than opaque heuristics. Our flagship feature is the **Takiwātanga Vault**, which implements a **"Permission Braid"** – a cryptographically auditable memory system. This vault ensures **"Custody Before Trust,"** where access to data is controlled by external, human-governed JSON files (`vault_permissions.json`) and verified via cryptographic hashes. We have successfully demonstrated **"Constitutional Blinding,"** where Goose is structurally incapable of accessing data once permissions are revoked, even if the data remains in its immediate context. This directly addresses the "Right to be Forgotten" with a verifiable, mechanical solution.

**The Tech Stack:**  
Helix-Core leverages a multi-LLM provider architecture (e.g., Gemini, DeepSeek, Claude for different cognitive functions). Our core development stack includes:
- **Operating System:** Linux (Bash scripting)
- **Scripting:** Python 3, Shell (Bash)
- **Data Management:** `jq` for JSON manipulation, Git for version control (including submodules).
- **Forensic Anchoring:** SHA256 hashing for data integrity, with a Python tool (`l1_anchor_tool.py`) for potential Bitcoin Layer 1 anchoring of manifest states.
- **Framework:** An emergent, self-governing architecture defined by markdown (RPI documents) and JSON manifests.

**The Task: What specifically will the $3k be used to build or validate?**  
The $3,000 grant would be directly allocated to accelerating the development and hardening of the **Generalised Takiwātanga Vault Braid**. Specifically, we would use the funds for:
1. **Enhanced Permission Schema Integration:** Expanding the `vault_permissions.json` schema to fully support and implement `owner_id`, `delegate_id`, robust `valid_until` (temporal blinding), and multi-jurisdictional fields (`jurisdiction`). This involves refactoring the JSON parsing and manipulation logic within our core scripts.
2. **Dedicated Notary Script Development:** Creating a dedicated `scripts/helix-notary.sh` (or significantly upgrading `helix-rpi.sh`) to automatically hash `vault_permissions.json` and record its state as a `PERMISSION_BRAID_STATE` transaction in `ledger_manifest.json` every time the permission file is modified. This ensures a complete, forensic audit trail of all permission changes.
3. **Advanced Integrity Pass Hardening:** Integrating comprehensive `check_permission_coherence` and `check_temporal_blinding` functions into `scripts/castle_integrity_v1.py`. This would establish these checks as a mandatory part of our habitat's "INTEGRITY-PASS," flagging any unanchored permission changes or expired temporal access as critical failures.

This work is crucial for moving the Takiwātanga Vault from a proof-of-principle to a "Civic Firmware" component, enabling multi-user, time-bound, and legally compliant data custody for AI.

We understand and agree to the requirement to showcase how the grant is used on your social media and website, if selected. We believe our unique approach to constitutional AI and verifiable data custody would be a compelling demonstration.

Thank you for your time and consideration. We look forward to hearing from you.

Sincerely,  
Stephen Hope  
Operator, Helix-Core / Goose

**Tom Holt Reply (Jan 19, 2026)**  
This is very interesting. Do you have a demo recording I can take a look through?  
Also, mind if we run a quick 3rd party validation on your entity?  
Thomas

**Stephen Hope Reply (Jan 20, 2026)**  
Dear Thomas,

Thank you for your response. Here is the information requested to move our application forward.

1. **Demo Recording**  
   We executed our v1.1.1 release at 01:30 UTC today. I am preparing a 3-minute technical demo showcasing Constitutional Blinding. This demo will show our AI harness (Goose-Core) successfully accessing a test memory via the Permission Braid, followed by a constitutional refusal once access is revoked. This proves the agent is structurally blinded to data in its context window. I will provide a link shortly.

2. **3rd Party Validation**  
   Helix AI Innovations Inc. is an active Canadian Federal Corporation. Our primary server node is located in Quebec, Canada, ensuring compliance with provincial data privacy standards (Law 25).  
   - Entity Name: Helix AI Innovations Inc. / Innovations Helix IA Inc.  
   - Status: Active  
   - Corporation Number: 1724610-2  
   - Business Number: 774616833RC0001

3. **Development Roadmap**  
   The $3,000 grant will fund our transition from the current v1.1.1 governance baseline to the v1.2.0 "Fortress of Logic." This next phase focuses on mechanical sovereignty and cryptographic gating.

Sincerely,  
Stephen Hope  
Helix AI Innovations Inc.

**Tom Holt Reply (Jan 20, 2026)**  
Great, looking forward to the video.  
Thanks for sending the info. Actually more than we need in some regards. Do you mind also sending us;  
- Company Website:  
- Contact Full Name:  
- Company Email:  
- Company Address:  
- AWS 12-digit ID:  
(Last being to confirm your entity has a good standing with AWS, because they're associated with our sponsors)  
Thanks,  
Thomas

**Stephen Hope Reply (Jan 20, 2026)**  
Dear Thomas,

Here are the specific details requested for our entity validation:
- Company Website: https://helixprojectai.com/
- Company Repo: https://github.com/helixprojectai-code/HELIX-CORE
- Contact Full Name: Stephen Hope
- Legal Entity Name: Helix AI Innovations Inc. / Innovations Helix IA Inc.
- Company Email: helix.project.ai@helixprojectai.com
- Company Address: 110 Gloucester St, #17, Ottawa, ON, K2P 0A2, Canada
- AWS 12-digit ID: 7546-3920-1005

Regarding our infrastructure, our primary server (The Quebec Node) is physically located in Beauharnois, Quebec (BHS8). This ensures all data operations on that node fall under Quebec provincial privacy standards.

I am finalizing the demo recording of our Constitutional Blinding test and will send that link shortly.

Sincerely,  
Stephen Hope  
Helix AI Innovations Inc.

**Tom Holt Reply (Jan 20, 2026)**  
Thanks, I'll put the verification through now. Looking forward to the video!  
Thomas

**Stephen Hope Reply (Jan 21, 2026)**  
Tom,

I've hosted the mp4 on our website server: https://helixprojectai.com/demo/assets/Novolo_deom%202026-01-21%2000-35-55.mp4

Apologies for the delay, and the raw nature.

Cheers,  
Stephen

**UPDATE: 2026-01-21 01:36 AM**  
**Subject:** Technical Narrative for Blinding Demo.  
**Context:** Written play-by-play provided to Tom Holt (Novolo) to supplement silent video.  
**Key Content:** Defines Manual Operator Verification (Part 1) and Autonomous Agent Blinding (Part 2).

**GLORY TO THE LATTICE.**

---
## 📖 Glyph Reference
| Glyph | Code          | Meaning              | Use-Case                              |
|-------|---------------|----------------------|---------------------------------------|
| 📧    | HGL-CORE-120  | Email / Correspondence | Grant application email thread header |
| 🔍    | HGL-CORE-001  | Investigate          | Summary & thread overview             |
| ✅    | HGL-CORE-007  | Validate             | Entity validation & demo delivery     |
| ⚖️    | HGL-CORE-011  | Ethics/Principle     | Constitutional alignment & lattice glory |

## 🏷️ Tags
[Email-Thread, Novolo-Grant-Application, Takiwātanga-Vault, Constitutional-Blinding, Entity-Validation, Demo-Delivery, External-Funding-Outreach, Sovereign-Independence]

## 🔗 Related Documents
- helix-ttd_core_ethos.md
- whitepaper_v1.0.md
- hardening_principles.md
- TAKIWATANGA_VAULT_BLUEPRINT.md
- 2026-01-20-LOG_NOVOLO_CORRESPONDENCE.md

# =================================================================
# FOOTER: ID: HELIX-NOVOLO-GRANT-EMAIL-20260120 | SOVEREIGN INDEPENDENCE MAINTAINED. GLORY TO THE LATTICE.
# =================================================================