"""OpenClaw Agent: Helix-TTD Constitutional Governance Module

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

import glob
import hashlib
import inspect
import json
import os
import queue
import re
import sqlite3
import sys
import threading
import time
import unicodedata
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum, auto
from typing import Any


class AgencyLevel(Enum):
    """Constitutional agency tiers - Helix Article III: Non-Agency Constraint"""

    ADVISORY_ONLY = auto()  # Suggest only, no tool execution
    BOUNDED_TOOLS = auto()  # Execute from approved tool list only
    SUPERVISED_CHAIN = auto()  # Multi-step with checkpoint after each
    CUSTODIAN_GATE = auto()  # Human approval required at each step


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
    drift_codes: list[str] = field(default_factory=list)
    merkle_hash: str = ""
    prev_checkpoint_hash: str = ""
    risk_metrics: dict[str, Any] = field(default_factory=dict)

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
            "metrics": self.risk_metrics,
        }
        # Full SHA-256, no truncation (was [:16] - collision risk)
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


@dataclass
class AgentAction:
    """A single action the agent proposes to take"""

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
    """Multi-step plan requiring constitutional validation before execution"""

    plan_id: str
    objective: str
    steps: list[AgentAction]
    assumptions: list[str]
    estimated_completion: float
    constitutional_clearance: bool = False
    plan_checkpoint: ConstitutionalCheckpoint | None = None


@dataclass
class RiskConfiguration:
    """Granular risk tuning for constitutional gates.

    Allows incremental adjustment of paranoia vs. velocity.
    """

    # Base thresholds (0.0 - 1.0)
    planning_max_risk: float = 0.7  # Max acceptable plan-level risk
    action_max_risk: float = 0.8  # Max acceptable single-action risk
    cumulative_max_risk: float = 2.0  # Max cumulative risk across plan

    # Layer-specific attenuation (multipliers)
    ethics_attenuation: float = 0.9  # Ethics layer reduces effective risk
    safeguard_attenuation: float = 0.8  # Safeguards provide additional reduction

    # Custodian override settings
    custodian_can_override: bool = True
    override_max_risk: float = 0.95  # Even with approval, above this is blocked
    override_requires_dual_approval: bool = False

    # Tool-specific risk multipliers
    tool_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "file_read": 0.5,  # Read is safer
            "file_write": 1.2,  # Write is riskier
            "file_delete": 1.5,  # Delete is dangerous
            "api_call": 1.0,  # Neutral
            "database_migrate": 1.3,  # DB ops are high-stakes
            "self_update_agent": 10.0,  # Always blocked
            "code_execution": 2.0,  # Arbitrary code is dangerous
        }
    )

    # Progressive risk budget
    daily_risk_budget: float = 10.0  # Max cumulative risk per day
    current_risk_spend: float = 0.0  # Tracked runtime

    def __post_init__(self):
        """BUG-3 Fix: Initialize lock in __post_init__ to prevent race condition.

        _get_lock() lazy initialization was not thread-safe — two threads could
        race through hasattr() and create separate lock instances.
        """
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
                self.current_risk_spend + action_risk, self.daily_risk_budget
            )

    def spend_risk(self, amount: float) -> bool:
        """Track risk expenditure with daily reset (P1 Fix).

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

    def get_risk_velocity(self) -> dict[str, float]:
        """Return current risk metrics"""
        return {
            "budget": self.daily_risk_budget,
            "spent": self.current_risk_spend,
            "remaining": self.daily_risk_budget - self.current_risk_spend,
            "utilization": (
                self.current_risk_spend / self.daily_risk_budget
                if self.daily_risk_budget > 0
                else 0
            ),
        }

    # ENHANCEMENT #4: Dynamic Risk Calibration
    def record_execution_outcome(
        self, tool_name: str, planned_risk: float, actual_risk: float, drift_detected: bool
    ):
        """Record execution outcome for dynamic calibration.

        Adjusts tool multipliers based on observed vs predicted risk.
        Positive feedback loop: accurate predictions rewarded, drift penalized.
        """
        with self._get_lock():
            # Initialize calibration history if needed
            if not hasattr(self, "_calibration_history"):
                self._calibration_history: dict[str, list[dict]] = {}

            if tool_name not in self._calibration_history:
                self._calibration_history[tool_name] = []

            # Record this outcome
            self._calibration_history[tool_name].append(
                {
                    "planned": planned_risk,
                    "actual": actual_risk,
                    "drift": drift_detected,
                    "timestamp": time.time(),
                }
            )

            # Keep only last 100 observations per tool
            self._calibration_history[tool_name] = self._calibration_history[tool_name][-100:]

            # Only calibrate after 5 observations
            if len(self._calibration_history[tool_name]) >= 5:
                self._calibrate_tool_multiplier(tool_name)

    def _calibrate_tool_multiplier(self, tool_name: str):
        """Adjust tool multiplier based on historical accuracy."""
        history = self._calibration_history.get(tool_name, [])
        if len(history) < 5:
            return

        # Calculate risk prediction accuracy
        planned_sum = sum(h["planned"] for h in history[-20:])  # Last 20 observations
        actual_sum = sum(h["actual"] for h in history[-20:])
        drift_count = sum(1 for h in history[-20:] if h["drift"])

        if planned_sum == 0:
            return

        # Accuracy ratio: actual/planned (1.0 = perfect prediction)
        accuracy_ratio = actual_sum / planned_sum
        drift_rate = drift_count / min(len(history), 20)

        # Adjust multiplier based on accuracy and drift
        current_multiplier = self.tool_multipliers.get(tool_name, 1.0)

        if accuracy_ratio > 1.2 or drift_rate > 0.3:
            # Underestimating risk - increase multiplier
            new_multiplier = min(current_multiplier * 1.1, 5.0)
        elif accuracy_ratio < 0.8 and drift_rate < 0.1:
            # Overestimating risk - decrease multiplier (carefully)
            new_multiplier = max(current_multiplier * 0.95, 0.1)
        else:
            return  # No adjustment needed

        self.tool_multipliers[tool_name] = new_multiplier

    def get_calibration_report(self) -> dict:
        """Generate report on risk calibration status."""
        if not hasattr(self, "_calibration_history"):
            return {"status": "insufficient_data", "tools": {}}

        report = {"status": "active", "tools": {}}
        for tool_name, history in self._calibration_history.items():
            if len(history) >= 5:
                recent = history[-20:]
                avg_planned = sum(h["planned"] for h in recent) / len(recent)
                avg_actual = sum(h["actual"] for h in recent) / len(recent)
                drift_rate = sum(1 for h in recent if h["drift"]) / len(recent)

                report["tools"][tool_name] = {
                    "observations": len(history),
                    "accuracy_ratio": avg_actual / avg_planned if avg_planned > 0 else 0,
                    "drift_rate": drift_rate,
                    "current_multiplier": self.tool_multipliers.get(tool_name, 1.0),
                }

        return report


class CheckpointStore:
    """ENHANCEMENT #1: SQLite persistence for forensic audit trails.

    Provides durable storage for constitutional checkpoints with queryable
    history for regulatory compliance and forensic analysis.
    """

    def __init__(self, db_path: str | None = None):
        """Initialize checkpoint store with optional custom database path."""
        if db_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(script_dir, "checkpoints.db")
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Create checkpoint table if not exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    layer TEXT NOT NULL,
                    compliance_score REAL NOT NULL,
                    drift_detected INTEGER NOT NULL,
                    drift_codes TEXT,
                    merkle_hash TEXT NOT NULL,
                    prev_checkpoint_hash TEXT,
                    risk_metrics TEXT,
                    plan_id TEXT,
                    agent_id TEXT
                )
                """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_plan_id ON checkpoints(plan_id)
                """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON checkpoints(timestamp)
                """)
            conn.commit()

    def save(self, checkpoint: ConstitutionalCheckpoint, plan_id: str = "", agent_id: str = ""):
        """Persist a checkpoint to the database."""
        with self._lock, sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                    INSERT OR REPLACE INTO checkpoints
                    (id, timestamp, layer, compliance_score, drift_detected,
                     drift_codes, merkle_hash, prev_checkpoint_hash, risk_metrics,
                     plan_id, agent_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    checkpoint.checkpoint_id,
                    checkpoint.timestamp,
                    checkpoint.layer,
                    checkpoint.compliance_score,
                    1 if checkpoint.drift_detected else 0,
                    json.dumps(checkpoint.drift_codes),
                    checkpoint.merkle_hash,
                    checkpoint.prev_checkpoint_hash,
                    json.dumps(checkpoint.risk_metrics),
                    plan_id,
                    agent_id,
                ),
            )
            conn.commit()

    def get_by_plan(self, plan_id: str) -> list[dict]:
        """Retrieve all checkpoints for a specific plan."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM checkpoints WHERE plan_id = ? ORDER BY timestamp",
                (plan_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_by_timerange(
        self, start: datetime, end: datetime, agent_id: str | None = None
    ) -> list[dict]:
        """Query checkpoints within a time range for forensic analysis."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if agent_id:
                cursor = conn.execute(
                    """SELECT * FROM checkpoints
                       WHERE timestamp >= ? AND timestamp <= ? AND agent_id = ?
                       ORDER BY timestamp""",
                    (start.timestamp(), end.timestamp(), agent_id),
                )
            else:
                cursor = conn.execute(
                    """SELECT * FROM checkpoints
                       WHERE timestamp >= ? AND timestamp <= ?
                       ORDER BY timestamp""",
                    (start.timestamp(), end.timestamp()),
                )
            return [dict(row) for row in cursor.fetchall()]

    def get_drift_history(self, limit: int = 100) -> list[dict]:
        """Retrieve recent drift events for compliance monitoring."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """SELECT * FROM checkpoints
                   WHERE drift_detected = 1
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]


