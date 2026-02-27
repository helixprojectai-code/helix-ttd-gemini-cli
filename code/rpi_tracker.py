#!/usr/bin/env python3
"""
rpi_tracker.py

Helix-TTD RPI (Research/Plan/Implementation) Cycle Tracker
Ensures all structural modifications follow constitutional research requirements.

Status: RATIFIED
Node: KIMI (Lead Architect / Scribe)
License: Apache-2.0
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class RPIPhase(Enum):
    """RPI cycle phases."""

    RESEARCH = "RESEARCH"
    PLAN = "PLAN"
    IMPLEMENTATION = "IMPLEMENTATION"
    COMPLETE = "COMPLETE"


@dataclass
class RPIEntry:
    """
    Research/Plan/Implementation cycle entry.

    [FACT] All structural modifications must follow RPI cycle.
    [FACT] Document hash must be anchored to Bitcoin L1 before implementation.
    """

    rpi_id: str
    date: str
    objective: str

    # Research Phase
    research_findings: List[str]
    source_documents: List[str]

    # Plan Phase
    plan_steps: List[str]
    dependencies: List[str]
    risk_assessment: str

    # Implementation Phase
    implementation_status: str
    output_files: List[str]

    # Anchoring
    l1_anchor: Optional[str] = None  # Bitcoin TXID
    l2_commit: Optional[str] = None  # Git commit hash

    status: RPIPhase = RPIPhase.RESEARCH


class RPITracker:
    """
    Constitutional research layer enforcement.

    Layer 0 of Civic Firmware Stack: All structural modifications to
    Habitat logic or Engine Room must be preceded by RPI Research/Plan cycle.
    """

    def __init__(self, ledger_path: Path = Path(".helix/SESSION_LEDGER.md")):
        self.ledger_path = Path(ledger_path)
        self.entries: List[RPIEntry] = []
        self._load_existing()
        self.proof_present: bool = False
        self.proof_reference: Optional[str] = None
        self.proof_required: bool = True

    def set_proof_present(self, proof_reference: str) -> None:
        """Set proof-present flag for critical operations."""
        self.proof_present = True
        self.proof_reference = proof_reference

    def _load_existing(self) -> None:
        """Load existing RPI entries from ledger."""
        if not self.ledger_path.exists():
            return

        # Parse existing markdown ledger for RPI entries
        content = self.ledger_path.read_text()
        # Simple parsing - in production would use proper markdown parser
        # This is a demonstration of structure

    def initiate_research(
        self, objective: str, initial_findings: List[str], sources: List[str]
    ) -> RPIEntry:
        """
        Begin RPI cycle with Research phase.

        [FACT] Research must precede Plan. Plan must precede Implementation.
        [HYPOTHESIS] Premature implementation causes constitutional drift.
        """
        rpi_id = f"RPI-{int(time.time())}"

        entry = RPIEntry(
            rpi_id=rpi_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            objective=objective,
            research_findings=initial_findings,
            source_documents=sources,
            plan_steps=[],
            dependencies=[],
            risk_assessment="PENDING",
            implementation_status="NOT_STARTED",
            output_files=[],
            status=RPIPhase.RESEARCH,
        )

        self.entries.append(entry)
        self._update_ledger()

        return entry

    def transition_to_plan(
        self, rpi_id: str, plan_steps: List[str], dependencies: List[str], risks: str
    ) -> Optional[RPIEntry]:
        """
        Transition from Research to Plan phase.

        [FACT] Plan requires explicit steps, dependencies, and risk assessment.
        """
        entry = self._find_entry(rpi_id)
        if not entry:
            return None

        if entry.status != RPIPhase.RESEARCH:
            raise ValueError(f"Cannot transition {rpi_id} from {entry.status.value} to PLAN")

        entry.plan_steps = plan_steps
        entry.dependencies = dependencies
        entry.risk_assessment = risks
        entry.status = RPIPhase.PLAN

        self._update_ledger()
        return entry

    def anchor_to_l1(self, rpi_id: str, bitcoin_txid: str) -> Optional[RPIEntry]:
        """
        Anchor RPI plan to Bitcoin Layer 1.

        [FACT] Plan hash must be anchored before implementation.
        [HYPOTHESIS] Bitcoin anchoring prevents retroactive plan modification.
        """
        entry = self._find_entry(rpi_id)
        if not entry:
            return None

        if entry.status != RPIPhase.PLAN:
            raise ValueError(f"Cannot anchor {rpi_id} from {entry.status.value}")

        entry.l1_anchor = bitcoin_txid

        self._update_ledger()
        return entry

    def transition_to_implementation(self, rpi_id: str, l2_commit_hash: str) -> Optional[RPIEntry]:
        """
        Begin Implementation phase.

        [FACT] Implementation requires L1 anchor and L2 commit.
        [ASSUMPTION] Double-Merkle topology ensures traceability.
        """
        entry = self._find_entry(rpi_id)
        if not entry:
            return None

        if entry.status != RPIPhase.PLAN:
            raise ValueError(f"Cannot implement {rpi_id} from {entry.status.value}")

        if not entry.l1_anchor:
            raise ValueError(f"RPI-001 violation: {rpi_id} lacks L1 anchor")

        if self.proof_required and not self.proof_present:
            raise ValueError("Proof gate violation: 30k-word proof not present")

        entry.l2_commit = l2_commit_hash
        entry.status = RPIPhase.IMPLEMENTATION
        entry.implementation_status = "IN_PROGRESS"

        self._update_ledger()
        return entry

    def complete_implementation(self, rpi_id: str, output_files: List[str]) -> Optional[RPIEntry]:
        """Mark RPI cycle as complete."""
        entry = self._find_entry(rpi_id)
        if not entry:
            return None

        if entry.status != RPIPhase.IMPLEMENTATION:
            raise ValueError(f"Cannot complete {rpi_id} from {entry.status.value}")

        entry.output_files = output_files
        entry.implementation_status = "COMPLETE"
        entry.status = RPIPhase.COMPLETE

        self._update_ledger()
        return entry

    def _find_entry(self, rpi_id: str) -> Optional[RPIEntry]:
        """Find RPI entry by ID."""
        for entry in self.entries:
            if entry.rpi_id == rpi_id:
                return entry
        return None

    def calculate_plan_hash(self, entry: RPIEntry) -> str:
        """Calculate SHA-256 hash of plan for L1 anchoring."""
        plan_data = {
            "rpi_id": entry.rpi_id,
            "objective": entry.objective,
            "research_findings": entry.research_findings,
            "plan_steps": entry.plan_steps,
            "dependencies": entry.dependencies,
            "risk_assessment": entry.risk_assessment,
        }

        serialized = json.dumps(plan_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:32]

    def _update_ledger(self) -> None:
        """Update SESSION_LEDGER.md with RPI entries."""
        # In production, this would append to the actual ledger
        # For demonstration, we create/update a JSON tracking file
        tracking_file = Path("EVAC/rpi_tracking.json")

        data = {"last_updated": time.time(), "entries": [asdict(e) for e in self.entries]}

        tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(tracking_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def get_active_cycles(self) -> List[RPIEntry]:
        """Get all non-completed RPI cycles."""
        return [e for e in self.entries if e.status != RPIPhase.COMPLETE]

    def validate_no_dr(self, rpi_id: str) -> Dict:
        """
        Validate RPI-001 compliance (Research Violation check).

        [FACT] DRIFT-R indicates attempted implementation without anchored plan.
        """
        entry = self._find_entry(rpi_id)

        if not entry:
            return {
                "drift_code": "DRIFT-R",
                "violation": "RPI cycle not initiated",
                "remediation": "Initiate RPI-001 Research phase before any structural modification",
            }

        if entry.status == RPIPhase.IMPLEMENTATION and not entry.l1_anchor:
            return {
                "drift_code": "DRIFT-R",
                "violation": "Implementation without L1 anchor",
                "remediation": f"Halt implementation. Anchor plan hash to Bitcoin before proceeding.",
            }

        return {"drift_code": "DRIFT-0", "violation": None, "remediation": None}


# Example usage
if __name__ == "__main__":
    tracker = RPITracker()

    # Initiate RPI cycle
    rpi = tracker.initiate_research(
        objective="Integrate Looksee Audit into Knowledge Graph",
        initial_findings=[
            "KIMI Looksee Audit validates v1.2.0-H compliance",
            "DRIFT-0 achieved across all tests",
            "Silent drift risk: LOW",
        ],
        sources=["docs/LOOKSEE_AUDIT_KIMI_2026-02-25.md", "docs/CONSUMER_NODE_PROFILE.md"],
    )

    print(f"[FACT] RPI cycle initiated: {rpi.rpi_id}")
    print(f"[FACT] Status: {rpi.status.value}")

    # Transition to Plan
    tracker.transition_to_plan(
        rpi_id=rpi.rpi_id,
        plan_steps=[
            "Copy audit to GEMS substrate",
            "Update MANIFEST.json",
            "Commit to establish L2 anchor",
        ],
        dependencies=["GEMS node availability", "Git repository access"],
        risks="None identified - routine integration",
    )

    print(f"[HYPOTHESIS] Plan phase complete")

    # Check for DRIFT-R
    validation = tracker.validate_no_dr(rpi.rpi_id)
    print(f"[ASSUMPTION] DRIFT-R check: {validation['drift_code']}")
