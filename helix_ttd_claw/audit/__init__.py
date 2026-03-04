"""[FACT] Audit module for non-repudiable checkpoint signing.

[HYPOTHESIS] DBC-linked signatures create forensic audit trails.
[ASSUMPTION] All checkpoints should be cryptographically signed.
"""

from .identity_signer import CheckpointIdentitySigner, DBCIdentity

__all__ = ["DBCIdentity", "CheckpointIdentitySigner"]