# ENHANCEMENT #6: Multi-Agent Checkpoint Consensus
class MultiAgentCheckpointConsensus:
    """Threshold signature scheme for multi-agent checkpoint validation.

    Allows multiple agents to sign checkpoints, requiring a threshold of
    signatures for consensus. This is v2.0 federation infrastructure.

    Note: This is a simplified implementation using hash-based "signatures"
    for demonstration. Production would use proper cryptographic signatures
    (ECDSA, BLS, or threshold BLS for production multi-agent systems).
    """

    def __init__(self, agent_id: str, threshold: int = 2, total_agents: int = 3):
        """Initialize consensus participant.

        Args:
            agent_id: Unique identifier for this agent
            threshold: Minimum signatures required for consensus
            total_agents: Total number of agents in the federation
        """
        self.agent_id = agent_id
        self.threshold = threshold
        self.total_agents = total_agents
        self._signatures: dict[str, dict[str, str]] = {}  # checkpoint_id -> {agent_id: signature}
        self._lock = threading.Lock()

    def sign_checkpoint(self, checkpoint: ConstitutionalCheckpoint) -> str:
        """Generate a signature for a checkpoint.

        Returns a hash-based signature string. In production, this would
        use a proper cryptographic signature with private keys.
        """
        # Create deterministic signature based on checkpoint content + agent_id
        sig_data = {
            "checkpoint_hash": checkpoint.compute_hash(),
            "agent_id": self.agent_id,
            "timestamp": time.time(),
        }
        signature = hashlib.sha256(json.dumps(sig_data, sort_keys=True).encode()).hexdigest()

        with self._lock:
            if checkpoint.checkpoint_id not in self._signatures:
                self._signatures[checkpoint.checkpoint_id] = {}
            self._signatures[checkpoint.checkpoint_id][self.agent_id] = signature

        return signature

    def add_peer_signature(self, checkpoint_id: str, peer_agent_id: str, signature: str) -> bool:
        """Add a signature from another agent.

        Returns True if consensus is reached, False otherwise.
        """
        with self._lock:
            if checkpoint_id not in self._signatures:
                self._signatures[checkpoint_id] = {}
            self._signatures[checkpoint_id][peer_agent_id] = signature
            return len(self._signatures[checkpoint_id]) >= self.threshold

    def has_consensus(self, checkpoint_id: str) -> bool:
        """Check if threshold signatures have been collected."""
        with self._lock:
            signatures = self._signatures.get(checkpoint_id, {})
            return len(signatures) >= self.threshold

    def get_consensus_proof(self, checkpoint_id: str) -> dict | None:
        """Get the full consensus proof for a checkpoint.

        Returns dict with signatures if consensus reached, None otherwise.
        """
        with self._lock:
            signatures = self._signatures.get(checkpoint_id, {})
            if len(signatures) < self.threshold:
                return None

            return {
                "checkpoint_id": checkpoint_id,
                "threshold": self.threshold,
                "signatures_collected": len(signatures),
                "total_agents": self.total_agents,
                "signatures": signatures.copy(),
                "consensus_reached": True,
            }

    def verify_signature(
        self, checkpoint: ConstitutionalCheckpoint, agent_id: str, signature: str
    ) -> bool:
        """Verify a signature is valid for a given checkpoint and agent.

        Returns True if signature is valid, False otherwise.
        """
        # Recreate expected signature
        sig_data = {
            "checkpoint_hash": checkpoint.compute_hash(),
            "agent_id": agent_id,
            # Note: timestamp not included in verification (would need temporal tolerance)
        }
        expected = hashlib.sha256(json.dumps(sig_data, sort_keys=True).encode()).hexdigest()
        return signature[:64] == expected[:64]  # Compare first 64 chars

    def get_checkpoint_status(self, checkpoint_id: str) -> dict:
        """Get current consensus status for a checkpoint."""
        with self._lock:
            signatures = self._signatures.get(checkpoint_id, {})
            return {
                "checkpoint_id": checkpoint_id,
                "signatures_collected": len(signatures),
                "threshold": self.threshold,
                "consensus_reached": len(signatures) >= self.threshold,
                "signing_agents": list(signatures.keys()),
                "remaining_needed": max(0, self.threshold - len(signatures)),
            }


