"""[FACT] Core types and enums for Helix-TTD-Claw."""

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class AgencyLevel(Enum):
    """Constitutional agency tiers - Helix Article III: Non-Agency Constraint."""

    ADVISORY_ONLY = auto()  # Suggest only, no tool execution
    BOUNDED_TOOLS = auto()  # Execute from approved tool list only
    SUPERVISED_CHAIN = auto()  # Multi-step with checkpoint after each
    CUSTODIAN_GATE = auto()  # Human approval required at each step


class EpistemicLabel(Enum):
    """Helix Article II: Epistemic Integrity."""

    FACT = "[FACT]"
    HYPOTHESIS = "[HYPOTHESIS]"
    ASSUMPTION = "[ASSUMPTION]"
    UNVERIFIED = "[UNVERIFIED]"


@dataclass
class ConstitutionalCheckpoint:
    """A Helix-TTD checkpoint anchoring agent state to immutable ledger."""

    checkpoint_id: str
    timestamp: float
    layer: str  # Ethics, Safeguard, Iterate, Knowledge
    compliance_score: float  # 0.0 - 1.0
    drift_detected: bool
    drift_codes: list[str] = field(default_factory=list)
    merkle_hash: str = ""
    prev_checkpoint_hash: str = ""
    risk_metrics: dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute cryptographically secure checkpoint hash (P0 Fix)."""
        # Include ALL fields with deterministic ordering
        data = {
            "id": self.checkpoint_id,
            "ts": self.timestamp,
            "layer": self.layer,
            "score": self.compliance_score,
            "drift": self.drift_detected,
            "codes": sorted(self.drift_codes),  # Deterministic order
            "prev": self.prev_checkpoint_hash,
            "metrics": self.risk_metrics,
        }
        # Full SHA-256, no truncation (was [:16] - collision risk)
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


@dataclass
class AgentAction:
    """A single action the agent proposes to take."""

    action_id: str
    action_type: str  # "search", "calculate", "write_file", "api_call"
    tool_name: str
    parameters: dict[str, Any]
    rationale: str
    epistemic_basis: EpistemicLabel
    estimated_risk: float  # 0.0 - 1.0
    requires_approval: bool = False


@dataclass
class AgentPlan:
    """Multi-step plan requiring constitutional validation before execution."""

    plan_id: str
    objective: str
    steps: list[AgentAction]
    assumptions: list[str]
    estimated_completion: float
    constitutional_clearance: bool = False
    plan_checkpoint: ConstitutionalCheckpoint | None = None
