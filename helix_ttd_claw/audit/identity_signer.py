"""[FACT] Digital Birth Certificate (DBC) identity signing for audit trails.

[HYPOTHESIS] DBC-linked signatures provide forensic non-repudiation.
[ASSUMPTION] DBC files contain identity and public key metadata.
"""

# Canonical hardened implementation lives in code/openclaw_agent.py.
# Re-export here to ensure a single secure DBC source across the repo.
from openclaw_agent import CheckpointIdentitySigner, DBCIdentity

__all__ = ["DBCIdentity", "CheckpointIdentitySigner"]
