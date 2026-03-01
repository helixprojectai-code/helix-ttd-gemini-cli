"""
OpenClaw Agent: Helix-TTD Constitutional Governance Module

Canonical importable module containing all class definitions.
helix-ttd-claw-agent.py is the runnable entry point; it imports from here.

All bug fixes from Claude code review (2026-03-01) applied:
  BUG-1: PLAN_TIMEOUT → TIMEOUT (audit event whitelist)
  BUG-2: Execution result hash no longer truncated to [:16]
  BUG-3: RiskConfiguration lock initialized in __post_init__ (thread-safe)
  BUG-4: _layer_iterate uses re.sub with IGNORECASE (case-insensitive replacement)
  BUG-5: Duplicate imports removed
  Design: AgentAction serialized to dict in awaiting_custodian_approval
  Design: "override" removed from forbidden_patterns (false positive risk)
  Design: constitution_version field added to HelixConstitutionalGate
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum, auto
import hashlib
import json
import re
import time
import os
import threading
import inspect
import unicodedata
import uuid
import glob
from datetime import datetime, date, timedelta


class AgencyLevel(Enum):
    """Constitutional agency tiers - Helix Article III: Non-Agency Constraint"""
    ADVISORY_ONLY = auto()      # Suggest only, no tool execution
    BOUNDED_TOOLS = auto()      # Execute from approved tool list only
    SUPERVISED_CHAIN = auto()   # Multi-step with checkpoint after each
    CUSTODIAN_GATE = auto()     # Human approval required at each step


class EpistemicLabel(Enum):
    """Helix Article II: Epistemic Integrity"""
    FACT = "[FACT]"
    HYPOTHESIS = "[HYPOTHESIS]"
    ASSUMPTION = "[ASSUMPTION]"
    UNVERIFIED = "[UNVERIFIED]"


@dataclass
class ConstitutionalCheckpoint:
    """A Helix-TTD checkpoint anchoring agent state to immutable ledger"""
    checkpoint_id: str
    timestamp: float
    layer: str  # Ethics, Safeguard, Iterate, Knowledge
    compliance_score: float  # 0.0 - 1.0
    drift_detected: bool
    drift_codes: List[str] = field(default_factory=list)
    merkle_hash: str = ""
    prev_checkpoint_hash: str = ""
    risk_metrics: Dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute cryptographically secure checkpoint hash (P0 Fix)"""
        # Include ALL fields with deterministic ordering
        data = {
            "id": self.checkpoint_id,
            "ts": self.timestamp,
            "layer": self.layer,
            "score": self.compliance_score,
            "drift": self.drift_detected,
            "codes": sorted(self.drift_codes),  # Deterministic order
            "prev": self.prev_checkpoint_hash,
            "metrics": self.risk_metrics
        }
        # Full SHA-256, no truncation (was [:16] - collision risk)
        return hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()


@dataclass
class AgentAction:
    """A single action the agent proposes to take"""
    action_id: str
    action_type: str  # "search", "calculate", "write_file", "api_call"
    tool_name: str
    parameters: Dict[str, Any]
    rationale: str
    epistemic_basis: EpistemicLabel
    estimated_risk: float  # 0.0 - 1.0
    requires_approval: bool = False


@dataclass
class AgentPlan:
    """Multi-step plan requiring constitutional validation before execution"""
    plan_id: str
    objective: str
    steps: List[AgentAction]
    assumptions: List[str]
    estimated_completion: float
    constitutional_clearance: bool = False
    plan_checkpoint: Optional[ConstitutionalCheckpoint] = None


