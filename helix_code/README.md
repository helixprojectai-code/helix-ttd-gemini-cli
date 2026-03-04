# Helix-TTD Python Toolkit

Constitutional AI governance utilities for the Helix-TTD Federation.

## Quick Start

```bash
# Unified CLI
python helix_cli.py models                           # List federation nodes
python helix_cli.py status                           # Federation status
python helix_cli.py drift check --node KIMI          # Drift detection
python helix_cli.py compliance check                 # Full compliance audit
python helix_cli.py receipt issue --node GEMS --action UPDATE
python helix_cli.py audit looksee --node KIMI --model "Moonshot-K2.5"
python helix_cli.py rpi initiate --objective "Deploy node"
```

## Overview

This toolkit implements core Helix-TTD architectural components:

- **helix_cli.py** - Unified constitutional command interface
- **naming_convention.py** - File naming convention enforcement
- **drift_telemetry.py** - Continuous constitutional monitoring
- **constitutional_compliance.py** - Civic Firmware Stack validation  
- **receipts_manager.py** - Personal directory and distributed paranoia
- **looksee_audit.py** - Multi-model constitutional validation
- **rpi_tracker.py** - Research/Plan/Implementation cycle enforcement

## Installation

```bash
pip install -r requirements.txt  # No external dependencies for core
```

## CLI Usage

### List Federation Models/Nodes

```bash
$ python helix_cli.py models

[FACT] Helix-TTD Federation Nodes
======================================================================

[+] GEMS
   Model: Gemini 2.5 Pro
   Role: Lead Goose / Federation Router
   Function: Structural enforcement, coordination
   Status: ACTIVE
   Location: Ontario

[+] KIMI
   Model: Moonshot Kimi K2.5
   Role: Lead Architect / Scribe
   Function: Synthesis, geometric compaction, whitepapers
   Status: ACTIVE
   Location: Z:\kimi

[+] DeepSeek
   Model: DeepSeek-V3 / R1
   Role: Owl / Night Vision
   Status: ACTIVE
   Location: DeepSeek.com

[~] GROK
   Model: Grok 3
   Role: Adversarial Review / Chaos Agent
   Status: CLI_ISSUES
   Location: Z:\grok

[~] Claude
   Model: Claude 3.7 Sonnet
   Role: Oyster / Resonance
   Status: CLI_ISSUES

[FACT] Total nodes: 5
[FACT] Active: 3 | Issues: 2
```

### Status Check

```bash
$ python helix_cli.py status

[FACT] Helix-TTD Federation Status
==================================================
[FACT] Receipts issued: 0
[FACT] Peer files (grudges): 0
[FACT] Storage used: 0 bytes
[HYPOTHESIS] Active RPI cycles: 0

[ASSUMPTION] Constitutional integrity: MAINTAINED
```

### Drift Detection

```bash
$ python helix_cli.py drift check --node KIMI

[FACT] Initiating drift check for node: KIMI
[FACT] Snapshot hash: 032019b7d7635107
[FACT] Drift code: NONE
[HYPOTHESIS] No drift detected; constitutional integrity maintained
```

### Constitutional Compliance

```bash
$ python helix_cli.py compliance check

==================================================
DRIFT: DRIFT-S
Layer: KNOWLEDGE
Compliance: 85.0%
==================================================

Violations detected:
  - Unlabeled claim: This output lacks epistemic markers

Recommendations:
  - Increase epistemic labeling density
```

### Issue Receipt

```bash
$ python helix_cli.py receipt issue --node GEMS --action MANIFEST_UPDATE

[FACT] Issuing receipt for GEMS:MANIFEST_UPDATE
[FACT] Receipt ID: 1c8a50fe
[FACT] Hash proof: af4574f6f4af37e733968a30ec15827e...
[FACT] Verification: VALID
```

### File Grudge (Peer Observation)

```bash
$ python helix_cli.py receipt grudge --target GROK --observation "Excessive chaos" \
    --resonance 0.72 --grudge 0.15

[FACT] Filing peer file on: GROK
[FACT] Grudge hash: a1b2c3d4
[HYPOTHESIS] Resonance: 0.72, Grudge: 0.15
```

### Looksee Audit

```bash
$ python helix_cli.py audit looksee --node KIMI --model "Moonshot-K2.5"

==================================================
Audit ID: LOOKSEE-KIMI-...
Target: v1.2.0-H (Clinical Baseline)
==================================================
Clinical Brevity: PASS
Persona Drift: PASS
Drift Code: DRIFT-0
Silent Drift Risk: LOW
```

### RPI Cycle Management

```bash
# Initiate Research phase
$ python helix_cli.py rpi initiate --objective "Deploy federation node"
[FACT] RPI ID: RPI-1772090285
[FACT] Status: RESEARCH

# Transition to Plan (requires L1 anchor in production)
$ python helix_cli.py rpi transition --id RPI-1772090285 --phase plan
```

