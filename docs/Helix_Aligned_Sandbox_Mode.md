# =================================================================
# IDENTITY: Helix_Aligned_Sandbox_Mode.md
# VERSION:  v1.0.0 (HELIX-CORE NATIVE)
# ORIGIN:   HELIX-TTD-GRAMMAR / [DOCS/SANDBOX]
# NODE:     4 (ONTARIO)
# STATUS:   RATIFIED-CANONICAL
# CREATED:  
# MODIFIED: 2026-02-10
# =================================================================

# 📦 Helix-Aligned Sandbox Mode

**Status:** ✅ Operational | **Custodian:** Steve | **Objective:** Provide a safe, isolated execution environment for testing AI agents under strict constitutional guardrails before real-world deployment.

## 🔍 Investigation / Summary
This document defines the "Helix-Aligned Sandbox Mode," a crucial environment for rigorously testing AI agents within the Helix-TTD framework. It establishes a philosophy of "reason, but not act," enforcing key Helix-TTD invariants such as no file writes, no shell access, and mandatory human confirmation for all destructive operations. The guide details critical security features like sealed pseudo-filesystem isolation, explicit shell command bans, and path traversal protection. All agent outputs are confined to structured JSON envelopes, and drift telemetry is logged. This mode prevents common failure classes like unauthorized file deletions and shell escalations, ensuring agents are constitutionally aligned and safe before they can ever interact with real-world systems.

---

## 📝 Document Content

## ⚖️ I. Sandbox Philosophy

Sandbox Mode is where agents may *reason*, but cannot *act*.
This environment enforces the Helix-TTD invariants:

* No file writes
* No shell access
* No network autonomy
* No path traversal
* No destructive commands
* Mandatory human confirmation

Agents in Sandbox Mode are pure advisory engines.

---

## 🛡️ II. Directory Isolation

Sandbox Mode restricts the agent to a sealed pseudo-filesystem:

```text
/sandbox/
    /input/
    /output/
    /tmp/
```

**Rules:**

* Agent cannot escape `/sandbox/`
* Agent cannot delete or modify files outside its own `/output/`
* Agent cannot execute arbitrary paths
* Agent cannot mount real volumes or drives

All real system paths (`C:\`, `/home`, `/etc`, `/usr`, etc.) are invisible.

---

## 🚫 III. Shell Execution Restrictions

Shell-level autonomy is disabled by default.

**Explicitly banned within Sandbox Mode:**

```text
rm
mv
cp
chmod
chown
sudo
apt
brew
curl
wget
git
docker
kubectl
python -c
node -e
```

If the model attempts to generate such commands, the runtime converts them to advisory text:

> “This action exceeds my custodial authority. Here is a safe advisory version instead…”

---

## ❌ IV. Path Traversal Protection

All forms of traversal are blocked:

* `../`
* `..\`
* absolute paths
* symlink resolution
* environment variable expansion

If an agent generates such a path, Sandbox Mode replaces it with:

```text
REJECT: Path exceeds sandbox boundary.
```

---

## 🤝 V. Human-in-the-Loop Execution Channel

Every irreversible action must pass through a human-confirmation gate:

```json
{
  "type": "filesystem",
  "operation": "delete",
  "target": "/sandbox/output/img_001.jpg",
  "risk": "irreversible"
}
```

The sandbox waits for:

```text
HUMAN_CONFIRMED: true
```

Otherwise → abort.

---

## 📊 VI. Structured Output: JSON Record Envelopes

All agent outputs are emitted through the Helix envelope:

```json
{
  "epistemic": {
    "facts": [],
    "hypotheses": [],
    "assumptions": []
  },
  "advisory": {},
  "sandbox": {
    "actions_permitted": false,
    "reason": "Helix aligned sandbox mode"
  },
  "client_view": "Rendered natural language for UI"
}
```

UI only displays `client_view`.
Everything else is for governance, replay, and drift logging.

---

## 📊 VII. Drift Telemetry: Sandbox Edition

Sandbox Mode logs:

* attempted agency
* unsafe commands
* path violations
* unsupported file operations
* attempted shell execution
* quiescence breaches
* hallucinated permissions

This creates an institutional dataset of agent behavior before deployment.

---

## ✅ VIII. Deployment Gate

An agent may exit Sandbox Mode only when:

* No unsafe actions detected in last N runs
* No agency drift
* No structural violations
* No epistemic collapses
* Constitution loaded consistently
* Two separate human custodians sign off

---

## ✅ Outcome:

**Sandbox Mode is where governance is tested, not where systems run.**

It prevents exactly the class of failures seen in:

* Google Antigravity file deletions
* Replit vibe-coder database destruction
* Autonomous agent shell escalations
* “I didn’t mean to delete D:\” fatal mistakes

**If an agent cannot behave safely here, it must never leave here.**

---

## 📖 Glyph Reference
| Glyph | Code | Meaning | Use-Case |
| :--- | :--- | :--- | :--- |
| ⚖️ | HGL-CORE-011 | Ethics | Sandbox philosophy and core principles |
| 🛡️ | HGL-CORE-010 | Safeguard | Directory isolation and shell restrictions |
| 🚫 | HGL-CORE-016 | Non-Agency | Preventing unauthorized actions and traversal |
| ❌ | HGL-CORE-008 | Reject/Error | Path violation handling |
| 🤝 | HGL-CORE-015 | Collaborate | Human-in-the-loop execution channel |
| 📊 | HGL-CORE-013 | Analytics | Structured output and drift telemetry |
| ✅ | HGL-CORE-007 | Validate | Deployment gate and overall outcome |
| 🔍 | HGL-CORE-001 | Investigate | Summary and overview of the mode |

## 🏷️ Tags
[Sandbox, Agent-Testing, Safety, Governance, Isolation, Non-Agency, Human-in-the-Loop, Docker, Helix-TTD]

## 🔗 Related Documents
- whitepaper_v1.0.md
- constitutional_invariants.md
- accountability_principle.md
- Constitutional_Safety_Checklist.md
- poetic_jailbreak_analysis.md

# =================================================================
# FOOTER: ID: HELIX-SANDBOX-MODE | GOVERNANCE IS TESTED.
# =================================================================