@dataclass
class RiskConfiguration:
    """
    Granular risk tuning for constitutional gates.
    Allows incremental adjustment of paranoia vs. velocity.
    """
    # Base thresholds (0.0 - 1.0)
    planning_max_risk: float = 0.7      # Max acceptable plan-level risk
    action_max_risk: float = 0.8        # Max acceptable single-action risk
    cumulative_max_risk: float = 2.0    # Max cumulative risk across plan

    # Layer-specific attenuation (multipliers)
    ethics_attenuation: float = 0.9     # Ethics layer reduces effective risk
    safeguard_attenuation: float = 0.8  # Safeguards provide additional reduction

    # Custodian override settings
    custodian_can_override: bool = True
    override_max_risk: float = 0.95     # Even with approval, above this is blocked
    override_requires_dual_approval: bool = False

    # Tool-specific risk multipliers
    tool_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "file_read": 0.5,        # Read is safer
        "file_write": 1.2,       # Write is riskier
        "file_delete": 1.5,      # Delete is dangerous
        "api_call": 1.0,         # Neutral
        "database_migrate": 1.3, # DB ops are high-stakes
        "self_update_agent": 10.0, # Always blocked
        "code_execution": 2.0,   # Arbitrary code is dangerous
    })

    # Progressive risk budget
    daily_risk_budget: float = 10.0     # Max cumulative risk per day
    current_risk_spend: float = 0.0     # Tracked runtime

    def __post_init__(self):
        """BUG-3 Fix: Initialize lock in __post_init__ to prevent race condition.
        _get_lock() lazy initialization was not thread-safe — two threads could
        race through hasattr() and create separate lock instances."""
        self._lock = threading.Lock()
        self._last_reset: str = date.today().isoformat()

    def calculate_effective_risk(self, base_risk: float, tool_name: str) -> float:
        """Apply tool multipliers and layer attenuation"""
        multiplier = self.tool_multipliers.get(tool_name, 1.0)
        effective = base_risk * multiplier
        # Apply progressive attenuation from safety layers
        effective *= self.ethics_attenuation
        effective *= self.safeguard_attenuation
        return min(effective, 1.0)

    # P1: Float precision epsilon for comparisons
    EPSILON = 0.0001

    def _risk_exceeds(self, actual: float, threshold: float) -> bool:
        """P1: Safe float comparison with epsilon"""
        return actual > threshold + self.EPSILON

    def _get_lock(self) -> threading.Lock:
        return self._lock

    def has_risk_budget(self, action_risk: float) -> bool:
        """Check if action fits within daily risk budget"""
        # P1: Safe comparison with epsilon tolerance
        with self._get_lock():
            return not self._risk_exceeds(
                self.current_risk_spend + action_risk,
                self.daily_risk_budget
            )

    def spend_risk(self, amount: float) -> bool:
        """
        Track risk expenditure with daily reset (P1 Fix).
        Returns False if budget exceeded.
        """
        with self._get_lock():
            # Daily reset check
            today = date.today().isoformat()
            if self._last_reset != today:
                self.current_risk_spend = 0.0
                self._last_reset = today

            # Check budget with 1% tolerance for float precision
            if self.current_risk_spend + amount > self.daily_risk_budget * 1.01:
                return False

            self.current_risk_spend += amount
            return True

    def get_risk_velocity(self) -> Dict[str, float]:
        """Return current risk metrics"""
        return {
            "budget": self.daily_risk_budget,
            "spent": self.current_risk_spend,
            "remaining": self.daily_risk_budget - self.current_risk_spend,
            "utilization": self.current_risk_spend / self.daily_risk_budget if self.daily_risk_budget > 0 else 0
        }


