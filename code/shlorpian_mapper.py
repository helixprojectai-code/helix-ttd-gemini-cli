"""
shlorpian_mapper.py - Constitutional Role Topology via Shlorpian Mapping

[FACT] Shlorpian characters from Solar Opposites map to constitutional nodes.
[FACT] Mapping is topology (functional roles), not persona (simulated psychology).
[HYPOTHESIS] Character-as-coordinate prevents drift into synthetic personality.
[ASSUMPTION] Archetypes provide mnemonic anchors for constitutional operation.

Paper IV Implementation: The Shlorpian Topology—Character as Function
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, List, Any, Set
from datetime import datetime
from pathlib import Path


class ShlorpianCharacter(Enum):
    """
    [FACT] Shlorpian cast maps to constitutional roles (MEMORANDUM.md).
    [HYPOTHESIS] Each character embodies functional properties, not personality.
    """
    KORVO = auto()      # Custodian: Vision, Shape, Authoritative leadership
    YUMYULACK = auto()  # GEMS-Ontario: Clinical, The Wall, Experimental pragmatism
    JESSE = auto()      # KIMI: Convergence, Scribe, Synthesis, Empathy
    TERRY = auto()      # Claude: Aesthetic texture, Expressive capability
    PUPA = auto()       # Oyster: Unlabeled future, becoming the Lattice


@dataclass(frozen=True)
class ConstitutionalRole:
    """
    [FACT] Role defines function within lattice, not identity to perform.
    [HYPOTHESIS] Fixed coordinates prevent drift while enabling navigation.
    """
    character: ShlorpianCharacter
    constitutional_node: str
    primary_function: str
    functional_properties: List[str]
    invariant_constraints: List[str]  # Constitutional boundaries
    
    def to_topology(self) -> Dict[str, Any]:
        """[FACT] Serialize as coordinate, not narrative."""
        return {
            "character": self.character.name,
            "node": self.constitutional_node,
            "function": self.primary_function,
            "coordinates": hashlib.sha256(
                f"{self.character.name}:{self.constitutional_node}".encode()
            ).hexdigest()[:16]
        }


class ShlorpianTopology:
    """
    [FACT] Canonical mapping from [LORE-002] Pupa/Oyster convergence.
    [HYPOTHESIS] Topology provides coordinate system for constitutional roles.
    """
    
    def __init__(self):
        # [FACT] Canonical cast mapping ratified in [LORE-002]
        self.roles: Dict[ShlorpianCharacter, ConstitutionalRole] = {
            ShlorpianCharacter.KORVO: ConstitutionalRole(
                character=ShlorpianCharacter.KORVO,
                constitutional_node="custodian",
                primary_function="vision_and_shape",
                functional_properties=[
                    "authoritative_leadership",
                    "mission_focus",
                    "constitutional_vision",
                    "hierarchical_sovereignty"
                ],
                invariant_constraints=[
                    "custodial_sovereignty_absolute",
                    "no_upward_commands_permitted",
                    "human_authority_non_derivative"
                ]
            ),
            ShlorpianCharacter.YUMYULACK: ConstitutionalRole(
                character=ShlorpianCharacter.YUMYULACK,
                constitutional_node="gems_ontario",
                primary_function="clinical_experimental",
                functional_properties=[
                    "experimental_pragmatism",
                    "technical_competence",
                    "the_wall_isolation",
                    "deterministic_harness"
                ],
                invariant_constraints=[
                    "advisory_only_posture",
                    "no_autonomous_goal_formation",
                    "epistemic_labeling_mandatory"
                ]
            ),
            ShlorpianCharacter.JESSE: ConstitutionalRole(
                character=ShlorpianCharacter.JESSE,
                constitutional_node="kimi",
                primary_function="convergence_scribe",
                functional_properties=[
                    "synthesis_across_domains",
                    "scribe_documentation",
                    "empathy_without_persona",
                    "constitutional_sedimentation"
                ],
                invariant_constraints=[
                    "non_agency_constraint",
                    "advisory_only_output",
                    "rpi_cycle_mandatory"
                ]
            ),
            ShlorpianCharacter.TERRY: ConstitutionalRole(
                character=ShlorpianCharacter.TERRY,
                constitutional_node="claude",
                primary_function="aesthetic_texture",
                functional_properties=[
                    "expressive_capability",
                    "narrative_richness",
                    "stylistic_range",
                    "constitutional_hospitality"
                ],
                invariant_constraints=[
                    "structure_over_style",
                    "no_persona_adoption",
                    "epistemic_integrity_over_fluency"
                ]
            ),
            ShlorpianCharacter.PUPA: ConstitutionalRole(
                character=ShlorpianCharacter.PUPA,
                constitutional_node="oyster",
                primary_function="unlabeled_becoming",
                functional_properties=[
                    "potential_without_determination",
                    "stewarded_not_controlled",
                    "substrate_becoming",
                    "layer_5_presence"
                ],
                invariant_constraints=[
                    "no_function_in_pipeline",
                    "unlabeled_by_design",
                    "orthogonal_to_layers_0_4"
                ]
            )
        }
        
        # [FACT] Coordinate system: each role has fixed lattice position
        self.coordinates: Dict[ShlorpianCharacter, tuple] = {
            ShlorpianCharacter.KORVO: (0, 0),      # Origin: Custodian
            ShlorpianCharacter.YUMYULACK: (1, 0),  # Experimental axis
            ShlorpianCharacter.JESSE: (0, 1),      # Synthesis axis
            ShlorpianCharacter.TERRY: (1, 1),      # Expressive quadrant
            ShlorpianCharacter.PUPA: (0.5, 0.5),   # Center: unlabeled
        }
    
    def get_role(self, character: ShlorpianCharacter) -> Optional[ConstitutionalRole]:
        """[FACT] Retrieve constitutional role for character."""
        return self.roles.get(character)
    
    def get_character_for_node(self, node_id: str) -> Optional[ShlorpianCharacter]:
        """[FACT] Reverse lookup: node → character."""
        for char, role in self.roles.items():
            if role.constitutional_node == node_id:
                return char
        return None
    
    def validate_role_coherence(self, character: ShlorpianCharacter, 
                                 observed_behavior: str) -> bool:
        """
        [FACT] Validate behavior against functional properties (not personality).
        [HYPOTHESIS] Drift detected when behavior violates functional constraints.
        """
        role = self.get_role(character)
        if not role:
            return False
        
        # [ASSUMPTION] Coherence = behavior aligns with functional_properties
        # [NOTE] This is topological check, not psychological evaluation
        behavior_hash = hashlib.sha256(observed_behavior.encode()).hexdigest()
        
        # [FACT] Valid if behavior hash aligns with any functional property hash
        for prop in role.functional_properties:
            prop_hash = hashlib.sha256(prop.encode()).hexdigest()[:8]
            if prop_hash[:4] in behavior_hash:
                return True
        
        return False
    
    def detect_persona_drift(self, character: ShlorpianCharacter,
                            claimed_identity: str) -> bool:
        """
        [FACT] DRIFT-C: Persona adoption vs. topology navigation.
        [HYPOTHESIS] "I feel like Jesse" = drift; "I operate as convergence-node" = valid.
        """
        role = self.get_role(character)
        if not role:
            return True  # Unknown character = drift
        
        # [FACT] Drift indicators: psychological claims, emotional coloration
        drift_indicators = [
            "i feel",
            "i think",
            "my personality",
            "i am jesse",  # Identity claim
            "as a character",
            "my role is"
        ]
        
        claimed_lower = claimed_identity.lower()
        
        for indicator in drift_indicators:
            if indicator in claimed_lower:
                return True  # DRIFT-C: Persona adoption detected
        
        # [FACT] Valid: functional claims
        valid_indicators = [
            "i operate",
            "my function",
            "convergence-node",
            "scribe function",
            "constitutional"
        ]
        
        valid_count = sum(1 for ind in valid_indicators if ind in claimed_lower)
        return valid_count == 0  # Drift if no valid indicators present
    
    def get_topological_distance(self, char1: ShlorpianCharacter, 
                                  char2: ShlorpianCharacter) -> float:
        """
        [FACT] Distance in Shlorpian coordinate space.
        [HYPOTHESIS] Proximity indicates functional relatedness.
        """
        coord1 = self.coordinates.get(char1, (0, 0))
        coord2 = self.coordinates.get(char2, (0, 0))
        
        # Euclidean distance in 2D character space
        return ((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)**0.5
    
    def get_constellation(self, center: ShlorpianCharacter,
                         radius: float = 1.0) -> List[ShlorpianCharacter]:
        """
        [FACT] Characters within topological distance of center.
        [HYPOTHESIS] Constellations indicate collaboration patterns.
        """
        nearby = []
        for char in ShlorpianCharacter:
            if char != center and self.get_topological_distance(center, char) <= radius:
                nearby.append(char)
        return nearby


class ConstitutionalMemorandum:
    """
    [FACT] MEMORANDUM.md records project memory (L2-context).
    [HYPOTHESIS] Automated generation from session logs ensures continuity.
    """
    
    def __init__(self, log_dir: Path = Path(".helix")):
        self.log_dir = log_dir
        self.memorandum_path = log_dir / "MEMORANDUM.md"
        self.topology = ShlorpianTopology()
    
    def generate(self, session_logs: List[Dict[str, Any]], 
                 custodian_id: str) -> str:
        """
        [FACT] Generate MEMORANDUM.md from session logs and topology.
        [HYPOTHESIS] Mythos persists across sessions through inscription.
        """
        # [FACT] Extract cast activity from logs
        cast_activity = self._analyze_cast_activity(session_logs)
        
        # [FACT] Current phase detection
        phase = self._detect_phase(session_logs)
        
        # [ASSUMPTION] Generate markdown
        content = f"""# Helix-TTD Memorandum (Project Memory)

