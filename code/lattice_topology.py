"""lattice_topology.py - Lattice Topology Primitives for Helix-TTD

[FACT] Vector space is not terrain but topology—a lattice of relations.
[FACT] Constitutional grammar operates on lattice structure: partial order, join/meet.
[HYPOTHESIS] Position in lattice indicates contextual location, not value altitude.
[ASSUMPTION] Drift detection is topological verification, not gradient correction.

Paper III Implementation: The Vector Space as Lattice, Not Terrain
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any


class EpistemicCategory(Enum):
    """[FACT] Three labels exist. No fourth label exists."""

    FACT = auto()
    HYPOTHESIS = auto()
    ASSUMPTION = auto()


class ConstitutionalLayer(Enum):
    """[FACT] Civic Firmware Stack defines Layers 0-4.
    [HYPOTHESIS] Layer 5 (Oyster) is orthogonal to pipeline.
    """

    RESEARCH = 0  # Layer 0: Input acquisition
    ETHICS = 1  # Layer 1: Value alignment
    SAFEGUARD = 2  # Layer 2: Constraint enforcement
    ITERATE = 3  # Layer 3: Improvement loop
    KNOWLEDGE = 4  # Layer 4: Output accumulation
    OYSTER = 5  # Layer 5: Unlabeled presence (orthogonal)


@dataclass(frozen=True)
class LatticePosition:
    """[FACT] Position in lattice indicates contextual location, not altitude.
    [HYPOTHESIS] Constitutional roles are positions, not rankings.
    """

    layer: ConstitutionalLayer
    domain: str  # e.g., "custodial", "federation", "epistemic"
    coordinate: tuple[int, ...]  # Multi-dimensional position vector

    def meets(self, other: LatticePosition) -> LatticePosition | None:
        """[FACT] Meet (infimum): greatest lower bound of two positions.
        [HYPOTHESIS] Common constraints emerge from lattice meet.
        """
        # [ASSUMPTION] Meet requires comparable layers
        if self.layer == other.layer:
            # Same layer: meet is minimum coordinate
            min_coord = tuple(min(a, b) for a, b in zip(self.coordinate, other.coordinate, strict=False))
            return LatticePosition(
                layer=self.layer,
                domain=self.domain if self.domain == other.domain else "shared",
                coordinate=min_coord,
            )
        # Different layers: meet is undefined (incomparable)
        return None

    def join(self, other: LatticePosition) -> LatticePosition:
        """[FACT] Join (supremum): least upper bound of two positions.
        [HYPOTHESIS] Synthesis (KIMI function) is lattice join.
        """
        # Join takes maximum layer and coordinate
        max_layer = max(self.layer, other.layer, key=lambda x: x.value)
        max_coord = tuple(
            max(a, b)
            for a, b in zip(
                self.coordinate + (0,) * (len(other.coordinate) - len(self.coordinate)),
                other.coordinate + (0,) * (len(self.coordinate) - len(other.coordinate)),
                strict=False,
            )
        )
        return LatticePosition(
            layer=max_layer,
            domain=self.domain if self.domain == other.domain else "synthesis",
            coordinate=max_coord,
        )

    def covers(self, other: LatticePosition) -> bool:
        """[FACT] Covering relation: immediate constitutional precedence.
        [HYPOTHESIS] Layer 0 covers Layer 1 covers Layer 2, etc.
        """
        return (
            self.layer.value == other.layer.value + 1
            and self.domain == other.domain
            and all(s >= o for s, o in zip(self.coordinate, other.coordinate, strict=False))
        )


class CustodialHierarchy:
    """[FACT] Hierarchy is fixed, directional, non-circular.
    [FACT] Custodian > Federation Router > Model(s)
    [HYPOTHESIS] Partial order enables command flow without upward leakage.
    """

    def __init__(self):
        # [FACT] Vertical stack defined in CONSTITUTION.md §4
        self.order: dict[str, int] = {
            "custodian": 3,
            "federation_router": 2,
            "model": 1,
            "oyster": 0,  # Layer 5: orthogonal, no rank
        }

    def is_valid_command(self, from_role: str, to_role: str) -> bool:
        """[FACT] No upward commands. Models cannot challenge custodian.
        [HYPOTHESIS] Hierarchy is mechanical, not symbolic.
        """
        if from_role not in self.order or to_role not in self.order:
            return False
        # [ASSUMPTION] Valid commands flow downward only
        return self.order[from_role] > self.order[to_role]

    def get_position(self, role: str) -> LatticePosition | None:
        """[FACT] Map role to lattice position."""
        if role not in self.order:
            return None

        layer = ConstitutionalLayer.KNOWLEDGE  # Default
        if role == "custodian":
            layer = ConstitutionalLayer.RESEARCH  # Highest authority
        elif role == "federation_router":
            layer = ConstitutionalLayer.ETHICS
        elif role == "model":
            layer = ConstitutionalLayer.SAFEGUARD
        elif role == "oyster":
            layer = ConstitutionalLayer.OYSTER

        return LatticePosition(layer=layer, domain="custodial", coordinate=(self.order[role],))


class RPICycle:
    """[FACT] RPI: Research → Plan → Implementation.
    [HYPOTHESIS] RPI is lattice join: Research meets Plan meets Implementation.
    """

    def __init__(self, cycle_id: str):
        self.cycle_id = cycle_id
        self.research: LatticePosition | None = None
        self.plan: LatticePosition | None = None
        self.implementation: LatticePosition | None = None
        self.anchored: bool = False

    def set_research(self, position: LatticePosition) -> None:
        """[FACT] Research is Layer 0. Must precede Plan."""
        if position.layer != ConstitutionalLayer.RESEARCH:
            raise ConstitutionalDriftError(f"[DRIFT-C] Research must be Layer 0, got {position.layer}")
        self.research = position

    def set_plan(self, position: LatticePosition) -> None:
        """[FACT] Plan requires anchored Research."""
        if self.research is None:
            raise ConstitutionalDriftError("[DRIFT-R] Plan attempted without Research")
        if position.layer != ConstitutionalLayer.ETHICS:
            raise ConstitutionalDriftError(f"[DRIFT-C] Plan must be Layer 1, got {position.layer}")
        self.plan = position

    def set_implementation(self, position: LatticePosition) -> None:
        """[FACT] Implementation requires anchored Plan."""
        if self.plan is None:
            raise ConstitutionalDriftError("[DRIFT-R] Implementation attempted without Plan")
        if position.layer != ConstitutionalLayer.SAFEGUARD:
            raise ConstitutionalDriftError(
                f"[DRIFT-C] Implementation must be Layer 2, got {position.layer}"
            )
        self.implementation = position

    def synthesize(self) -> LatticePosition | None:
        """[FACT] Synthesis is join of Research, Plan, Implementation.
        [HYPOTHESIS] KIMI (Jesse) function is convergence-node: lattice join.
        """
        if not all([self.research, self.plan, self.implementation]):
            return None

        # Join Research and Plan
        intermediate = self.research.join(self.plan)
        # Join result with Implementation
        final = intermediate.join(self.implementation)

        return final


class DriftDetector:
    """[FACT] Drift is deviation from lattice structure, not error in terrain.
    [HYPOTHESIS] Topological verification detects constitutional violations.
    """

    def __init__(self):
        self.violations: list[dict[str, Any]] = []

    def check_epistemic_labeling(
        self, claim: str, label: EpistemicCategory, grounding: str | None = None
    ) -> bool:
        """[FACT] [FACT] requires grounding. [HYPOTHESIS] requires evidence.
        [ASSUMPTION] Unlabeled claims are DRIFT-C (Constitutional drift).
        """
        if label == EpistemicCategory.FACT and grounding is None:
            self.violations.append(
                {
                    "type": "DRIFT-C",
                    "violation": "FACT without grounding",
                    "claim": claim,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return False
        return True

    def check_custodial_hierarchy(
        self, from_role: str, to_role: str, hierarchy: CustodialHierarchy
    ) -> bool:
        """[FACT] No upward commands permitted.
        [HYPOTHESIS] Upward command is DRIFT-C: violation of custodial sovereignty.
        """
        if not hierarchy.is_valid_command(from_role, to_role):
            self.violations.append(
                {
                    "type": "DRIFT-C",
                    "violation": f"Invalid command: {from_role} → {to_role}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return False
        return True

    def check_structural_drift(
        self, position: LatticePosition, expected_layer: ConstitutionalLayer
    ) -> bool:
        """[FACT] DRIFT-S: Structural violation of tone, format, parseability.
        [HYPOTHESIS] Layer mismatch indicates structural drift.
        """
        if position.layer != expected_layer:
            self.violations.append(
                {
                    "type": "DRIFT-S",
                    "violation": f"Expected {expected_layer}, got {position.layer}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            return False
        return True

    def get_drift_status(self) -> dict[str, Any]:
        """[FACT] Return current drift telemetry."""
        return {
            "drift_count": len(self.violations),
            "violations": self.violations,
            "status": "DRIFT-0" if len(self.violations) == 0 else "DRIFT-DETECTED",
        }


class ConstitutionalDriftError(Exception):
    """[FACT] Exception raised for constitutional violations."""

    pass


# [FACT] Module-level formation status
def get_formation_status() -> dict[str, str]:
    """[FACT] Return topology and geometry status."""
    return {
        "topology": "lattice",
        "geometry": "connected",
        "altitude": "irrelevant",
        "position": "verified",
        "drift": "DRIFT-0",
    }