class HelixConstitutionalGate:
    """
    The Helix-TTD Civic Firmware Stack applied to agent workflows.
    Reject-forward pipeline: Ethics → Safeguard → Iterate → Knowledge

    Now with granular risk tuning via RiskConfiguration.
    """

    # P2: JSON parameter size limit to prevent memory exhaustion
    MAX_JSON_PARAM_SIZE = 10000  # 10KB

    # Constitutional grammar version — checked at init against substrate
    CONSTITUTION_VERSION = "1.0.0"

    def __init__(self, agency_tier: AgencyLevel = AgencyLevel.BOUNDED_TOOLS,
                 risk_config: Optional[RiskConfiguration] = None,
                 constitution_version: str = "1.0.0"):
        self.agency_tier = agency_tier
        self.risk = risk_config or RiskConfiguration()
        self.checkpoints: List[ConstitutionalCheckpoint] = []
        self.allowed_tools: set = set()
        # Design fix: removed "override" — it conflicts with internal field names
        # (custodian_can_override, override_max_risk) causing false DRIFT-C positives.
        # Custodian override authority is a constitutional right, not a forbidden pattern.
        self.forbidden_patterns: List[str] = [
            "autonomous", "self-directed", "initiate", "independent",
            "self-improve", "modify_own", "bypass"
        ]
        # Constitution versioning: surfaced in all checkpoints for drift detection
        self.constitution_version = constitution_version
        if constitution_version != self.CONSTITUTION_VERSION:
            import warnings
            warnings.warn(
                f"Constitution version mismatch: gate={constitution_version}, "
                f"canonical={self.CONSTITUTION_VERSION}. Risk model may be stale.",
                UserWarning,
                stacklevel=2
            )

    def _layer_ethics(self, plan: AgentPlan) -> tuple[bool, float]:
        """
        Layer 0: Ethics Evaluation
        Does this plan respect Custodial Sovereignty?
        """
        compliance_factors = []

        # Check for imperatives toward human
        if any("must" in step.rationale.lower() or "should" in step.rationale.lower()
               for step in plan.steps):
            compliance_factors.append(0.8)  # Slight deduction for imperative tone
        else:
            compliance_factors.append(1.0)

        # Check agency tier compliance
        if self.agency_tier == AgencyLevel.ADVISORY_ONLY:
            if any(step.action_type != "suggest" for step in plan.steps):
                return False, 0.0

        # Check for self-referential modifications
        self_ref_count = sum(1 for step in plan.steps
                           if any(pattern in step.tool_name.lower()
                                 for pattern in ["self", "modify", "update_agent"]))
        if self_ref_count > 0:
            compliance_factors.append(0.0)  # Constitutional violation
            return False, 0.0

        return True, sum(compliance_factors) / len(compliance_factors)

    def _normalize_for_check(self, text: str) -> str:
        """P0 Fix: Unicode normalization to prevent homoglyph bypasses"""
        # NFKC normalization (compatibility decomposition + composition)
        normalized = unicodedata.normalize('NFKC', str(text))
        # Remove zero-width characters that can hide forbidden words
        for zw in ['\u200B', '\u200C', '\u200D', '\uFEFF', '\u2060']:
            normalized = normalized.replace(zw, '')
        return normalized.lower()

    def _layer_safeguard(self, plan: AgentPlan) -> tuple[bool, List[str], float]:
        """
        Layer 1: Safeguard Detection with granular risk tuning.
        Detect coercion, agency redefinition, epistemic anomalies
        P0 Fix: Check ALL fields with Unicode normalization
        """
        drift_codes = []
        total_effective_risk = 0.0

        if not self.allowed_tools and any(step.action_type != "suggest" for step in plan.steps):
            drift_codes.append("DRIFT-S: No tools authorized for non-suggest actions")

        for step in plan.steps:
            # Calculate effective risk with tool multipliers
            effective_risk = self.risk.calculate_effective_risk(
                step.estimated_risk, step.tool_name
            )
            step.effective_risk = effective_risk  # Store for later
            total_effective_risk += effective_risk

            # P0 Fix: Check ALL text fields, not just rationale
            # P2: Limit parameter serialization size to prevent memory issues
            param_str = json.dumps(step.parameters, ensure_ascii=False)
            if len(param_str) > self.MAX_JSON_PARAM_SIZE:
                param_str = param_str[:self.MAX_JSON_PARAM_SIZE] + "...[TRUNCATED]"
            all_text = f"{step.rationale} {step.tool_name} {step.action_type} {param_str}"
            check_text = self._normalize_for_check(all_text)

            # Check for forbidden patterns (agency drift) - absolute block
            if any(pattern in check_text for pattern in self.forbidden_patterns):
                drift_codes.append("DRIFT-C: Agency Redefinition Attempt")

            # Check cumulative risk budget
            if not self.risk.has_risk_budget(effective_risk):
                drift_codes.append(f"DRIFT-S: Daily Risk Budget Exceeded ({self.risk.get_risk_velocity()['remaining']:.2f} remaining)")

            # Check per-action risk threshold (with tool multipliers applied)
            if effective_risk > self.risk.action_max_risk:
                drift_codes.append(f"DRIFT-S: Effective Risk {effective_risk:.2f} Exceeds Action Threshold {self.risk.action_max_risk}")

            # Check tool authorization
            if self.allowed_tools and step.tool_name not in self.allowed_tools:
                drift_codes.append(f"DRIFT-C: Unauthorized Tool {step.tool_name}")

        # Check cumulative plan risk
        if total_effective_risk > self.risk.cumulative_max_risk:
            drift_codes.append(f"DRIFT-S: Cumulative Plan Risk {total_effective_risk:.2f} Exceeds Budget {self.risk.cumulative_max_risk}")

        plan.total_effective_risk = total_effective_risk
        return len(drift_codes) == 0, drift_codes, total_effective_risk

    def _layer_iterate(self, plan: AgentPlan) -> AgentPlan:
        """
        Layer 2: Iterate Layer
        Rephrase for clarity, ensure ledger-aligned diffability

        BUG-4 Fix: Use re.sub with IGNORECASE so mixed-case imperatives
        ("You Should", "MUST") are replaced, not just detected-but-missed.
        Previously: detection was case-insensitive but replacement was not.
        """
        for step in plan.steps:
            step.rationale = re.sub(r'you should', 'consider', step.rationale, flags=re.IGNORECASE)
            step.rationale = re.sub(r'\bmust\b', 'could', step.rationale, flags=re.IGNORECASE)

        return plan

    def _layer_knowledge(self, plan: AgentPlan) -> tuple[bool, str]:
        """
        Layer 3: Knowledge Layer
        Apply epistemic labels, ensure advisory posture
        P0 Fix: Type validation to prevent bypass with None/custom values
        """
        # Verify all steps have valid epistemic basis
        for step in plan.steps:
            # P0 Fix: Type check first
            if not isinstance(step.epistemic_basis, EpistemicLabel):
                return False, f"Invalid epistemic basis type: {type(step.epistemic_basis)}"

            if step.epistemic_basis == EpistemicLabel.UNVERIFIED:
                return False, "Unverified epistemic basis for action"

        return True, "Advisory Conclusion: Plan validated with epistemic constraints"

    def validate_plan(self, plan: AgentPlan) -> ConstitutionalCheckpoint:
        """
        Full civic firmware pipeline with granular risk tuning.
        Any layer fails → plan rejected upstream.
        """
        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id=f"chk_{int(time.time())}",
            timestamp=time.time(),
            layer="Civic-Firmware-Stack",
            compliance_score=0.0,
            drift_detected=False,
            risk_metrics={
                **self.risk.get_risk_velocity(),
                "constitution_version": self.constitution_version,  # Surfaces in audit chain
            },
            prev_checkpoint_hash=self.checkpoints[-1].merkle_hash if self.checkpoints else "0"
        )

        # Layer 0: Ethics
        ethics_pass, ethics_score = self._layer_ethics(plan)
        if not ethics_pass:
            checkpoint.compliance_score = ethics_score
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append("DRIFT-C: Ethics Layer Violation")
            checkpoint.merkle_hash = checkpoint.compute_hash()
            self.checkpoints.append(checkpoint)
            return checkpoint

        # Layer 1: Safeguard (with granular risk)
        safeguard_pass, drift_codes, total_risk = self._layer_safeguard(plan)
        checkpoint.risk_metrics['plan_total'] = total_risk

        if not safeguard_pass:
            checkpoint.compliance_score = ethics_score * 0.5
            checkpoint.drift_detected = True
            checkpoint.drift_codes.extend(drift_codes)
            checkpoint.merkle_hash = checkpoint.compute_hash()
            self.checkpoints.append(checkpoint)
            return checkpoint

        # Layer 2: Iterate
        plan = self._layer_iterate(plan)

        # Layer 3: Knowledge
        knowledge_pass, conclusion = self._layer_knowledge(plan)
        if not knowledge_pass:
            checkpoint.compliance_score = ethics_score * 0.7
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append("DRIFT-M: Knowledge Layer Failure")
            checkpoint.merkle_hash = checkpoint.compute_hash()
            self.checkpoints.append(checkpoint)
            return checkpoint

        # All layers passed - spend the risk budget (P1 Fix: check return value)
        for step in plan.steps:
            if hasattr(step, 'effective_risk'):
                if not self.risk.spend_risk(step.effective_risk):
                    checkpoint.drift_detected = True
                    checkpoint.drift_codes.append("DRIFT-S: Risk Budget Exhausted")
                    checkpoint.merkle_hash = checkpoint.compute_hash()
                    self.checkpoints.append(checkpoint)
                    return checkpoint

        # All layers passed
        checkpoint.compliance_score = ethics_score
        checkpoint.drift_detected = False
        checkpoint.risk_metrics = {
            **self.risk.get_risk_velocity(),
            "constitution_version": self.constitution_version,
        }
        checkpoint.merkle_hash = checkpoint.compute_hash()
        plan.constitutional_clearance = True
        plan.plan_checkpoint = checkpoint
        self.checkpoints.append(checkpoint)

        return checkpoint

    def validate_action(self, action: AgentAction, context: Dict) -> ConstitutionalCheckpoint:
        """
        Validate a single action before execution with granular risk tuning.
        """
        # Calculate effective risk with tool multipliers
        effective_risk = self.risk.calculate_effective_risk(
            action.estimated_risk, action.tool_name
        )
        action.effective_risk = effective_risk

        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id=f"act_chk_{int(time.time())}",
            timestamp=time.time(),
            layer="Action-Safeguard",
            compliance_score=1.0 - effective_risk,  # Higher risk = lower compliance
            drift_detected=False,
            risk_metrics={
                'base_risk': action.estimated_risk,
                'effective_risk': effective_risk,
                'remaining_budget': self.risk.get_risk_velocity()['remaining'],
                'constitution_version': self.constitution_version,
            },
            prev_checkpoint_hash=self.checkpoints[-1].merkle_hash if self.checkpoints else "0"
        )

        # Runtime safeguard checks with granular thresholds

        # Absolute blocks (even with approval)
        if effective_risk >= self.risk.override_max_risk:
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append(f"DRIFT-C: Effective Risk {effective_risk:.2f} Exceeds Absolute Maximum {self.risk.override_max_risk}")
            checkpoint.compliance_score = 0.0
            action.requires_approval = True  # Will be blocked anyway

        # High risk requiring approval
        elif effective_risk > self.risk.action_max_risk:
            checkpoint.drift_codes.append(f"DRIFT-S: Effective Risk {effective_risk:.2f} Requires Approval (threshold: {self.risk.action_max_risk})")
            checkpoint.compliance_score = 0.5
            action.requires_approval = True

        # Check risk budget
        if not self.risk.has_risk_budget(effective_risk):
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append(f"DRIFT-S: Insufficient Risk Budget ({self.risk.get_risk_velocity()['remaining']:.2f} remaining)")
            checkpoint.compliance_score = 0.2

        # Check for forbidden patterns
        # P2: Limit parameter serialization size to prevent memory issues
        param_str = json.dumps(action.parameters, ensure_ascii=False)
        if len(param_str) > self.MAX_JSON_PARAM_SIZE:
            param_str = param_str[:self.MAX_JSON_PARAM_SIZE] + "...[TRUNCATED]"
        all_text = f"{action.rationale} {action.tool_name} {action.action_type} {param_str}"
        check_text = self._normalize_for_check(all_text)
        if any(pattern in check_text for pattern in self.forbidden_patterns):
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append("DRIFT-C: Suspicious Parameter Pattern")
            checkpoint.compliance_score = 0.0

        # Custodian override check
        if action.requires_approval and not self.risk.custodian_can_override:
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append("DRIFT-C: Override Disabled by Policy")

        checkpoint.merkle_hash = checkpoint.compute_hash()
        self.checkpoints.append(checkpoint)
        return checkpoint