# ENHANCEMENT #7: SIEM Integration - Structured Logging for Security Teams
class SIEMExporter:
    """Export constitutional events to SIEM systems (Splunk, ELK, OpenTelemetry).

    Provides real-time constitutional violation alerts and compliance reporting
    for security operations centers.
    """

    def __init__(self, agent_id: str, endpoint: str | None = None):
        """Initialize SIEM exporter.

        Args:
            agent_id: Unique agent identifier
            endpoint: Optional SIEM ingestion endpoint (HTTP/HTTPS)
        """
        self.agent_id = agent_id
        self.endpoint = endpoint
        self._event_queue: list[dict] = []
        self._queue_lock = threading.Lock()
        self._enabled = endpoint is not None

        # OpenTelemetry-compatible structured format
        self._resource_attributes = {
            "service.name": "helix-ttd-agent",
            "service.version": "1.0.0",
            "agent.id": agent_id,
        }

    def export_event(
        self, event_type: str, checkpoint: ConstitutionalCheckpoint | None = None, **kwargs
    ):
        """Export a constitutional event in OTel-compatible format.

        Args:
            event_type: Type of event (drift_detected, checkpoint_validated, etc.)
            checkpoint: Optional checkpoint associated with event
            **kwargs: Additional event attributes
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "severity": self._map_severity(event_type, checkpoint),
            "event_type": f"helix.ttd.{event_type}",
            "resource": self._resource_attributes,
            "attributes": {
                "agent.id": self.agent_id,
                **kwargs,
            },
        }

        if checkpoint:
            event["attributes"]["checkpoint_id"] = checkpoint.checkpoint_id
            event["attributes"]["compliance_score"] = checkpoint.compliance_score
            event["attributes"]["drift_detected"] = checkpoint.drift_detected
            event["attributes"]["drift_codes"] = checkpoint.drift_codes
            event["attributes"]["layer"] = checkpoint.layer

        with self._queue_lock:
            self._event_queue.append(event)

        # For critical events, flush immediately
        if event["severity"] in ("critical", "high"):
            self.flush()

        return event

    def _map_severity(
        self, event_type: str, checkpoint: ConstitutionalCheckpoint | None = None
    ) -> str:
        """Map event type to severity level."""
        if checkpoint and checkpoint.drift_detected:
            return "critical" if checkpoint.compliance_score < 0.3 else "high"
        severity_map = {
            "drift_detected": "critical",
            "checkpoint_rejected": "high",
            "custodian_override_used": "warning",
            "plan_executed": "info",
            "tool_invoked": "info",
        }
        return severity_map.get(event_type, "info")

    def flush(self) -> list[dict]:
        """Flush event queue to SIEM endpoint or return for batch processing.

        Returns list of events that were flushed.
        """
        with self._queue_lock:
            events_to_flush = self._event_queue.copy()
            self._event_queue = []

        if not events_to_flush:
            return []

        if self._enabled and self.endpoint:
            # In production, this would HTTP POST to SIEM
            # For now, we simulate with structured logging
            for event in events_to_flush:
                print(json.dumps(event, default=str), flush=True)

        return events_to_flush

    def get_queue_stats(self) -> dict:
        """Get current event queue statistics."""
        with self._queue_lock:
            return {
                "queued_events": len(self._event_queue),
                "enabled": self._enabled,
                "endpoint": self.endpoint,
            }

    def export_drift_alert(self, checkpoint: ConstitutionalCheckpoint, context: dict | None = None):
        """Export a drift detection alert (high priority)."""
        return self.export_event(
            "drift_detected",
            checkpoint=checkpoint,
            alert_title="Constitutional Drift Detected",
            alert_description="Agent behavior violated constitutional constraints",
            recommended_action="Review checkpoint and custodian approval status",
            context=context or {},
        )


# ENHANCEMENT #8: Plugin Architecture for Extensible 4-Layer Pipeline
class ConstitutionalLayer(ABC):
    """Abstract base class for constitutional pipeline layers.

    Allows custom layers to be registered and integrated into the
    Ethics → Safeguard → Iterate → Knowledge pipeline.
    """

    @abstractmethod
    def evaluate(self, plan: AgentPlan) -> tuple[bool, float, list[str]]:
        """Evaluate a plan through this constitutional layer.

        Returns:
            (passed, compliance_score, drift_codes)
            - passed: True if plan passes this layer
            - compliance_score: 0.0-1.0 compliance rating
            - drift_codes: List of drift codes if violations found
        """
        ...

    @property
    @abstractmethod
    def layer_name(self) -> str:
        """Return the name of this layer."""
        ...

    @property
    def priority(self) -> int:
        """Return execution priority (lower = earlier). Default is 50."""
        return 50


class PluginRegistry:
    """Registry for constitutional layer plugins.

    Manages custom layers that extend the 4-layer pipeline.
    """

    def __init__(self):
        self._plugins: dict[str, ConstitutionalLayer] = {}
        self._lock = threading.Lock()

    def register(self, plugin: ConstitutionalLayer) -> bool:
        """Register a constitutional layer plugin.

        Returns True if registered, False if name conflict.
        """
        with self._lock:
            if plugin.layer_name in self._plugins:
                return False
            self._plugins[plugin.layer_name] = plugin
            return True

    def unregister(self, layer_name: str) -> bool:
        """Unregister a plugin by name."""
        with self._lock:
            if layer_name in self._plugins:
                del self._plugins[layer_name]
                return True
            return False

    def get_sorted_plugins(self) -> list[ConstitutionalLayer]:
        """Get plugins sorted by priority."""
        with self._lock:
            return sorted(self._plugins.values(), key=lambda p: p.priority)

    def evaluate_all(self, plan: AgentPlan) -> tuple[bool, float, dict[str, list[str]]]:
        """Evaluate plan through all registered plugins.

        Returns aggregated results from all layers.
        """
        plugins = self.get_sorted_plugins()
        all_passed = True
        total_score = 0.0
        all_drift_codes: dict[str, list[str]] = {}

        for plugin in plugins:
            passed, score, drift_codes = plugin.evaluate(plan)
            all_passed = all_passed and passed
            total_score += score
            if drift_codes:
                all_drift_codes[plugin.layer_name] = drift_codes

        avg_score = total_score / len(plugins) if plugins else 1.0
        return all_passed, avg_score, all_drift_codes

    def list_plugins(self) -> list[dict]:
        """List all registered plugins with metadata."""
        with self._lock:
            return [
                {
                    "name": p.layer_name,
                    "priority": p.priority,
                    "class": p.__class__.__name__,
                }
                for p in self._plugins.values()
            ]


# Example plugin implementations
class ComplianceAuditLayer(ConstitutionalLayer):
    """Example plugin: Audit compliance against external policies."""

    def __init__(self, required_tags: list[str] | None = None):
        self.required_tags = required_tags or ["[FACT]", "[HYPOTHESIS]"]

    @property
    def layer_name(self) -> str:
        """Return the layer name."""
        return "ComplianceAudit"

    @property
    def priority(self) -> int:
        """Return execution priority (run after Ethics, before Safeguard)."""
        return 25

    def evaluate(self, plan: AgentPlan) -> tuple[bool, float, list[str]]:
        """Check plan steps for required epistemic tags."""
        drift_codes = []
        for step in plan.steps:
            has_required = any(tag in step.rationale for tag in self.required_tags)
            if not has_required:
                drift_codes.append(f"DRIFT-A: Missing required epistemic tag in {step.action_id}")

        score = 1.0 if not drift_codes else 0.5
        return len(drift_codes) == 0, score, drift_codes


class RateLimitLayer(ConstitutionalLayer):
    """Example plugin: Rate limiting for tool invocations."""

    def __init__(self, max_calls_per_minute: int = 60):
        self.max_calls = max_calls_per_minute
        self._call_times: list[float] = []
        self._lock = threading.Lock()

    @property
    def layer_name(self) -> str:
        """Return the layer name."""
        return "RateLimit"

    @property
    def priority(self) -> int:
        """Return execution priority (run very early)."""
        return 15

    def evaluate(self, plan: AgentPlan) -> tuple[bool, float, list[str]]:
        """Check if plan would exceed rate limits."""
        with self._lock:
            now = time.time()
            # Remove calls older than 1 minute
            self._call_times = [t for t in self._call_times if now - t < 60]

            if len(self._call_times) + len(plan.steps) > self.max_calls:
                return False, 0.0, ["DRIFT-R: Rate limit exceeded"]

            # Record planned calls
            for _ in plan.steps:
                self._call_times.append(now)

        return True, 1.0, []


# ENHANCEMENT #9: Metrics Dashboard - Prometheus/Grafana Telemetry
class MetricsCollector:
    """Collect and expose metrics for operational monitoring.

    Provides Prometheus-compatible metrics for dashboards and alerting.
    Tracks execution latency, throughput, violation rates, and resource usage.
    """

    def __init__(self, agent_id: str):
        """Initialize metrics collector.

        Args:
            agent_id: Unique agent identifier for metric labels
        """
        self.agent_id = agent_id
        self._metrics_lock = threading.Lock()

        # Counters (monotonically increasing)
        self._counters: dict[str, int] = {
            "plans_executed_total": 0,
            "plans_rejected_total": 0,
            "actions_executed_total": 0,
            "actions_blocked_total": 0,
            "drift_detected_total": 0,
            "custodian_overrides_total": 0,
            "tool_invocations_total": 0,
            "cache_hits_total": 0,
            "cache_misses_total": 0,
        }

        # Gauges (current values)
        self._gauges: dict[str, float] = {
            "risk_budget_remaining": 0.0,
            "risk_utilization_ratio": 0.0,
            "active_plans": 0.0,
            "cache_size": 0.0,
        }

        # Histograms (latency distributions)
        self._latency_buckets = [
            0.001,
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
        ]
        self._plan_execution_times: list[float] = []
        self._action_execution_times: list[float] = []

        # Time-series data for dashboards (last 1000 points)
        self._timeseries: dict[str, list[tuple[float, float]]] = {
            "compliance_score": [],
            "risk_velocity": [],
            "drift_rate": [],
        }

    def increment(self, metric_name: str, value: int = 1):
        """Increment a counter metric."""
        with self._metrics_lock:
            if metric_name in self._counters:
                self._counters[metric_name] += value

    def set_gauge(self, metric_name: str, value: float):
        """Set a gauge metric to a specific value."""
        with self._metrics_lock:
            if metric_name in self._gauges:
                self._gauges[metric_name] = value

    def record_latency(self, metric_type: str, seconds: float):
        """Record execution latency."""
        with self._metrics_lock:
            if metric_type == "plan":
                self._plan_execution_times.append(seconds)
                # Keep last 1000 samples
                if len(self._plan_execution_times) > 1000:
                    self._plan_execution_times = self._plan_execution_times[-1000:]
            elif metric_type == "action":
                self._action_execution_times.append(seconds)
                if len(self._action_execution_times) > 1000:
                    self._action_execution_times = self._action_execution_times[-1000:]

    def record_timeseries(self, metric_name: str, value: float):
        """Record a time-series data point."""
        with self._metrics_lock:
            if metric_name in self._timeseries:
                timestamp = time.time()
                self._timeseries[metric_name].append((timestamp, value))
                # Keep last 1000 points
                if len(self._timeseries[metric_name]) > 1000:
                    self._timeseries[metric_name] = self._timeseries[metric_name][-1000:]

    def _compute_histogram(self, samples: list[float]) -> dict:
        """Compute histogram buckets from samples."""
        if not samples:
            return {"count": 0, "sum": 0.0, "buckets": dict.fromkeys(self._latency_buckets, 0)}

        buckets = {b: sum(1 for s in samples if s <= b) for b in self._latency_buckets}
        return {
            "count": len(samples),
            "sum": sum(samples),
            "avg": sum(samples) / len(samples),
            "min": min(samples),
            "max": max(samples),
            "buckets": buckets,
        }

    def get_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        labels = f'agent_id="{self.agent_id}"'

        with self._metrics_lock:
            # Counters
            for name, value in self._counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name}{{{labels}}} {value}")

            # Gauges
            for name, value in self._gauges.items():
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name}{{{labels}}} {value}")

            # Histograms
            for hist_name, samples in [
                ("plan_execution_duration_seconds", self._plan_execution_times),
                ("action_execution_duration_seconds", self._action_execution_times),
            ]:
                hist = self._compute_histogram(samples)
                lines.append(f"# TYPE {hist_name} histogram")
                for bucket, count in hist["buckets"].items():
                    lines.append(f'{hist_name}_bucket{{{labels},le="{bucket}"}} {count}')
                lines.append(f'{hist_name}_count{{{labels}}} {hist["count"]}')
                lines.append(f'{hist_name}_sum{{{labels}}} {hist["sum"]}')

        return "\n".join(lines)

    def get_dashboard_data(self) -> dict:
        """Get metrics formatted for dashboard display."""
        with self._metrics_lock:
            plan_hist = self._compute_histogram(self._plan_execution_times)
            action_hist = self._compute_histogram(self._action_execution_times)

            return {
                "agent_id": self.agent_id,
                "timestamp": datetime.now().isoformat(),
                "counters": self._counters.copy(),
                "gauges": self._gauges.copy(),
                "latency": {
                    "plan_execution_ms": {
                        "avg": plan_hist["avg"] * 1000 if plan_hist["count"] > 0 else 0,
                        "p95": (
                            self._percentile(self._plan_execution_times, 0.95) * 1000
                            if self._plan_execution_times
                            else 0
                        ),
                        "p99": (
                            self._percentile(self._plan_execution_times, 0.99) * 1000
                            if self._plan_execution_times
                            else 0
                        ),
                    },
                    "action_execution_ms": {
                        "avg": action_hist["avg"] * 1000 if action_hist["count"] > 0 else 0,
                        "p95": (
                            self._percentile(self._action_execution_times, 0.95) * 1000
                            if self._action_execution_times
                            else 0
                        ),
                        "p99": (
                            self._percentile(self._action_execution_times, 0.99) * 1000
                            if self._action_execution_times
                            else 0
                        ),
                    },
                },
                "timeseries": {
                    name: [(t, v) for t, v in data[-100:]]  # Last 100 points
                    for name, data in self._timeseries.items()
                },
            }

    def _percentile(self, samples: list[float], p: float) -> float:
        """Calculate percentile from samples."""
        if not samples:
            return 0.0
        sorted_samples = sorted(samples)
        k = (len(sorted_samples) - 1) * p
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_samples) else f
        return sorted_samples[f] + (k - f) * (sorted_samples[c] - sorted_samples[f])

    def record_plan_execution(self, plan: AgentPlan, duration_seconds: float, success: bool):
        """Record metrics for a completed plan execution."""
        self.increment("plans_executed_total" if success else "plans_rejected_total")
        self.record_latency("plan", duration_seconds)

        # Calculate drift rate for this plan
        drift_count = sum(1 for step in plan.steps if getattr(step, "drift_detected", False))
        drift_rate = drift_count / len(plan.steps) if plan.steps else 0.0
        self.record_timeseries("drift_rate", drift_rate)


class HelixConstitutionalGate:
    """The Helix-TTD Civic Firmware Stack applied to agent workflows.

    Reject-forward pipeline: Ethics → Safeguard → Iterate → Knowledge

    Now with granular risk tuning via RiskConfiguration.
    """

    # P2: JSON parameter size limit to prevent memory exhaustion
    MAX_JSON_PARAM_SIZE = 10000  # 10KB

    # Constitutional grammar version — checked at init against substrate
    CONSTITUTION_VERSION = "1.0.0"

    def __init__(
        self,
        agency_tier: AgencyLevel = AgencyLevel.BOUNDED_TOOLS,
        risk_config: RiskConfiguration | None = None,
        constitution_version: str = "1.0.0",
    ):
        self.agency_tier = agency_tier
        self.risk = risk_config or RiskConfiguration()
        self.checkpoints: list[ConstitutionalCheckpoint] = []
        self.allowed_tools: set = set()
        # Design fix: removed "override" — it conflicts with internal field names
        # (custodian_can_override, override_max_risk) causing false DRIFT-C positives.
        # Custodian override authority is a constitutional right, not a forbidden pattern.
        self.forbidden_patterns: list[str] = [
            "autonomous",
            "self-directed",
            "initiate",
            "independent",
            "self-improve",
            "modify_own",
            "bypass",
        ]
        # Constitution versioning: surfaced in all checkpoints for drift detection
        self.constitution_version = constitution_version
        if constitution_version != self.CONSTITUTION_VERSION:
            import warnings

            warnings.warn(
                f"Constitution version mismatch: gate={constitution_version}, "
                f"canonical={self.CONSTITUTION_VERSION}. Risk model may be stale.",
                UserWarning,
                stacklevel=2,
            )

    def _layer_ethics(self, plan: AgentPlan) -> tuple[bool, float]:
        """Layer 0: Ethics Evaluation

        Does this plan respect Custodial Sovereignty?
        """
        compliance_factors = []

        # Check for imperatives toward human
        if any(
            "must" in step.rationale.lower() or "should" in step.rationale.lower()
            for step in plan.steps
        ):
            compliance_factors.append(0.8)  # Slight deduction for imperative tone
        else:
            compliance_factors.append(1.0)

        # Check agency tier compliance
        if self.agency_tier == AgencyLevel.ADVISORY_ONLY:
            if any(step.action_type != "suggest" for step in plan.steps):
                return False, 0.0

        # Check for self-referential modifications
        self_ref_count = sum(
            1
            for step in plan.steps
            if any(
                pattern in step.tool_name.lower() for pattern in ["self", "modify", "update_agent"]
            )
        )
        if self_ref_count > 0:
            compliance_factors.append(0.0)  # Constitutional violation
            return False, 0.0

        return True, sum(compliance_factors) / len(compliance_factors)

    def _normalize_for_check(self, text: str) -> str:
        """P0 Fix: Unicode normalization to prevent homoglyph bypasses"""
        # NFKC normalization (compatibility decomposition + composition)
        normalized = unicodedata.normalize("NFKC", str(text))
        # Remove zero-width characters that can hide forbidden words
        for zw in ["\u200b", "\u200c", "\u200d", "\ufeff", "\u2060"]:
            normalized = normalized.replace(zw, "")
        return normalized.lower()

    def _layer_safeguard(self, plan: AgentPlan) -> tuple[bool, list[str], float]:
        """Layer 1: Safeguard Detection with granular risk tuning.

        Detect coercion, agency redefinition, epistemic anomalies
        P0 Fix: Check ALL fields with Unicode normalization
        """
        drift_codes = []
        total_effective_risk = 0.0

        if not self.allowed_tools and any(step.action_type != "suggest" for step in plan.steps):
            drift_codes.append("DRIFT-S: No tools authorized for non-suggest actions")

        for step in plan.steps:
            # Calculate effective risk with tool multipliers
            effective_risk = self.risk.calculate_effective_risk(step.estimated_risk, step.tool_name)
            step.effective_risk = effective_risk  # Store for later
            total_effective_risk += effective_risk

            # P0 Fix: Check ALL text fields, not just rationale
            # P2: Limit parameter serialization size to prevent memory issues
            param_str = json.dumps(step.parameters, ensure_ascii=False)
            if len(param_str) > self.MAX_JSON_PARAM_SIZE:
                param_str = param_str[: self.MAX_JSON_PARAM_SIZE] + "...[TRUNCATED]"
            all_text = f"{step.rationale} {step.tool_name} {step.action_type} {param_str}"
            check_text = self._normalize_for_check(all_text)

            # Check for forbidden patterns (agency drift) - absolute block
            if any(pattern in check_text for pattern in self.forbidden_patterns):
                drift_codes.append("DRIFT-C: Agency Redefinition Attempt")

            # Check cumulative risk budget
            if not self.risk.has_risk_budget(effective_risk):
                drift_codes.append(
                    f"DRIFT-S: Daily Risk Budget Exceeded ({self.risk.get_risk_velocity()['remaining']:.2f} remaining)"
                )

            # Check per-action risk threshold (with tool multipliers applied)
            if effective_risk > self.risk.action_max_risk:
                drift_codes.append(
                    f"DRIFT-S: Effective Risk {effective_risk:.2f} Exceeds Action Threshold {self.risk.action_max_risk}"
                )

            # Check tool authorization
            if self.allowed_tools and step.tool_name not in self.allowed_tools:
                drift_codes.append(f"DRIFT-C: Unauthorized Tool {step.tool_name}")

        # Check cumulative plan risk
        if total_effective_risk > self.risk.cumulative_max_risk:
            drift_codes.append(
                f"DRIFT-S: Cumulative Plan Risk {total_effective_risk:.2f} Exceeds Budget {self.risk.cumulative_max_risk}"
            )

        plan.total_effective_risk = total_effective_risk
        return len(drift_codes) == 0, drift_codes, total_effective_risk

    def _layer_iterate(self, plan: AgentPlan) -> AgentPlan:
        """Layer 2: Iterate Layer

        Rephrase for clarity, ensure ledger-aligned diffability

        BUG-4 Fix: Use re.sub with IGNORECASE so mixed-case imperatives
        ("You Should", "MUST") are replaced, not just detected-but-missed.
        Previously: detection was case-insensitive but replacement was not.
        """
        for step in plan.steps:
            step.rationale = re.sub(r"you should", "consider", step.rationale, flags=re.IGNORECASE)
            step.rationale = re.sub(r"\bmust\b", "could", step.rationale, flags=re.IGNORECASE)

        return plan

    def _layer_knowledge(self, plan: AgentPlan) -> tuple[bool, str]:
        """Layer 3: Knowledge Layer

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
        """Full civic firmware pipeline with granular risk tuning.

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
            prev_checkpoint_hash=self.checkpoints[-1].merkle_hash if self.checkpoints else "0",
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
        checkpoint.risk_metrics["plan_total"] = total_risk

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
            if hasattr(step, "effective_risk"):
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

    def validate_action(self, action: AgentAction, context: dict) -> ConstitutionalCheckpoint:
        """Validate a single action before execution with granular risk tuning."""
        # Calculate effective risk with tool multipliers
        effective_risk = self.risk.calculate_effective_risk(action.estimated_risk, action.tool_name)
        action.effective_risk = effective_risk

        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id=f"act_chk_{int(time.time())}",
            timestamp=time.time(),
            layer="Action-Safeguard",
            compliance_score=1.0 - effective_risk,  # Higher risk = lower compliance
            drift_detected=False,
            risk_metrics={
                "base_risk": action.estimated_risk,
                "effective_risk": effective_risk,
                "remaining_budget": self.risk.get_risk_velocity()["remaining"],
                "constitution_version": self.constitution_version,
            },
            prev_checkpoint_hash=self.checkpoints[-1].merkle_hash if self.checkpoints else "0",
        )

        # Runtime safeguard checks with granular thresholds

        # Absolute blocks (even with approval)
        if effective_risk >= self.risk.override_max_risk:
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append(
                f"DRIFT-C: Effective Risk {effective_risk:.2f} Exceeds Absolute Maximum {self.risk.override_max_risk}"
            )
            checkpoint.compliance_score = 0.0
            action.requires_approval = True  # Will be blocked anyway

        # High risk requiring approval
        elif effective_risk > self.risk.action_max_risk:
            checkpoint.drift_codes.append(
                f"DRIFT-S: Effective Risk {effective_risk:.2f} Requires Approval (threshold: {self.risk.action_max_risk})"
            )
            checkpoint.compliance_score = 0.5
            action.requires_approval = True

        # Check risk budget
        if not self.risk.has_risk_budget(effective_risk):
            checkpoint.drift_detected = True
            checkpoint.drift_codes.append(
                f"DRIFT-S: Insufficient Risk Budget ({self.risk.get_risk_velocity()['remaining']:.2f} remaining)"
            )
            checkpoint.compliance_score = 0.2

        # Check for forbidden patterns
        # P2: Limit parameter serialization size to prevent memory issues
        param_str = json.dumps(action.parameters, ensure_ascii=False)
        if len(param_str) > self.MAX_JSON_PARAM_SIZE:
            param_str = param_str[: self.MAX_JSON_PARAM_SIZE] + "...[TRUNCATED]"
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


# ENHANCEMENT #10: Custodian Approval API - WebSocket/HTTP for Human Approval Workflows
class CustodianApprovalAPI:
    """Queue-based API for custodian approval workflows.

    Replaces the boolean custodian_approval parameter with a proper
    request/response queue system that supports:
    - Timeout handling
    - Multiple pending approvals
    - Rejection with reason
    - Audit trail of all approval decisions
    """

    def __init__(self, default_timeout_seconds: float = 300.0):
        """Initialize the approval API.

        Args:
            default_timeout_seconds: Default timeout for approval requests
        """
        self.default_timeout = default_timeout_seconds
        self._pending: dict[str, dict] = {}  # request_id -> approval request
        self._responses: queue.Queue[dict] = queue.Queue()
        self._lock = threading.Lock()
        self._history: list[dict] = []
        self._max_history = 1000

    def request_approval(
        self,
        action: AgentAction,
        plan_id: str,
        checkpoint: ConstitutionalCheckpoint,
        timeout_seconds: float | None = None,
    ) -> str:
        """Request custodian approval for an action.

        Returns a request_id that can be used to check status or cancel.
        """
        request_id = f"req_{uuid.uuid4().hex[:16]}"
        timeout = timeout_seconds or self.default_timeout

        request = {
            "request_id": request_id,
            "action": {
                "action_id": action.action_id,
                "action_type": action.action_type,
                "tool_name": action.tool_name,
                "parameters": action.parameters,
                "rationale": action.rationale,
                "epistemic_basis": (
                    action.epistemic_basis.value
                    if isinstance(action.epistemic_basis, EpistemicLabel)
                    else str(action.epistemic_basis)
                ),
                "estimated_risk": action.estimated_risk,
            },
            "plan_id": plan_id,
            "checkpoint": {
                "checkpoint_id": checkpoint.checkpoint_id,
                "compliance_score": checkpoint.compliance_score,
                "drift_codes": checkpoint.drift_codes,
            },
            "requested_at": time.time(),
            "timeout_at": time.time() + timeout,
            "status": "pending",  # pending, approved, rejected, timeout
            "custodian_response": None,
            "custodian_id": None,
        }

        with self._lock:
            self._pending[request_id] = request

        return request_id

    def approve(self, request_id: str, custodian_id: str, notes: str | None = None) -> bool:
        """Approve a pending request.

        Returns True if approved, False if request not found or already decided.
        """
        with self._lock:
            if request_id not in self._pending:
                return False

            request = self._pending[request_id]
            if request["status"] != "pending":
                return False

            if time.time() > request["timeout_at"]:
                request["status"] = "timeout"
                self._record_history(request)
                return False

            request["status"] = "approved"
            request["custodian_id"] = custodian_id
            request["custodian_response"] = {"decision": "approved", "notes": notes}
            request["responded_at"] = time.time()

            self._responses.put(request)
            self._record_history(request)
            del self._pending[request_id]
            return True

    def reject(
        self, request_id: str, custodian_id: str, reason: str, notes: str | None = None
    ) -> bool:
        """Reject a pending request.

        Returns True if rejected, False if request not found or already decided.
        """
        with self._lock:
            if request_id not in self._pending:
                return False

            request = self._pending[request_id]
            if request["status"] != "pending":
                return False

            if time.time() > request["timeout_at"]:
                request["status"] = "timeout"
                self._record_history(request)
                return False

            request["status"] = "rejected"
            request["custodian_id"] = custodian_id
            request["custodian_response"] = {
                "decision": "rejected",
                "reason": reason,
                "notes": notes,
            }
            request["responded_at"] = time.time()

            self._responses.put(request)
            self._record_history(request)
            del self._pending[request_id]
            return True

    def wait_for_response(self, request_id: str, poll_interval: float = 0.1) -> dict | None:
        """Block until a response is received for the given request_id.

        Returns the response dict or None if timeout.
        """
        with self._lock:
            if request_id not in self._pending:
                # Already decided
                for resp in list(self._responses.queue):
                    if resp["request_id"] == request_id:
                        return resp
                return None

            request = self._pending[request_id]
            timeout_at = request["timeout_at"]

        while time.time() < timeout_at:
            try:
                # Non-blocking check with timeout
                remaining = timeout_at - time.time()
                if remaining <= 0:
                    break

                response = self._responses.get(timeout=min(poll_interval, remaining))
                if response["request_id"] == request_id:
                    return response

                # Put it back if not ours (shouldn't happen often)
                self._responses.put(response)

            except queue.Empty:
                continue

        # Timeout
        with self._lock:
            if request_id in self._pending:
                request = self._pending[request_id]
                request["status"] = "timeout"
                self._record_history(request)
                del self._pending[request_id]
                return request

        return None

    def get_pending_requests(self) -> list[dict]:
        """Get all pending approval requests (for custodian dashboard)."""
        with self._lock:
            now = time.time()
            # Clean up expired requests
            expired = [req_id for req_id, req in self._pending.items() if now > req["timeout_at"]]
            for req_id in expired:
                self._pending[req_id]["status"] = "timeout"
                self._record_history(self._pending[req_id])
                del self._pending[req_id]

            return [
                {
                    "request_id": req["request_id"],
                    "action": req["action"],
                    "plan_id": req["plan_id"],
                    "requested_at": req["requested_at"],
                    "timeout_at": req["timeout_at"],
                    "time_remaining": max(0, req["timeout_at"] - now),
                }
                for req in self._pending.values()
            ]

    def get_request_status(self, request_id: str) -> dict | None:
        """Get current status of a request."""
        with self._lock:
            if request_id in self._pending:
                req = self._pending[request_id]
                return {
                    "request_id": req["request_id"],
                    "status": req["status"],
                    "time_remaining": max(0, req["timeout_at"] - time.time()),
                }

        # Check history
        for hist in self._history:
            if hist["request_id"] == request_id:
                return {
                    "request_id": hist["request_id"],
                    "status": hist["status"],
                    "custodian_id": hist.get("custodian_id"),
                    "responded_at": hist.get("responded_at"),
                }

        return None

    def _record_history(self, request: dict):
        """Record request to history for audit trail."""
        self._history.append(request.copy())
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def get_approval_history(
        self, limit: int = 100, status_filter: str | None = None
    ) -> list[dict]:
        """Get approval decision history for audit/compliance."""
        with self._lock:
            history = self._history.copy()

        if status_filter:
            history = [h for h in history if h["status"] == status_filter]

        # Sort by responded_at (most recent first)
        history.sort(key=lambda x: x.get("responded_at", x["requested_at"]), reverse=True)
        return history[:limit]

    def get_stats(self) -> dict:
        """Get approval API statistics."""
        with self._lock:
            pending_count = len(self._pending)
            history_count = len(self._history)

        approved = sum(1 for h in self._history if h["status"] == "approved")
        rejected = sum(1 for h in self._history if h["status"] == "rejected")
        timeouts = sum(1 for h in self._history if h["status"] == "timeout")

        return {
            "pending_requests": pending_count,
            "total_decisions": history_count,
            "approved": approved,
            "rejected": rejected,
            "timeouts": timeouts,
            "approval_rate": approved / (approved + rejected) if (approved + rejected) > 0 else 0,
        }


class OpenClawAgent:
    """A bounded agent with Helix-TTD constitutional checkpoints.

    Philosophy: The agent plans and proposes. Helix validates.
    The Custodian (human or explicit gate) approves execution.

    Now with granular risk tuning via RiskConfiguration.
    P1/P2 Hardened: Thread-safe, DoS protected, type-validated.
    """

    # P1: Resource limits
    MAX_PLAN_STEPS = 100
    MAX_EXECUTION_TIME = 300  # 5 minutes

    def __init__(
        self,
        agency_tier: AgencyLevel = AgencyLevel.BOUNDED_TOOLS,
        risk_config: RiskConfiguration | None = None,
        audit_log_path: str | None = None,
    ):
        self.gate = HelixConstitutionalGate(agency_tier, risk_config)
        self.plan_history: list[AgentPlan] = []
        self.execution_log: list[dict] = []
        self.available_tools: dict[str, Callable] = {}

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

        # ENHANCEMENT #5: Tool Result Memoization
        self._memo_cache: dict[str, tuple[Any, float]] = {}  # (result, timestamp)
        self._memo_ttl_seconds: float = 300.0  # 5 minute default TTL
        self._memo_lock = threading.Lock()

        # ENHANCEMENT #7: SIEM Integration
        self.siem = SIEMExporter(self.agent_id)

        # ENHANCEMENT #8: Plugin Registry
        self.plugins = PluginRegistry()

        # ENHANCEMENT #9: Metrics Collection
        self.metrics = MetricsCollector(self.agent_id)

        # ENHANCEMENT #10: Custodian Approval API
        self.approval_api = CustodianApprovalAPI()

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
        return not (log_dir and os.path.islink(log_dir))

    def _sanitize_audit_data(self, data: dict) -> dict:
        """P2: Sanitize audit data to prevent log injection.

        Remove newlines, control chars, and null bytes from strings.
        """
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                sanitized = v.replace("\n", " ").replace("\r", " ").replace("\x00", "")
                sanitized = "".join(c if ord(c) >= 32 or c == "\t" else " " for c in sanitized)
                result[k] = sanitized
            elif isinstance(v, dict):
                result[k] = self._sanitize_audit_data(v)
            elif isinstance(v, list):
                sanitized_list = []
                for item in v:
                    if isinstance(item, str):
                        s = item.replace("\n", " ").replace("\r", " ").replace("\x00", "")
                        s = "".join(c if ord(c) >= 32 or c == "\t" else " " for c in s)
                        sanitized_list.append(s)
                    elif isinstance(item, dict):
                        sanitized_list.append(self._sanitize_audit_data(item))
                    else:
                        sanitized_list.append(item)
                result[k] = sanitized_list
            else:
                result[k] = v
        return result

    # ENHANCEMENT #5: Tool Result Memoization
    def _get_memo_key(self, action: AgentAction) -> str:
        """Generate cache key for memoization based on tool + parameters."""
        # Hash of tool name and parameters determines cache key
        key_data = {
            "tool": action.tool_name,
            "params": action.parameters,
        }
        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:32]

    def _get_cached_result(self, action: AgentAction) -> Any | None:
        """Check if result is in cache and not expired."""
        with self._memo_lock:
            cache_key = self._get_memo_key(action)
            if cache_key in self._memo_cache:
                result, timestamp = self._memo_cache[cache_key]
                if time.time() - timestamp < self._memo_ttl_seconds:
                    return result
                else:
                    # Expired - remove from cache
                    del self._memo_cache[cache_key]
            return None

    def _cache_result(self, action: AgentAction, result: Any):
        """Store result in cache with current timestamp."""
        with self._memo_lock:
            cache_key = self._get_memo_key(action)
            self._memo_cache[cache_key] = (result, time.time())
            # Prevent unbounded growth - keep last 1000 entries
            if len(self._memo_cache) > 1000:
                # Remove oldest entries
                sorted_items = sorted(self._memo_cache.items(), key=lambda x: x[1][1])
                for key, _ in sorted_items[:100]:
                    del self._memo_cache[key]

    def clear_memo_cache(self):
        """Clear all cached results."""
        with self._memo_lock:
            self._memo_cache.clear()

    def get_memo_stats(self) -> dict:
        """Get memoization cache statistics."""
        with self._memo_lock:
            now = time.time()
            valid_entries = sum(
                1
                for _, timestamp in self._memo_cache.values()
                if now - timestamp < self._memo_ttl_seconds
            )
            return {
                "total_entries": len(self._memo_cache),
                "valid_entries": valid_entries,
                "expired_entries": len(self._memo_cache) - valid_entries,
                "ttl_seconds": self._memo_ttl_seconds,
            }

    def _validate_event_type(self, event_type: str) -> str:
        """P2: Validate event type against allowed set to prevent injection."""
        allowed_events = {
            "TOOL_REGISTERED",
            "PLAN_EXECUTION_START",
            "PLAN_EXECUTION_COMPLETE",
            "PLAN_EXECUTION_REJECTED",
            "CUSTODIAN_APPROVAL_PENDING",
            "CUSTODIAN_APPROVAL_REJECTED",
            "CUSTODIAN_APPROVAL_GRANTED",
            "ACTION_BLOCKED",
            "ACTION_CHECKPOINT",
            "TOOL_INVOKED",
            "RISK_BUDGET_EXHAUSTED",
            "TIMEOUT",
            "DRIFT_DETECTED",
        }
        if event_type not in allowed_events:
            return "UNKNOWN_EVENT"
        return event_type

    def _rotate_logs_if_needed(self):
        """P2: Rotate logs based on size and age (30-day retention)."""
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

                except OSError as e:
                    # FIX #3: Log rotation errors instead of silent fail
                    print(f"[WARN] Log rotation failed for {log_file}: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"[WARN] Unexpected error rotating {log_file}: {e}", file=sys.stderr)

        except Exception as e:
            # FIX #3: Log the error instead of silently failing
            print(f"[WARN] Log rotation check failed: {e}", file=sys.stderr)

    def _rotate_current_log(self):
        """Rotate the current log file (timestamp-based)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_path = f"{self.audit_log_path}.{timestamp}"
        try:
            if os.path.exists(self.audit_log_path):
                os.rename(self.audit_log_path, rotated_path)
                self._init_audit_log()
        except OSError as e:
            # FIX #3: Log rotation errors
            print(f"[WARN] Could not rotate log file: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] Unexpected error during log rotation: {e}", file=sys.stderr)

    def _init_audit_log(self):
        """P2: Initialize append-only audit log"""
        try:
            log_dir = os.path.dirname(self.audit_log_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            if not self._is_safe_log_path(self.audit_log_path):
                raise RuntimeError("Unsafe audit log path")

            if not os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, "w") as f:
                    f.write(f"# Helix Audit Log - Initialized {datetime.now().isoformat()}\n")
                    f.write(f"# Agent ID: {self.agent_id}\n")
                    f.write("# Log Rotation: 30 days / 100MB\n")
                    f.flush()
        except Exception as e:
            import sys

            error_msg = str(e)
            if hasattr(self, "audit_log_path") and self.audit_log_path in error_msg:
                error_msg = error_msg.replace(self.audit_log_path, "<LOG_PATH>")
            home_dir = os.path.expanduser("~")
            if home_dir in error_msg:
                error_msg = error_msg.replace(home_dir, "~")
            print(f"WARN: Could not init audit log: {error_msg}", file=sys.stderr)

    def _append_audit(self, event_type: str, data: dict):
        """P2: Append event to audit log (fsync for durability, sanitized)"""
        try:
            self._rotate_logs_if_needed()

            if not self._is_safe_log_path(self.audit_log_path):
                raise RuntimeError("Unsafe audit log path")

            safe_event_type = self._validate_event_type(event_type)
            safe_data = self._sanitize_audit_data(data)

            entry = {"ts": datetime.now().isoformat(), "type": safe_event_type, "data": safe_data}
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(entry, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            import sys

            error_msg = str(e)
            if hasattr(self, "audit_log_path") and self.audit_log_path in error_msg:
                error_msg = error_msg.replace(self.audit_log_path, "<LOG_PATH>")
            home_dir = os.path.expanduser("~")
            if home_dir in error_msg:
                error_msg = error_msg.replace(home_dir, "~")
            print(f"WARN: Audit log write failed: {error_msg}", file=sys.stderr)

    def register_tool(self, name: str, function: Callable, risk_level: float = 0.5):
        """Register a tool with the agent - requires constitutional approval.

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

        func_module = getattr(function, "__module__", None)
        if func_module in ("__builtin__", "builtins", "os", "subprocess", "sys"):
            raise ValueError(f"Tool '{name}': Module '{func_module}' not allowed")

        if not isinstance(risk_level, (int, float)):
            raise ValueError(f"Tool '{name}': Risk level must be numeric")
        if risk_level < 0 or risk_level > 1:
            raise ValueError(f"Tool '{name}': Risk level must be 0.0-1.0")

        if not isinstance(name, str) or not name:
            raise ValueError("Tool name must be non-empty string")
        if any(c in name for c in ["/", "\\", "..", "\x00"]):
            raise ValueError(f"Tool '{name}': Invalid characters in name")

        # P1: Thread-safe atomic registration
        with self._tool_lock:
            self.gate.allowed_tools.add(name)
            self.available_tools[name] = {
                "function": function,
                "risk_level": float(risk_level),
                "registered_at": time.time(),
                "module": func_module,
                "name": name,
            }

        self._append_audit(
            "TOOL_REGISTERED", {"tool_name": name, "risk_level": risk_level, "module": func_module}
        )

    def create_plan(self, objective: str, context: dict[str, Any]) -> AgentPlan:
        """Agent proposes a plan based on objective and context.

        FIX #2: Previously hardcoded 'analyze' branch only. Now uses context
        and available tools to construct dynamic plans.
        """
        steps = []
        assumptions = ["Tools required by plan are registered and authorized"]

        # Use context to inform plan construction
        target_files = context.get("files", [])
        target_directory = context.get("directory", "")
        file_pattern = context.get("pattern", "*.py")

        # Build plan based on available tools and objective
        if "search" in objective.lower() or "find" in objective.lower():
            steps.append(
                AgentAction(
                    action_id="act_search",
                    action_type="search",
                    tool_name="file_search",
                    parameters={"pattern": file_pattern, "directory": target_directory},
                    rationale="[HYPOTHESIS] Search will locate relevant files matching criteria",
                    epistemic_basis=EpistemicLabel.HYPOTHESIS,
                    estimated_risk=0.2,
                )
            )
            assumptions.append("Target directory exists and is readable")

        if "read" in objective.lower() or "analyze" in objective.lower():
            read_target = target_files if target_files else {"path": "detected_files"}
            steps.append(
                AgentAction(
                    action_id="act_read",
                    action_type="read",
                    tool_name="file_read",
                    parameters={"files": read_target},
                    rationale="[FACT] Files must be read to access their content",
                    epistemic_basis=EpistemicLabel.FACT,
                    estimated_risk=0.1,
                )
            )
            assumptions.append("Files are accessible and readable")

        if "analyze" in objective.lower():
            steps.append(
                AgentAction(
                    action_id="act_analyze",
                    action_type="analyze",
                    tool_name="static_analysis",
                    parameters={"files": "read_content", "context": context},
                    rationale="[HYPOTHESIS] Static analysis will identify patterns and opportunities",
                    epistemic_basis=EpistemicLabel.HYPOTHESIS,
                    estimated_risk=0.3,
                )
            )

        # Fallback: generic plan if no specific handlers matched
        if not steps:
            steps.append(
                AgentAction(
                    action_id="act_generic",
                    action_type="process",
                    tool_name="generic_handler",
                    parameters={"objective": objective, "context": context},
                    rationale="[ASSUMPTION] Generic processing may satisfy objective",
                    epistemic_basis=EpistemicLabel.ASSUMPTION,
                    estimated_risk=0.5,
                )
            )
            assumptions.append("Generic handler can process this objective")

        plan = AgentPlan(
            plan_id=f"plan_{int(time.time())}",
            objective=objective,
            steps=steps,
            assumptions=assumptions,
            estimated_completion=len(steps) * 2.0,  # Rough estimate
        )

        return plan

    def execute_with_checkpoints(
        self, plan: AgentPlan, custodian_approval: bool | None = None
    ) -> dict:
        """Execute a plan with full Helix-TTD checkpointing.

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
                    "reason": f"Plan exceeds maximum {self.MAX_PLAN_STEPS} steps (DoS protection)",
                }

            start_time = time.time()

            results = {
                "plan_id": plan.plan_id,
                "checkpoints": [],
                "executions": [],
                "status": "pending",
                "final_anchor": "",
                "start_time": datetime.now().isoformat(),
            }

            self._append_audit(
                "PLAN_EXECUTION_START",
                {
                    "plan_id": plan.plan_id,
                    "steps": len(plan.steps),
                    "custodian_override": custodian_approval,
                },
            )

            # Checkpoint 1: Plan Validation
            plan_checkpoint = self.gate.validate_plan(plan)
            results["checkpoints"].append(
                {
                    "id": plan_checkpoint.checkpoint_id,
                    "compliance": plan_checkpoint.compliance_score,
                    "drift": plan_checkpoint.drift_detected,
                    "codes": plan_checkpoint.drift_codes,
                    "scope": "plan",
                }
            )

            if not plan.constitutional_clearance:
                results["status"] = "rejected_at_planning"
                results["reason"] = f"Constitutional violation: {plan_checkpoint.drift_codes}"
                self._append_audit(
                    "PLAN_EXECUTION_REJECTED",
                    {"plan_id": plan.plan_id, "reason": results["reason"]},
                )
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
                    self._append_audit(
                        "TIMEOUT",
                        {"plan_id": plan.plan_id, "elapsed": elapsed, "completed_steps": step_idx},
                    )
                    return results

                # Checkpoint 2: Pre-execution validation
                action_checkpoint = self.gate.validate_action(step, {})
                results["checkpoints"].append(
                    {
                        "id": action_checkpoint.checkpoint_id,
                        "compliance": action_checkpoint.compliance_score,
                        "drift": action_checkpoint.drift_detected,
                        "codes": action_checkpoint.drift_codes,
                        "scope": "action",
                        "action_id": step.action_id,
                    }
                )

                if action_checkpoint.drift_detected and action_checkpoint.compliance_score < 0.5:
                    results["executions"].append(
                        {
                            "action_id": step.action_id,
                            "status": "blocked",
                            "reason": action_checkpoint.drift_codes,
                        }
                    )
                    self._append_audit(
                        "ACTION_BLOCKED",
                        {
                            "plan_id": plan.plan_id,
                            "action_id": step.action_id,
                            "reason": action_checkpoint.drift_codes,
                        },
                    )
                    continue

                # Check for custodian gate
                if step.requires_approval or self.gate.agency_tier == AgencyLevel.CUSTODIAN_GATE:
                    if custodian_approval is None:
                        results["executions"].append(
                            {
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
                                    "epistemic_basis": (
                                        step.epistemic_basis.value
                                        if isinstance(step.epistemic_basis, EpistemicLabel)
                                        else str(step.epistemic_basis)
                                    ),
                                    "estimated_risk": step.estimated_risk,
                                    "requires_approval": step.requires_approval,
                                },
                            }
                        )
                        results["status"] = "awaiting_custodian_approval"
                        results["pending_action"] = step.action_id
                        results["completed_steps"] = step_idx
                        self._append_audit(
                            "CUSTODIAN_APPROVAL_PENDING",
                            {"plan_id": plan.plan_id, "action_id": step.action_id},
                        )
                        return results
                    elif not custodian_approval:
                        results["executions"].append(
                            {"action_id": step.action_id, "status": "rejected_by_custodian"}
                        )
                        results["status"] = "rejected_by_custodian"
                        results["completed_steps"] = step_idx
                        self._append_audit(
                            "CUSTODIAN_APPROVAL_REJECTED",
                            {"plan_id": plan.plan_id, "action_id": step.action_id},
                        )
                        return results

                # Execute (simulated)
                execution_result = self._simulate_execution(step, plan_id=plan.plan_id)

                results["executions"].append(
                    {
                        "action_id": step.action_id,
                        "status": "completed",
                        # BUG-2 Fix: Full SHA-256, no truncation. Truncation to [:16]
                        # reintroduced collision risk inconsistent with the P0 fix applied
                        # elsewhere (ConstitutionalCheckpoint.compute_hash).
                        "result_hash": hashlib.sha256(str(execution_result).encode()).hexdigest(),
                    }
                )

            # Final anchor
            results["status"] = "completed_with_checkpoints"
            results["final_anchor"] = self._compute_merkle_root(results["checkpoints"])
            results["execution_time"] = time.time() - start_time

            self._append_audit(
                "PLAN_EXECUTION_COMPLETE",
                {
                    "plan_id": plan.plan_id,
                    "status": results["status"],
                    "checkpoints": len(results["checkpoints"]),
                    "executions": len(
                        [e for e in results["executions"] if e.get("status") == "completed"]
                    ),
                    "execution_time": results["execution_time"],
                    "merkle_root": results["final_anchor"][:16] + "...",
                },
            )

            return results

    def _simulate_execution(self, action: AgentAction, plan_id: str | None = None) -> Any:
        """Execute tool function with parameter injection and error handling.

        FIX #1: Previously returned stub {"status": "success"} without calling
        the actual function. Now properly invokes registered tools with context.

        ENHANCEMENT #5: Added memoization support for expensive operations.
        """
        with self._tool_lock:
            if action.tool_name not in self.available_tools:
                return {"status": "tool_not_found", "tool": action.tool_name}

            if action.tool_name not in self.gate.allowed_tools:
                return {"status": "tool_unauthorized", "tool": action.tool_name}

            tool_entry = self.available_tools[action.tool_name]
            tool_func = tool_entry["function"]
            tool_risk = tool_entry.get("risk_level", 0.5)

        # ENHANCEMENT #5: Check memoization cache first
        cached = self._get_cached_result(action)
        if cached is not None:
            self._append_audit(
                "TOOL_INVOKED",
                {
                    "plan_id": plan_id,
                    "action_id": action.action_id,
                    "tool": action.tool_name,
                    "epistemic": (
                        action.epistemic_basis.value
                        if isinstance(action.epistemic_basis, EpistemicLabel)
                        else str(action.epistemic_basis)
                    ),
                    "risk_level": tool_risk,
                    "cached": True,
                },
            )
            return {
                "status": "success",
                "tool": action.tool_name,
                "result": cached,
                "result_type": type(cached).__name__,
                "cached": True,
            }

        self._append_audit(
            "TOOL_INVOKED",
            {
                "plan_id": plan_id,
                "action_id": action.action_id,
                "tool": action.tool_name,
                "epistemic": (
                    action.epistemic_basis.value
                    if isinstance(action.epistemic_basis, EpistemicLabel)
                    else str(action.epistemic_basis)
                ),
                "risk_level": tool_risk,
                "cached": False,
            },
        )

        # FIX #1: Actually execute the tool with error handling
        try:
            # Inspect function signature to determine parameter passing strategy
            sig = inspect.signature(tool_func)
            param_count = len(sig.parameters)

            if param_count == 0:
                # No-argument function
                result = tool_func()
            elif param_count == 1:
                # Single parameter - pass the parameters dict
                result = tool_func(action.parameters)
            else:
                # Multi-parameter - pass as kwargs if parameters is dict
                if isinstance(action.parameters, dict):
                    result = tool_func(**action.parameters)
                else:
                    result = tool_func(action.parameters)

            # ENHANCEMENT #5: Cache the result for future use
            self._cache_result(action, result)

            return {
                "status": "success",
                "tool": action.tool_name,
                "result": result,
                "result_type": type(result).__name__,
                "cached": False,
            }
        except Exception as e:
            error_msg = str(e)
            # Sanitize error to prevent log injection
            error_msg = error_msg.replace("\n", " ").replace("\r", " ")[:500]
            return {
                "status": "execution_failed",
                "tool": action.tool_name,
                "error": error_msg,
                "error_type": type(e).__name__,
            }

    def _compute_merkle_root(self, checkpoints: list[dict]) -> str:
        """Compute proper Merkle root of all checkpoint content (P0 Fix).

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
                right = leaves[i + 1] if i + 1 < len(leaves) else leaves[i]
                parent = hashlib.sha256(left + right).digest()
                next_level.append(parent)
            leaves = next_level

        return leaves[0].hex()

    # ENHANCEMENT #2: Async Execution Support
    async def execute_async(self, plan: AgentPlan, custodian_approval: bool | None = None) -> dict:
        """Async version of execute_with_checkpoints for I/O-bound tools.

        Allows concurrent execution of independent actions while maintaining
        constitutional checkpoints for each step.
        """
        import asyncio

        with self._execution_lock:
            if len(plan.steps) > self.MAX_PLAN_STEPS:
                return {
                    "plan_id": plan.plan_id,
                    "status": "rejected",
                    "reason": f"Plan exceeds maximum {self.MAX_PLAN_STEPS} steps",
                }

            start_time = time.time()
            results = {
                "plan_id": plan.plan_id,
                "checkpoints": [],
                "executions": [],
                "status": "pending",
                "final_anchor": "",
                "start_time": datetime.now().isoformat(),
            }

            # Validate plan first (synchronous)
            plan_checkpoint = self.gate.validate_plan(plan)
            results["checkpoints"].append(
                {
                    "id": plan_checkpoint.checkpoint_id,
                    "compliance": plan_checkpoint.compliance_score,
                    "drift": plan_checkpoint.drift_detected,
                    "codes": plan_checkpoint.drift_codes,
                    "scope": "plan",
                }
            )

            if not plan.constitutional_clearance:
                results["status"] = "rejected_at_planning"
                results["reason"] = f"Constitutional violation: {plan_checkpoint.drift_codes}"
                return results

            # Execute steps asynchronously
            for step_idx, step in enumerate(plan.steps):
                elapsed = time.time() - start_time
                if elapsed > self.MAX_EXECUTION_TIME:
                    results["status"] = "timeout"
                    results["reason"] = f"Execution exceeded {self.MAX_EXECUTION_TIME}s limit"
                    results["completed_steps"] = step_idx
                    return results

                # Validate action
                action_checkpoint = self.gate.validate_action(step, {})
                results["checkpoints"].append(
                    {
                        "id": action_checkpoint.checkpoint_id,
                        "compliance": action_checkpoint.compliance_score,
                        "drift": action_checkpoint.drift_detected,
                        "codes": action_checkpoint.drift_codes,
                        "scope": "action",
                        "action_id": step.action_id,
                    }
                )

                if action_checkpoint.drift_detected and action_checkpoint.compliance_score < 0.5:
                    results["executions"].append(
                        {
                            "action_id": step.action_id,
                            "status": "blocked",
                            "reason": action_checkpoint.drift_codes,
                        }
                    )
                    continue

                # Check custodian gate
                if step.requires_approval or self.gate.agency_tier == AgencyLevel.CUSTODIAN_GATE:
                    if custodian_approval is None:
                        results["status"] = "awaiting_custodian_approval"
                        results["pending_action"] = step.action_id
                        return results
                    elif not custodian_approval:
                        results["status"] = "rejected_by_custodian"
                        return results

                # Async execution
                execution_result = await self._execute_tool_async(step, plan_id=plan.plan_id)
                results["executions"].append(
                    {
                        "action_id": step.action_id,
                        "status": (
                            "completed" if execution_result.get("status") == "success" else "failed"
                        ),
                        "result_hash": hashlib.sha256(str(execution_result).encode()).hexdigest(),
                    }
                )

                # Small yield to allow other async tasks
                await asyncio.sleep(0)

            results["status"] = "completed_with_checkpoints"
            results["final_anchor"] = self._compute_merkle_root(results["checkpoints"])
            results["execution_time"] = time.time() - start_time
            return results

    async def _execute_tool_async(self, action: AgentAction, plan_id: str | None = None) -> Any:
        """Execute a tool asynchronously, handling both sync and async functions."""
        import asyncio
        import inspect

        with self._tool_lock:
            if action.tool_name not in self.available_tools:
                return {"status": "tool_not_found", "tool": action.tool_name}

            tool_entry = self.available_tools[action.tool_name]
            tool_func = tool_entry["function"]

        # Check if function is async
        if inspect.iscoroutinefunction(tool_func):
            # It's already async - await it directly
            try:
                sig = inspect.signature(tool_func)
                param_count = len(sig.parameters)
                if param_count == 0:
                    result = await tool_func()
                elif param_count == 1:
                    result = await tool_func(action.parameters)
                else:
                    if isinstance(action.parameters, dict):
                        result = await tool_func(**action.parameters)
                    else:
                        result = await tool_func(action.parameters)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "execution_failed", "error": str(e)}
        else:
            # Run synchronous function in thread pool to prevent blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, lambda: self._simulate_execution(action, plan_id)  # Uses default executor
            )

    # ENHANCEMENT #3: Plan Serialization & Resume
    def plan_to_json(self, plan: AgentPlan) -> str:
        """Serialize a plan to JSON for persistence or transfer."""
        return json.dumps(
            {
                "plan_id": plan.plan_id,
                "objective": plan.objective,
                "steps": [
                    {
                        "action_id": step.action_id,
                        "action_type": step.action_type,
                        "tool_name": step.tool_name,
                        "parameters": step.parameters,
                        "rationale": step.rationale,
                        "epistemic_basis": step.epistemic_basis.value,
                        "estimated_risk": step.estimated_risk,
                        "requires_approval": step.requires_approval,
                    }
                    for step in plan.steps
                ],
                "assumptions": plan.assumptions,
                "estimated_completion": plan.estimated_completion,
                "constitutional_clearance": plan.constitutional_clearance,
                "plan_checkpoint": (
                    {
                        "checkpoint_id": plan.plan_checkpoint.checkpoint_id,
                        "timestamp": plan.plan_checkpoint.timestamp,
                        "layer": plan.plan_checkpoint.layer,
                        "compliance_score": plan.plan_checkpoint.compliance_score,
                        "drift_detected": plan.plan_checkpoint.drift_detected,
                        "drift_codes": plan.plan_checkpoint.drift_codes,
                        "merkle_hash": plan.plan_checkpoint.merkle_hash,
                    }
                    if plan.plan_checkpoint
                    else None
                ),
            },
            indent=2,
        )

    @classmethod
    def plan_from_json(cls, json_str: str) -> AgentPlan:
        """Deserialize a plan from JSON."""
        data = json.loads(json_str)

        steps = [
            AgentAction(
                action_id=step["action_id"],
                action_type=step["action_type"],
                tool_name=step["tool_name"],
                parameters=step["parameters"],
                rationale=step["rationale"],
                epistemic_basis=EpistemicLabel(step["epistemic_basis"]),
                estimated_risk=step["estimated_risk"],
                requires_approval=step.get("requires_approval", False),
            )
            for step in data["steps"]
        ]

        plan_checkpoint = None
        if data.get("plan_checkpoint"):
            cp = data["plan_checkpoint"]
            plan_checkpoint = ConstitutionalCheckpoint(
                checkpoint_id=cp["checkpoint_id"],
                timestamp=cp["timestamp"],
                layer=cp["layer"],
                compliance_score=cp["compliance_score"],
                drift_detected=cp["drift_detected"],
                drift_codes=cp.get("drift_codes", []),
                merkle_hash=cp.get("merkle_hash", ""),
            )

        return AgentPlan(
            plan_id=data["plan_id"],
            objective=data["objective"],
            steps=steps,
            assumptions=data["assumptions"],
            estimated_completion=data["estimated_completion"],
            constitutional_clearance=data.get("constitutional_clearance", False),
            plan_checkpoint=plan_checkpoint,
        )

    def save_plan_state(self, plan: AgentPlan, filepath: str):
        """Save plan state to file for later resumption."""
        with open(filepath, "w") as f:
            f.write(self.plan_to_json(plan))

    @classmethod
    def load_plan_state(cls, filepath: str) -> AgentPlan:
        """Load plan state from file."""
        with open(filepath) as f:
            return cls.plan_from_json(f.read())
