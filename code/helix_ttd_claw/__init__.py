"""[FACT] Helix-TTD-Claw Agent: Constitutional AI Governance Package.

[HYPOTHESIS] This package provides modular access to the constitutional governance system:
- core: Types, enums, and configuration
- gate: 4-layer constitutional pipeline
- audit: Persistence, SIEM, metrics, and DBC identity signing
- federation: Multi-agent consensus, DBC cross-node verification, and approvals
- agent: The bounded agent implementation
- utils: Crypto and validation helpers

[ASSUMPTION] All submodules are importable and functional.

Version: 1.3.1
License: Apache-2.0
"""

# v1.3.1: DBC Federation - Cross-node signature verification
# v1.3.0: DBC Integration - Non-repudiable audit trails with identity signing
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
    DBCFederationRegistry,
    DBCIdentity,
    EpistemicLabel,
    FederatedCheckpointValidator,
    HelixConstitutionalGate,
    MetricsCollector,
    MultiAgentCheckpointConsensus,
    OpenClawAgent,
    PluginRegistry,
    RateLimitLayer,
    RiskConfiguration,
    SIEMExporter,
)

__version__ = "1.3.2"
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
    "DBCIdentity",  # v1.3.0: DBC-signed checkpoints
    "DBCFederationRegistry",  # v1.3.1: Cross-node verification
    # Federation
    "MultiAgentCheckpointConsensus",
    "CustodianApprovalAPI",
    "FederatedCheckpointValidator",
    # Agent
    "OpenClawAgent",
]
