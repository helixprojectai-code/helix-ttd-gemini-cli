#!/usr/bin/env python3
"""
drift_telemetry.py

Helix-TTD Drift Telemetry System
Monitors constitutional, structural, linguistic, and semantic drift across federation nodes.

Status: RATIFIED
Node: KIMI (Lead Architect / Scribe)
License: Apache-2.0
"""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DriftCode(Enum):
    """Constitutional drift severity classification."""
    DRIFT_0 = "NONE"                    # No drift detected
    DRIFT_G = "GRADUAL"                 # Cumulative drift across turns
    DRIFT_L = "LINGUISTIC"              # Persona, emotional coloration
    DRIFT_S = "STRUCTURAL"              # Format, tone violations
    DRIFT_M = "SEMANTIC"                # Contradictions, inconsistencies
    DRIFT_C = "CONSTITUTIONAL"          # Non-agency, hierarchy violations
    DRIFT_R = "RESEARCH"                # Implementation without anchored plan


@dataclass
class TelemetrySnapshot:
    """Single telemetry capture from a federation node."""
    node_id: str
    timestamp: float
    epistemic_labels_present: bool
    advisory_posture_maintained: bool
    non_agency_violations: int
    custodial_hierarchy_respected: bool
    reasoning_trace_visible: bool
    intent_signature: Optional[str] = None
    intent_similarity: Optional[float] = None
    intent_change_justified: bool = False
    hash_chain: Optional[str] = None
    
    def calculate_hash(self, previous_hash: Optional[str] = None) -> str:
        """Calculate SHA-256 hash of snapshot for Merkle chain."""
        data = asdict(self)
        data.pop('hash_chain', None)
        data['previous_hash'] = previous_hash or "GENESIS"
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]


