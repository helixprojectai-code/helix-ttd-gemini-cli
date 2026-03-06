"""[FACT] Helix-TTD-Claw Agent: Constitutional AI Governance Package.

[HYPOTHESIS] This package provides modular access to the constitutional governance system:
- core: Types, enums, and configuration
- gate: 4-layer constitutional pipeline
- audit: Persistence, SIEM, metrics, and DBC identity signing
- federation: Multi-agent consensus, DBC cross-node verification, and approvals
- agent: The bounded agent implementation
- topology: Lattice structure, Merkle bridging, Layer 5 witness (v1.4.0)
- utils: Crypto and validation helpers

[ASSUMPTION] All submodules are importable and functional.

Version: 1.4.0
License: Apache-2.0
"""

# v1.4.0: Lattice Topology - Paper III/IV implementation (Merkle bridge, Layer 5 witness)
# v1.3.2: Security Hardening - Ed25519, Fernet encryption, Red Team remediation
# v1.3.1: DBC Federation - Cross-node signature verification
# v1.3.0: DBC Integration - Non-repudiable audit trails with identity signing
# All exports from original openclaw_agent.py are preserved

# Import all public APIs from openclaw_agent for backwards compatibility
# This allows both:
#   from helix_ttd_claw import OpenClawAgent  (new way)
#   from openclaw_agent import OpenClawAgent  (old way - still works)

from article_zero import (
    ArticleZeroProtocol,
    ConstitutionalConstant,
    ZTCEvent,
    ZTCEventType,
    get_constant,
)
from deepseek_bridge import DeepSeekBridge, DeepSeekModel, DeepSeekReceipt, FederationRouter
from federation_receipts import (
    CrossNodeVerifier,
    EpistemicMarkers,
    FederationReceipt,
    FederationReceiptManager,
    NodeType,
    QuorumAttestation,
    ReceiptMigrator,
    ReceiptVersion,
)

# v1.4.0: Lattice Topology imports (Paper III)
from lattice_topology import (
    CustodialHierarchy,
    DriftDetector,
    EpistemicCategory,
    LatticePosition,
    RPICycle,
)
from merkle_bridge import ConstitutionalContinuity, L2Entry, MerkleBridge
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
from shlorpian_mapper import (
    ConstitutionalMemorandum,
    ConstitutionalRole,
    ShlorpianCharacter,
    ShlorpianDriftDetector,
    ShlorpianTopology,
)
from suitcase import (
    AzureBlobStorage,
    AzureKeyVault,
    CloudProvider,
    EVACStateManager,
    MultiCloudReplicator,
    SuitcaseBundle,
    SuitcaseSerializer,
)
from witness_node import (
    DuckProtocol,
    Layer5Infrastructure,
    OwlProtocol,
    OysterProtocol,
    WitnessType,
)

__version__ = "1.4.0"
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
    # Topology (v1.4.0 - Paper III/IV)
    "LatticePosition",
    "CustodialHierarchy",
    "RPICycle",
    "DriftDetector",
    "EpistemicCategory",
    "MerkleBridge",
    "L2Entry",
    "ConstitutionalContinuity",
    "OwlProtocol",
    "DuckProtocol",
    "OysterProtocol",
    "Layer5Infrastructure",
    "WitnessType",
    # Shlorpian (Paper IV)
    "ShlorpianCharacter",
    "ConstitutionalRole",
    "ShlorpianTopology",
    "ConstitutionalMemorandum",
    "ShlorpianDriftDetector",
    # Article 0 (Paper IV)
    "ArticleZeroProtocol",
    "ZTCEvent",
    "ZTCEventType",
    "ConstitutionalConstant",
    "get_constant",
    # Federation (Milestone 3)
    "NodeType",
    "ReceiptVersion",
    "EpistemicMarkers",
    "FederationReceipt",
    "ReceiptMigrator",
    "QuorumAttestation",
    "CrossNodeVerifier",
    "FederationReceiptManager",
    "DeepSeekModel",
    "DeepSeekReceipt",
    "DeepSeekBridge",
    "FederationRouter",
    # EVAC (Milestone 4)
    "CloudProvider",
    "SuitcaseBundle",
    "SuitcaseSerializer",
    "AzureBlobStorage",
    "AzureKeyVault",
    "MultiCloudReplicator",
    "EVACStateManager",
]