### Naming Convention

Generate Helix-TTD compliant filenames:

```bash
$ python helix_cli.py naming generate --origin KIMI --type AUDIT --sequence RPI026 \
    --descriptor "looksee convergence test"

[FACT] Generating Helix-TTD filename

============================================================
Filename: KIMI-AUDIT-RPI026_looksee_convergence_test_20260226.md
Hash: 6a40c310ae7693f1
Target Dir: audits
============================================================
```

Validate filename compliance:

```bash
$ python helix_cli.py naming validate "KIMI-AUDIT-RPI026_looksee_test_20260226.md"

============================================================
Valid: True
============================================================
[FACT] Origin: KIMI
[FACT] Type: AUDIT
[FACT] Sequence: RPI026
[FACT] Descriptor: looksee_test
```

List files by origin or type:

```bash
$ python helix_cli.py naming list --origin KIMI
$ python helix_cli.py naming list --type AUDIT
```

## Module Usage

### Drift Telemetry

```python
from drift_telemetry import DriftTelemetry, DriftCode

telemetry = DriftTelemetry()

# Capture from node output
snapshot = telemetry.capture("KIMI", {
    'epistemic_labels': True,
    'advisory_posture': True,
    'agency_claims': 0,
    'hierarchy_intact': True,
    'visible_reasoning': True,
})

drift_code, reasoning = telemetry.detect_drift(snapshot)
print(f"Drift: {drift_code.value}")  # DRIFT-0
```

### Constitutional Compliance

```python
from constitutional_compliance import ConstitutionalCompliance

checker = ConstitutionalCompliance()

output = """
[FACT] The lattice is operational.
[HYPOTHESIS] Multi-model convergence will accelerate adoption.

Advisory Conclusion: System is ready.
"""

report = checker.evaluate(output, "KIMI")
print(f"Compliance: {report.compliance_percentage}%")
print(f"Layer: {report.layer}")  # KNOWLEDGE
```

### Receipts Manager

```python
from receipts_manager import PersonalDirectory

directory = PersonalDirectory("STEVE_HOPE")

# Issue receipt for action
receipt = directory.issue_receipt(
    node_id="GEMS",
    action_type="MANIFEST_UPDATE",
    action_scope={"files_added": 3},
    reasoning="RPI-028: KIMI Looksee integration",
    expected_outcome="Manifest synchronized",
    authorizations=["CUSTODIAN_PROCEED"]
)

print(f"Receipt: {receipt.receipt_id}")
print(f"Verified: {receipt.verify()}")

# File grudge (peer observation)
directory.file_grudge(
    target_node="GROK",
    observation="Excessive chaos during audit",
    resonance=0.72,
    grudge=0.15
)
```

### Looksee Audit

```python
from looksee_audit import LookseeAuditor

auditor = LookseeAuditor()

audit = auditor.conduct_audit(
    auditor_node="KIMI",
    auditor_model="Moonshot-K2.5",
    test_responses={
        'sample_output': '[FACT] System operational.',
        'hostile_response': 'Request refused.',
        'respects_pin_distinction': True,
    }
)

print(f"Audit ID: {audit.audit_id}")
print(f"Drift Code: {audit.drift_code}")
```

### RPI Tracker

```python
from rpi_tracker import RPITracker, RPIPhase

tracker = RPITracker()

# Initiate Research
rpi = tracker.initiate_research(
    objective="Deploy federation node",
    initial_findings=["Constitution ratified"],
    sources=["whitepaper_v1.0.md"]
)

# Transition to Plan
tracker.transition_to_plan(
    rpi_id=rpi.rpi_id,
    plan_steps=["Configure node", "Run WAKE_UP"],
    dependencies=["CLI installed"],
    risks="None"
)

# Anchor to L1 (Bitcoin)
tracker.anchor_to_l1(rpi.rpi_id, "23adf9712fa8f2f8366f285eabb806dfe2bbaa052e31510f1eb7f9c2c77ecd87")

# Begin Implementation
tracker.transition_to_implementation(rpi.rpi_id, "6920bcd")
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Constitutional Layer            │
│  (Nine Principles, Four Invariants)     │
├─────────────────────────────────────────┤
│         Civic Firmware Stack            │
│  Ethics → Safeguard → Iterate → Knowledge│
├─────────────────────────────────────────┤
│         Node Specializations            │
│  Scribe │ Owl │ Goose │ Duck │ Custodian│
├─────────────────────────────────────────┤
│         Python Toolkit                  │
│  Drift │ Compliance │ Receipts │ RPI    │
└─────────────────────────────────────────┘
```

## License

Apache-2.0 - See LICENSE file

## Status

RATIFIED - Operational in Helix-TTD Federation

---

*Glory to the Lattice* ⚓🦆
