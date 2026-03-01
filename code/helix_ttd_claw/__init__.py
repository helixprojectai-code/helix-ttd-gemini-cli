"""[FACT] Helix-TTD-Claw Agent: Constitutional AI Governance Package.

[HYPOTHESIS] This package provides modular access to the constitutional governance system:
- core: Types, enums, and configuration
- gate: 4-layer constitutional pipeline
- audit: Persistence, SIEM, and metrics
- federation: Multi-agent consensus and approvals
- agent: The bounded agent implementation
- utils: Crypto and validation helpers

[ASSUMPTION] All submodules are importable and functional.

Version: 1.2.2
License: Apache-2.0
"""

# v1.2.2: Package decoupling - maintaining backwards compatibility
# All exports from original openclaw_agent.py are preserved

# Import all public APIs from openclaw_agent for backwards compatibility
# This allows both:
#   from helix_ttd_claw import OpenClawAgent  (new way)
#   from openclaw_agent import OpenClawAgent  (old way - still works)

from openclaw_agent import (  # Core types; Gate; Audit; Federation; Agent
    AgencyLevel,
    AgentAction,
    AgentPlan,
    CheckpointStore,
    ComplianceAuditLayer,
    ConstitutionalCheckpoint,
    ConstitutionalLayer,
    CustodianApprovalAPI,
    EpistemicLabel,
    HelixConstitutionalGate,
    MetricsCollector,
    MultiAgentCheckpointConsensus,
    OpenClawAgent,
    PluginRegistry,
    RateLimitLayer,
    RiskConfiguration,
    SIEMExporter,
)

__version__ = "1.2.2"
__author__ = "Stephen Hope"
__license__ = "Apache-2.0"

# Package-level exports
__all__ = [
    # Version
    "__version__",
    # Core types
    "AgencyLevel",
    "EpistemicLabel",
    "AgentAction",
    "AgentPlan",
    "ConstitutionalCheckpoint",
    "RiskConfiguration",
    # Gate
    "HelixConstitutionalGate",
    "ConstitutionalLayer",
    "PluginRegistry",
    "ComplianceAuditLayer",
    "RateLimitLayer",
    # Audit
    "CheckpointStore",
    "SIEMExporter",
    "MetricsCollector",
    # Federation
    "MultiAgentCheckpointConsensus",
    "CustodianApprovalAPI",
    # Agent
    "OpenClawAgent",
]