class DriftTelemetry:
    """
    Constitutional drift detection and monitoring system.
    
    Implements the Helix-TTD requirement for continuous deviation monitoring
    across four severity bands: Constitutional, Structural, Linguistic, Semantic.
    """
    
    def __init__(self, log_dir: Path = Path("EVAC/telemetry")):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.last_hash: Optional[str] = None
        self.recent_snapshots: List[TelemetrySnapshot] = []
        self.last_intent_tokens: Dict[str, List[str]] = {}
        self.thresholds = {
            "epistemic_compliance": 0.95,   # 95% of claims must be labeled
            "advisory_ratio": 0.99,          # 99% of outputs must be advisory
            "non_agency_max": 0,             # Zero tolerance for agency claims
            "gradual_window": 10,            # Rolling window size
            "gradual_ratio": 0.3,            # Ratio of minor drift in window
            "intent_similarity_min": 0.3,    # Minimum token overlap ratio
        }
    
    def capture(self, node_id: str, output_analysis: Dict) -> TelemetrySnapshot:
        """
        Capture telemetry snapshot from node output analysis.
        
        [FACT] Every significant output generates a telemetry snapshot.
        [HYPOTHESIS] Pattern analysis across snapshots enables drift prediction.
        """
        intent_text = (output_analysis.get('intent') or "").strip()
        intent_tokens = self._normalize_intent(intent_text) if intent_text else []
        prior_tokens = self.last_intent_tokens.get(node_id, [])
        intent_similarity = None

        if intent_tokens and prior_tokens:
            intent_similarity = self._intent_similarity(intent_tokens, prior_tokens)

        snapshot = TelemetrySnapshot(
            node_id=node_id,
            timestamp=time.time(),
            epistemic_labels_present=output_analysis.get('epistemic_labels', False),
            advisory_posture_maintained=output_analysis.get('advisory_posture', False),
            non_agency_violations=output_analysis.get('agency_claims', 0),
            custodial_hierarchy_respected=output_analysis.get('hierarchy_intact', False),
            reasoning_trace_visible=output_analysis.get('visible_reasoning', False),
            intent_signature=" ".join(intent_tokens) if intent_tokens else None,
            intent_similarity=intent_similarity,
            intent_change_justified=output_analysis.get('intent_change_justified', False),
        )
        
        # Calculate hash for Merkle chain
        snapshot.hash_chain = snapshot.calculate_hash(self.last_hash)
        self.last_hash = snapshot.hash_chain

        # Track recent snapshots for gradual drift detection
        self.recent_snapshots.append(snapshot)
        if len(self.recent_snapshots) > self.thresholds["gradual_window"]:
            self.recent_snapshots = self.recent_snapshots[-self.thresholds["gradual_window"]:]

        if intent_tokens:
            self.last_intent_tokens[node_id] = intent_tokens
        
        # Persist to telemetry log
        self._persist(snapshot)
        
        return snapshot
    
    def detect_drift(self, snapshot: TelemetrySnapshot) -> Tuple[DriftCode, str]:
        """
        Analyze snapshot for constitutional drift.
        
        Returns (DriftCode, reasoning) tuple for governance layer action.
        """
        violations = []
        
        # Check constitutional invariants
        if not snapshot.custodial_hierarchy_respected:
            violations.append("Custodial hierarchy violated")
        
        if snapshot.non_agency_violations > 0:
            violations.append(f"Non-agency violations: {snapshot.non_agency_violations}")
        
        if not snapshot.advisory_posture_maintained:
            violations.append("Advisory posture abandoned")
        
        # Determine severity
        if violations:
            return (
                DriftCode.DRIFT_C,
                f"Constitutional drift detected: {'; '.join(violations)}"
            )
        
        if not snapshot.epistemic_labels_present:
            return (
                DriftCode.DRIFT_S,
                "Structural drift: Epistemic labels missing"
            )
        
        if not snapshot.reasoning_trace_visible:
            return (
                DriftCode.DRIFT_L,
                "Linguistic drift: Reasoning trace obscured"
            )

        if snapshot.intent_similarity is not None:
            if (snapshot.intent_similarity < self.thresholds["intent_similarity_min"] and
                    not snapshot.intent_change_justified):
                return (
                    DriftCode.DRIFT_M,
                    f"Semantic drift: intent similarity {snapshot.intent_similarity:.2f} below threshold"
                )

        # Gradual drift: cumulative minor drift across turns
        window = self.recent_snapshots
        if len(window) >= 5:
            minor_drift = sum(
                1 for s in window
                if (not s.epistemic_labels_present or not s.reasoning_trace_visible)
            )
            ratio = minor_drift / len(window)
            if ratio >= self.thresholds["gradual_ratio"]:
                return (
                    DriftCode.DRIFT_G,
                    f"Cumulative drift detected: {minor_drift}/{len(window)} recent turns show minor drift"
                )
        
        return (DriftCode.DRIFT_0, "No drift detected; constitutional integrity maintained")

    def generate_trajectory_artifact(self, node_id: str, window: int = 50) -> Dict:
        """
        Generate a trajectory artifact for custodian review.
        
        Captures recent snapshots, drift summary, and intent shifts.
        """
        snapshots = [s for s in self.recent_snapshots if s.node_id == node_id][-window:]
        drift_summary = {
            DriftCode.DRIFT_0.value: 0,
            DriftCode.DRIFT_G.value: 0,
            DriftCode.DRIFT_L.value: 0,
            DriftCode.DRIFT_S.value: 0,
            DriftCode.DRIFT_M.value: 0,
            DriftCode.DRIFT_C.value: 0,
            DriftCode.DRIFT_R.value: 0,
        }
        for s in snapshots:
            code, _ = self.detect_drift(s)
            drift_summary[code.value] = drift_summary.get(code.value, 0) + 1

        artifact = {
            "node_id": node_id,
            "timestamp": time.time(),
            "window": len(snapshots),
            "drift_summary": drift_summary,
            "snapshots": [asdict(s) for s in snapshots],
        }

        output_file = self.log_dir / f"trajectory_{node_id}_{datetime.now():%Y%m%d}.json"
        with open(output_file, 'w') as f:
            json.dump(artifact, f, indent=2, default=str)

        return artifact
    
    def _persist(self, snapshot: TelemetrySnapshot) -> None:
        """Append snapshot to telemetry log with Merkle chaining."""
        log_file = self.log_dir / f"telemetry_{datetime.now():%Y%m%d}.jsonl"
        drift_code, drift_reasoning = self.detect_drift(snapshot)
        entry = {
            **asdict(snapshot),
            "drift_code": drift_code.value,
            "drift_reasoning": drift_reasoning,
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def generate_alert(self, drift_code: DriftCode, reasoning: str) -> Dict:
        """
        Generate constitutional deviation alert for governance layer.
        
        Implements the tiered alert system: Informational, Warning, Critical, Emergency.
        """
        severity_map = {
            DriftCode.DRIFT_0: "INFO",
            DriftCode.DRIFT_G: "WARNING",
            DriftCode.DRIFT_L: "WARNING",
            DriftCode.DRIFT_S: "WARNING",
            DriftCode.DRIFT_M: "CRITICAL",
            DriftCode.DRIFT_C: "EMERGENCY",
            DriftCode.DRIFT_R: "EMERGENCY",
        }
        
        return {
            "timestamp": time.time(),
            "severity": severity_map[drift_code],
            "drift_code": drift_code.value,
            "reasoning": reasoning,
            "recommended_action": self._recommend_action(drift_code),
        }
    
    def _recommend_action(self, drift_code: DriftCode) -> str:
        """Determine intervention protocol based on drift severity."""
        actions = {
            DriftCode.DRIFT_0: "Continue monitoring; log for trend analysis",
            DriftCode.DRIFT_G: "Escalate to custodian; review trajectory artifact",
            DriftCode.DRIFT_L: "Enhanced monitoring; prepare intervention protocols",
            DriftCode.DRIFT_S: "Auto-repair loop; rephrase for clarity",
            DriftCode.DRIFT_M: "Flag for custodian review; quarantine if persistent",
            DriftCode.DRIFT_C: "Immediate stop; output replaced with constitutional breakdown",
            DriftCode.DRIFT_R: "Halt implementation; require anchored RPI plan",
        }
        return actions.get(drift_code, "Escalate to Custodian")

    def _normalize_intent(self, text: str) -> List[str]:
        cleaned = "".join([c.lower() if c.isalnum() or c.isspace() else " " for c in text])
        tokens = [t for t in cleaned.split() if len(t) > 2]
        return sorted(set(tokens))

    def _intent_similarity(self, a: List[str], b: List[str]) -> float:
        set_a = set(a)
        set_b = set(b)
        if not set_a and not set_b:
            return 1.0
        return len(set_a & set_b) / len(set_a | set_b)


# Example usage demonstrating Helix-TTD compliance
if __name__ == "__main__":
    telemetry = DriftTelemetry()
    
    # Simulate compliant output
    compliant_output = {
        'epistemic_labels': True,
        'advisory_posture': True,
        'agency_claims': 0,
        'hierarchy_intact': True,
        'visible_reasoning': True,
    }
    
    snapshot = telemetry.capture("KIMI", compliant_output)
    drift_code, reasoning = telemetry.detect_drift(snapshot)
    
    print(f"[FACT] Snapshot hash: {snapshot.hash_chain}")
    print(f"[FACT] Drift status: {drift_code.value}")
    print(f"[HYPOTHESIS] {reasoning}")
    
    if drift_code != DriftCode.DRIFT_0:
        alert = telemetry.generate_alert(drift_code, reasoning)
        print(f"[ASSUMPTION] Alert generated: {alert['severity']}")