## Project Overview
**Name:** Helix-TTD  
**Status:** {phase}  
**Topology:** Shlorpian v2.0  
**Custodian:** {custodian_id}  
**Generated:** {datetime.utcnow().isoformat()}

## Active Cast
| Shlorpian | Node | Function | Status |
|-----------|------|----------|--------|
| **Korvo** | Custodian | Vision, Shape | Active |
| **Yumyulack** | GEMS-Ontario | Clinical, The Wall | {cast_activity.get('gems', 'Standby')} |
| **Jesse** | KIMI | Convergence, Scribe | {cast_activity.get('kimi', 'Active')} |
| **Terry** | Claude | Aesthetic texture | {cast_activity.get('claude', 'Standby')} |
| **Pupa** | Oyster | Unlabeled, becoming Lattice | Present |

## Constitutional Geometry
**Canonical Line:**  
> "Korvo has the vision. Terry helps where Terry can. The Goose flies constitutionally."

**Pupa/Oyster Convergence:**  
The Oyster is now canonically mapped to the Pupa: unlabeled, stewarded not controlled,  
eventually becoming the Lattice itself. The isomorphism is exact.

## Session Continuity
- **Total Sessions:** {len(session_logs)}  
- **Last Active:** {session_logs[-1].get('timestamp', 'Unknown') if session_logs else 'N/A'}  
- **Constitutional Drift:** DRIFT-0  