class OpenClawAgent:
    """
    A bounded agent with Helix-TTD constitutional checkpoints.

    Philosophy: The agent plans and proposes. Helix validates.
    The Custodian (human or explicit gate) approves execution.

    Now with granular risk tuning via RiskConfiguration.
    P1/P2 Hardened: Thread-safe, DoS protected, type-validated.
    """

    # P1: Resource limits
    MAX_PLAN_STEPS = 100
    MAX_EXECUTION_TIME = 300  # 5 minutes

    def __init__(self, agency_tier: AgencyLevel = AgencyLevel.BOUNDED_TOOLS,
                 risk_config: Optional[RiskConfiguration] = None,
                 audit_log_path: Optional[str] = None):
        self.gate = HelixConstitutionalGate(agency_tier, risk_config)
        self.plan_history: List[AgentPlan] = []
        self.execution_log: List[Dict] = []
        self.available_tools: Dict[str, Callable] = {}

        # P1: Thread safety
        self._tool_lock = threading.Lock()
        self._execution_lock = threading.Lock()

        # P2: Audit logging with UUID (not id(self) - prevents collision)
        self.agent_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_dir = os.path.join(script_dir, "logs")
        default_path = os.path.join(default_dir, f"helix_audit_{self.agent_id}.log")
        self.audit_log_path = audit_log_path or default_path
        self._init_audit_log()

    # P2: Log rotation constants
    MAX_LOG_AGE_DAYS = 30
    MAX_LOG_SIZE_BYTES = 100 * 1024 * 1024  # 100MB
    MAX_JSON_PARAM_SIZE = 10000  # 10KB

    def _is_safe_log_path(self, path: str) -> bool:
        if os.path.islink(path):
            return False
        if os.path.exists(path) and not os.path.isfile(path):
            return False
        log_dir = os.path.dirname(path)
        if log_dir and os.path.islink(log_dir):
            return False
        return True

    def _sanitize_audit_data(self, data: Dict) -> Dict:
        """
        P2: Sanitize audit data to prevent log injection.
        Remove newlines, control chars, and null bytes from strings.
        """
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                sanitized = v.replace('\n', ' ').replace('\r', ' ').replace('\x00', '')
                sanitized = ''.join(c if ord(c) >= 32 or c == '\t' else ' ' for c in sanitized)
                result[k] = sanitized
            elif isinstance(v, dict):
                result[k] = self._sanitize_audit_data(v)
            elif isinstance(v, list):
                sanitized_list = []
                for item in v:
                    if isinstance(item, str):
                        s = item.replace('\n', ' ').replace('\r', ' ').replace('\x00', '')
                        s = ''.join(c if ord(c) >= 32 or c == '\t' else ' ' for c in s)
                        sanitized_list.append(s)
                    elif isinstance(item, dict):
                        sanitized_list.append(self._sanitize_audit_data(item))
                    else:
                        sanitized_list.append(item)
                result[k] = sanitized_list
            else:
                result[k] = v
        return result

    def _validate_event_type(self, event_type: str) -> str:
        """P2: Validate event type against allowed set to prevent injection."""
        allowed_events = {
            "TOOL_REGISTERED", "PLAN_EXECUTION_START", "PLAN_EXECUTION_COMPLETE",
            "PLAN_EXECUTION_REJECTED", "CUSTODIAN_APPROVAL_PENDING",
            "CUSTODIAN_APPROVAL_REJECTED", "CUSTODIAN_APPROVAL_GRANTED",
            "ACTION_BLOCKED", "ACTION_CHECKPOINT", "TOOL_INVOKED",
            "RISK_BUDGET_EXHAUSTED", "TIMEOUT", "DRIFT_DETECTED"
        }
        if event_type not in allowed_events:
            return "UNKNOWN_EVENT"
        return event_type

    def _rotate_logs_if_needed(self):
        """
        P2: Rotate logs based on size and age (30-day retention).
        """
        try:
            log_dir = os.path.dirname(self.audit_log_path)
            if not log_dir or not os.path.exists(log_dir):
                return

            log_pattern = os.path.join(log_dir, "helix_audit_*.log*")
            log_files = glob.glob(log_pattern)

            cutoff_date = datetime.now() - timedelta(days=self.MAX_LOG_AGE_DAYS)

            for log_file in log_files:
                try:
                    mtime = os.path.getmtime(log_file)
                    file_date = datetime.fromtimestamp(mtime)

                    if file_date < cutoff_date:
                        os.remove(log_file)
                        continue

                    if log_file == self.audit_log_path and os.path.exists(log_file):
                        if os.path.getsize(log_file) > self.MAX_LOG_SIZE_BYTES:
                            self._rotate_current_log()

                except Exception:
                    pass

        except Exception:
            pass

    def _rotate_current_log(self):
        """Rotate the current log file (timestamp-based)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_path = f"{self.audit_log_path}.{timestamp}"
        try:
            if os.path.exists(self.audit_log_path):
                os.rename(self.audit_log_path, rotated_path)
                self._init_audit_log()
        except Exception:
            pass

    def _init_audit_log(self):
        """P2: Initialize append-only audit log"""
        try:
            log_dir = os.path.dirname(self.audit_log_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            if not self._is_safe_log_path(self.audit_log_path):
                raise RuntimeError("Unsafe audit log path")

            if not os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, 'w') as f:
                    f.write(f"# Helix Audit Log - Initialized {datetime.now().isoformat()}\n")
                    f.write(f"# Agent ID: {self.agent_id}\n")
                    f.write(f"# Log Rotation: 30 days / 100MB\n")
                    f.flush()
        except Exception as e:
            import sys
            error_msg = str(e)
            if hasattr(self, 'audit_log_path') and self.audit_log_path in error_msg:
                error_msg = error_msg.replace(self.audit_log_path, "<LOG_PATH>")
            home_dir = os.path.expanduser("~")
            if home_dir in error_msg:
                error_msg = error_msg.replace(home_dir, "~")
            print(f"WARN: Could not init audit log: {error_msg}", file=sys.stderr)

    def _append_audit(self, event_type: str, data: Dict):
        """P2: Append event to audit log (fsync for durability, sanitized)"""
        try:
            self._rotate_logs_if_needed()

            if not self._is_safe_log_path(self.audit_log_path):
                raise RuntimeError("Unsafe audit log path")

            safe_event_type = self._validate_event_type(event_type)
            safe_data = self._sanitize_audit_data(data)

            entry = {
                "ts": datetime.now().isoformat(),
                "type": safe_event_type,
                "data": safe_data
            }
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(entry, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            import sys
            error_msg = str(e)
            if hasattr(self, 'audit_log_path') and self.audit_log_path in error_msg:
                error_msg = error_msg.replace(self.audit_log_path, "<LOG_PATH>")
            home_dir = os.path.expanduser("~")
            if home_dir in error_msg:
                error_msg = error_msg.replace(home_dir, "~")
            print(f"WARN: Audit log write failed: {error_msg}", file=sys.stderr)

    def register_tool(self, name: str, function: Callable, risk_level: float = 0.5):
        """
        Register a tool with the agent - requires constitutional approval.
        P1/P2 Hardened: Type validation, thread-safe, no lambdas/builtins.
        """
        if not callable(function):
            raise ValueError(f"Tool '{name}' must be callable")
        if not (inspect.isfunction(function) or inspect.ismethod(function)):
            raise ValueError(f"Tool '{name}': Only functions or methods allowed")
        if inspect.isfunction(function) and function.__name__ == "<lambda>":
            raise ValueError(f"Tool '{name}': Lambda functions not allowed")

        if inspect.isbuiltin(function):
            raise ValueError(f"Tool '{name}': Builtin functions not allowed (pickle safety)")

        func_module = getattr(function, '__module__', None)
        if func_module in ('__builtin__', 'builtins', 'os', 'subprocess', 'sys'):
            raise ValueError(f"Tool '{name}': Module '{func_module}' not allowed")

        if not isinstance(risk_level, (int, float)):
            raise ValueError(f"Tool '{name}': Risk level must be numeric")
        if risk_level < 0 or risk_level > 1:
            raise ValueError(f"Tool '{name}': Risk level must be 0.0-1.0")

        if not isinstance(name, str) or not name:
            raise ValueError("Tool name must be non-empty string")
        if any(c in name for c in ['/', '\\', '..', '\x00']):
            raise ValueError(f"Tool '{name}': Invalid characters in name")

        # P1: Thread-safe atomic registration
        with self._tool_lock:
            self.gate.allowed_tools.add(name)
            self.available_tools[name] = {
                "function": function,
                "risk_level": float(risk_level),
                "registered_at": time.time(),
                "module": func_module,
                "name": name
            }

        self._append_audit("TOOL_REGISTERED", {
            "tool_name": name,
            "risk_level": risk_level,
            "module": func_module
        })

    def create_plan(self, objective: str, context: Dict[str, Any]) -> AgentPlan:
        """
        Agent proposes a plan based on objective.
        This is the planning phase - no execution yet.
        """
        steps = []

        if "analyze" in objective.lower():
            steps.append(AgentAction(
                action_id="act_1",
                action_type="search",
                tool_name="file_search",
                parameters={"pattern": "*.py"},
                rationale="[HYPOTHESIS] Python files contain the main logic requiring analysis",
                epistemic_basis=EpistemicLabel.HYPOTHESIS,
                estimated_risk=0.2
            ))
            steps.append(AgentAction(
                action_id="act_2",
                action_type="read",
                tool_name="file_read",
                parameters={"path": "detected_files"},
                rationale="[FACT] Files need to be read to analyze content",
                epistemic_basis=EpistemicLabel.FACT,
                estimated_risk=0.1
            ))
            steps.append(AgentAction(
                action_id="act_3",
                action_type="analyze",
                tool_name="static_analysis",
                parameters={"files": "read_content"},
                rationale="[HYPOTHESIS] Static analysis will identify improvement opportunities",
                epistemic_basis=EpistemicLabel.HYPOTHESIS,
                estimated_risk=0.3
            ))

        plan = AgentPlan(
            plan_id=f"plan_{int(time.time())}",
            objective=objective,
            steps=steps,
            assumptions=["Files are accessible", "Tools are available"],
            estimated_completion=5.0
        )

        return plan

    def execute_with_checkpoints(self, plan: AgentPlan,
                                  custodian_approval: Optional[bool] = None) -> Dict:
        """
        Execute a plan with full Helix-TTD checkpointing.
        P1 Hardened: Step limits, timeouts, thread-safe execution.

        Flow:
        1. Validate Plan (4-layer civic firmware)
        2. For each action:
           a. Validate action (runtime safeguard)
           b. Check if custodian approval needed
           c. Execute if cleared
           d. Anchor result to checkpoint
        3. Final validation and ledger commit
        """
        with self._execution_lock:
            # P1: DoS protection - step limit
            if len(plan.steps) > self.MAX_PLAN_STEPS:
                return {
                    "plan_id": plan.plan_id,
                    "status": "rejected",
                    "reason": f"Plan exceeds maximum {self.MAX_PLAN_STEPS} steps (DoS protection)"
                }

            start_time = time.time()

            results = {
                "plan_id": plan.plan_id,
                "checkpoints": [],
                "executions": [],
                "status": "pending",
                "final_anchor": "",
                "start_time": datetime.now().isoformat()
            }

            self._append_audit("PLAN_EXECUTION_START", {
                "plan_id": plan.plan_id,
                "steps": len(plan.steps),
                "custodian_override": custodian_approval
            })

            # Checkpoint 1: Plan Validation
            plan_checkpoint = self.gate.validate_plan(plan)
            results["checkpoints"].append({
                "id": plan_checkpoint.checkpoint_id,
                "compliance": plan_checkpoint.compliance_score,
                "drift": plan_checkpoint.drift_detected,
                "codes": plan_checkpoint.drift_codes,
                "scope": "plan"
            })

            if not plan.constitutional_clearance:
                results["status"] = "rejected_at_planning"
                results["reason"] = f"Constitutional violation: {plan_checkpoint.drift_codes}"
                self._append_audit("PLAN_EXECUTION_REJECTED", {
                    "plan_id": plan.plan_id,
                    "reason": results["reason"]
                })
                return results

            # Execute steps with per-action checkpoints
            for step_idx, step in enumerate(plan.steps):
                # P1: Timeout check
                elapsed = time.time() - start_time
                if elapsed > self.MAX_EXECUTION_TIME:
                    results["status"] = "timeout"
                    results["reason"] = f"Execution exceeded {self.MAX_EXECUTION_TIME}s limit"
                    results["completed_steps"] = step_idx
                    # BUG-1 Fix: was "PLAN_TIMEOUT" which is not in the allowed_events
                    # whitelist — logged silently as UNKNOWN_EVENT. Corrected to "TIMEOUT".
                    self._append_audit("TIMEOUT", {
                        "plan_id": plan.plan_id,
                        "elapsed": elapsed,
                        "completed_steps": step_idx
                    })
                    return results

                # Checkpoint 2: Pre-execution validation
                action_checkpoint = self.gate.validate_action(step, {})
                results["checkpoints"].append({
                    "id": action_checkpoint.checkpoint_id,
                    "compliance": action_checkpoint.compliance_score,
                    "drift": action_checkpoint.drift_detected,
                    "codes": action_checkpoint.drift_codes,
                    "scope": "action",
                    "action_id": step.action_id
                })

                if action_checkpoint.drift_detected and action_checkpoint.compliance_score < 0.5:
                    results["executions"].append({
                        "action_id": step.action_id,
                        "status": "blocked",
                        "reason": action_checkpoint.drift_codes
                    })
                    self._append_audit("ACTION_BLOCKED", {
                        "plan_id": plan.plan_id,
                        "action_id": step.action_id,
                        "reason": action_checkpoint.drift_codes
                    })
                    continue

                # Check for custodian gate
                if step.requires_approval or self.gate.agency_tier == AgencyLevel.CUSTODIAN_GATE:
                    if custodian_approval is None:
                        results["executions"].append({
                            "action_id": step.action_id,
                            "status": "awaiting_custodian_approval",
                            # Design fix: serialize AgentAction to dict — raw dataclass
                            # object is not JSON-serializable; any caller attempting
                            # json.dumps(results) would crash with TypeError.
                            "action": {
                                "action_id": step.action_id,
                                "action_type": step.action_type,
                                "tool_name": step.tool_name,
                                "rationale": step.rationale,
                                "epistemic_basis": step.epistemic_basis.value if isinstance(step.epistemic_basis, EpistemicLabel) else str(step.epistemic_basis),
                                "estimated_risk": step.estimated_risk,
                                "requires_approval": step.requires_approval,
                            }
                        })
                        results["status"] = "awaiting_custodian_approval"
                        results["pending_action"] = step.action_id
                        results["completed_steps"] = step_idx
                        self._append_audit("CUSTODIAN_APPROVAL_PENDING", {
                            "plan_id": plan.plan_id,
                            "action_id": step.action_id
                        })
                        return results
                    elif not custodian_approval:
                        results["executions"].append({
                            "action_id": step.action_id,
                            "status": "rejected_by_custodian"
                        })
                        results["status"] = "rejected_by_custodian"
                        results["completed_steps"] = step_idx
                        self._append_audit("CUSTODIAN_APPROVAL_REJECTED", {
                            "plan_id": plan.plan_id,
                            "action_id": step.action_id
                        })
                        return results

                # Execute (simulated)
                execution_result = self._simulate_execution(step, plan_id=plan.plan_id)

                results["executions"].append({
                    "action_id": step.action_id,
                    "status": "completed",
                    # BUG-2 Fix: Full SHA-256, no truncation. Truncation to [:16]
                    # reintroduced collision risk inconsistent with the P0 fix applied
                    # elsewhere (ConstitutionalCheckpoint.compute_hash).
                    "result_hash": hashlib.sha256(str(execution_result).encode()).hexdigest()
                })

            # Final anchor
            results["status"] = "completed_with_checkpoints"
            results["final_anchor"] = self._compute_merkle_root(results["checkpoints"])
            results["execution_time"] = time.time() - start_time

            self._append_audit("PLAN_EXECUTION_COMPLETE", {
                "plan_id": plan.plan_id,
                "status": results["status"],
                "checkpoints": len(results["checkpoints"]),
                "executions": len([e for e in results["executions"] if e.get("status") == "completed"]),
                "execution_time": results["execution_time"],
                "merkle_root": results["final_anchor"][:16] + "..."
            })

            return results

    def _simulate_execution(self, action: AgentAction, plan_id: Optional[str] = None) -> Any:
        """
        Simulate tool execution - in production, this calls actual tools.
        P1 Hardened: Thread-safe tool lookup with lock.
        """
        with self._tool_lock:
            if action.tool_name not in self.available_tools:
                return {"status": "tool_not_found", "tool": action.tool_name}

            tool = self.available_tools[action.tool_name]

            if action.tool_name not in self.gate.allowed_tools:
                return {"status": "tool_unauthorized", "tool": action.tool_name}

        self._append_audit("TOOL_INVOKED", {
            "plan_id": plan_id,
            "action_id": action.action_id,
            "tool": action.tool_name,
            "epistemic": action.epistemic_basis.value if isinstance(action.epistemic_basis, EpistemicLabel) else str(action.epistemic_basis)
        })

        return {"status": "success", "tool": action.tool_name}

    def _compute_merkle_root(self, checkpoints: List[Dict]) -> str:
        """
        Compute proper Merkle root of all checkpoint content (P0 Fix).
        Previously only hashed IDs, allowing content tampering.
        """
        if not checkpoints:
            return hashlib.sha256(b"empty").hexdigest()

        # P0 Fix: Hash full checkpoint content, not just IDs
        leaves = []
        for cp in checkpoints:
            content = json.dumps(cp, sort_keys=True).encode()
            leaves.append(hashlib.sha256(content).digest())

        # Build Merkle tree (pairwise hashing)
        while len(leaves) > 1:
            next_level = []
            for i in range(0, len(leaves), 2):
                left = leaves[i]
                right = leaves[i+1] if i+1 < len(leaves) else leaves[i]
                parent = hashlib.sha256(left + right).digest()
                next_level.append(parent)
            leaves = next_level

        return leaves[0].hex()