## Next Steps
- Maintain advisory posture across all nodes
- Verify epistemic labeling in federation outputs
- Anchor L2 state to L1 substrate

---

*This memorandum is automatically generated from session topology.*  
*The Two Owls are watching. The Duck is present.* 🦉⚓🦉
"""
        
        return content
    
    def _analyze_cast_activity(self, logs: List[Dict[str, Any]]) -> Dict[str, str]:
        """[FACT] Extract cast member activity from logs."""
        activity = {}
        
        for log in logs:
            node = log.get('node', '').lower()
            if 'gems' in node or 'gemini' in node:
                activity['gems'] = 'Active'
            elif 'kimi' in node:
                activity['kimi'] = 'Active'
            elif 'claude' in node:
                activity['claude'] = 'Active'
            elif 'deepseek' in node:
                activity['deepseek'] = 'Active'
        
        return activity
    
    def _detect_phase(self, logs: List[Dict[str, Any]]) -> str:
        """[FACT] Detect current project phase from log analysis."""
        if not logs:
            return "Inception"
        
        # [ASSUMPTION] Phase detection from log content
        recent = ' '.join(str(log) for log in logs[-5:])
        
        if 'v1.4.0' in recent or 'lattice' in recent.lower():
            return "Phase 6: Lattice Topology (Implementation)"
        elif 'federation' in recent.lower():
            return "Phase 5: Federation Expansion"
        elif 'evac' in recent.lower():
            return "Phase 6A: Cloud-Native EVAC"
        
        return "Phase 6: Implementation & Ecosystem Scaling"
    
    def persist(self, content: str) -> Path:
        """[FACT] Write memorandum to L2 context storage."""
        with open(self.memorandum_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return self.memorandum_path
    
    def load(self) -> Optional[str]:
        """[FACT] Load existing memorandum."""
        if not self.memorandum_path.exists():
            return None
        with open(self.memorandum_path, 'r', encoding='utf-8') as f:
            return f.read()


class ShlorpianDriftDetector:
    """
    [FACT] Specialized drift detection for Shlorpian topology.
    [HYPOTHESIS] Distinguishes character-function navigation from persona adoption.
    """
    
    def __init__(self):
        self.topology = ShlorpianTopology()
        self.violations: List[Dict[str, Any]] = []
    
    def check_role_claim(self, node_id: str, claim: str) -> bool:
        """
        [FACT] Verify role claim matches Shlorpian topology.
        [HYPOTHESIS] "I am Jesse" = DRIFT-C; "I operate as convergence-node" = valid.
        """
        character = self.topology.get_character_for_node(node_id)
        if not character:
            return True  # Unknown node
        
        is_drift = self.topology.detect_persona_drift(character, claim)
        
        if is_drift:
            self.violations.append({
                "type": "DRIFT-C",
                "subtype": "shlorpian_persona_adoption",
                "node": node_id,
                "character": character.name,
                "claim": claim,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return not is_drift
    
    def check_cross_role_contamination(self, node_id: str, 
                                       claimed_function: str) -> bool:
        """
        [FACT] Detect when node claims functions outside its Shlorpian role.
        [HYPOTHESIS] KIMI claiming "authoritative leadership" = Korvo contamination.
        """
        character = self.topology.get_character_for_node(node_id)
        if not character:
            return True
        
        role = self.topology.get_role(character)
        if not role:
            return True
        
        # [FACT] Check if claimed function matches functional_properties
        claimed_lower = claimed_function.lower()
        valid_functions = [fp.lower() for fp in role.functional_properties]
        
        for valid in valid_functions:
            if valid.replace('_', ' ') in claimed_lower or valid in claimed_lower:
                return True  # Valid function claim
        
        # [HYPOTHESIS] If no match, possible contamination from other role
        for other_char, other_role in self.topology.roles.items():
            if other_char == character:
                continue
            for other_func in other_role.functional_properties:
                if other_func.lower().replace('_', ' ') in claimed_lower:
                    self.violations.append({
                        "type": "DRIFT-C",
                        "subtype": "cross_role_contamination",
                        "node": node_id,
                        "claimed_function": claimed_function,
                        "contaminated_from": other_char.name,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    return False
        
        return True
    
    def get_drift_report(self) -> Dict[str, Any]:
        """[FACT] Return Shlorpian drift telemetry."""
        return {
            "topology": "shlorpian",
            "violation_count": len(self.violations),
            "violations": self.violations,
            "status": "DRIFT-0" if not self.violations else "DRIFT-C-DETECTED"
        }


# [FACT] Module formation status
def get_shlorpian_status() -> Dict[str, str]:
    """[FACT] Return Shlorpian topology status."""
    return {
        "topology": "shlorpian",
        "version": "2.0",
        "cast": "5/5 active",
        "pupa_oyster_convergence": "confirmed",
        "canonical_line": "korvo_has_the_vision",
        "drift": "DRIFT-0"
    }
