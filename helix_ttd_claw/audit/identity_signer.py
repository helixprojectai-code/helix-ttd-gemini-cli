"""[FACT] Digital Birth Certificate (DBC) identity signing for audit trails.

[HYPOTHESIS] DBC-linked signatures provide forensic non-repudiation.
[ASSUMPTION] DBC files contain identity and public key metadata.
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class DBCIdentity:
    """[FACT] DBC identity wrapper for cryptographic signing.
    
    [HYPOTHESIS] Each agent has a unique DBC establishing identity chain.
    [ASSUMPTION] DBC files are immutable once created.
    """
    
    def __init__(self, dbc_path: Optional[Path] = None):
        """[FACT] Initialize DBC identity from file.
        
        Args:
            dbc_path: Path to DBC JSON file. If None, uses environment default.
        """
        self.dbc_path = dbc_path or self._find_dbc()
        self.dbc_data: dict = {}
        self._private_key: Optional[str] = None
        self._loaded = False
        
    def _find_dbc(self) -> Path:
        """[FACT] Locate DBC file in standard locations."""
        # Check environment variable first
        import os
        if dbc_env := os.environ.get("HELIX_DBC_PATH"):
            return Path(dbc_env)
        
        # Standard locations by node type
        workspace = Path("Z:/gemini")
        evac_dir = workspace / "EVAC"
        
        # Try gems.dbc.json first (GEMS substrate)
        dbc_file = evac_dir / "gems.dbc.json"
        if dbc_file.exists():
            return dbc_file
            
        # Fallback to kimi.dbc.json (KIMI substrate)
        dbc_file = Path("Z:/kimi/EVAC/kimi.dbc.json")
        if dbc_file.exists():
            return dbc_file
            
        # Default to gems location (will need creation)
        return evac_dir / "gems.dbc.json"
    
    def load(self) -> "DBCIdentity":
        """[FACT] Load DBC from disk.
        
        Returns:
            Self for chaining.
            
        Raises:
            FileNotFoundError: If DBC file doesn't exist.
        """
        if not self.dbc_path.exists():
            raise FileNotFoundError(
                f"[ASSUMPTION] DBC not found at {self.dbc_path}. "
                "Run DBC creation first."
            )
            
        with open(self.dbc_path, 'r', encoding='utf-8') as f:
            self.dbc_data = json.load(f)
            
        self._loaded = True
        return self
    
    def load_or_create(
        self,
        agent_name: Optional[str] = None,
        custodian_id: Optional[str] = None
    ) -> "DBCIdentity":
        """[FACT] Load existing DBC or create new one.
        
        Args:
            agent_name: Name for new DBC if creation needed.
            custodian_id: Custodian for new DBC if creation needed.
            
        Returns:
            Self for chaining.
        """
        try:
            return self.load()
        except FileNotFoundError:
            return self._create_default(agent_name, custodian_id)
    
    def _create_default(
        self,
        agent_name: Optional[str] = None,
        custodian_id: Optional[str] = None
    ) -> "DBCIdentity":
        """[FACT] Create minimal DBC for testing/development."""
        # Generate keypair simulation (in production, use proper crypto)
        key_seed = f"{agent_name or 'agent'}_{uuid.uuid4().hex[:16]}"
        self._private_key = hashlib.sha256(key_seed.encode()).hexdigest()
        public_key = hashlib.sha256(self._private_key.encode()).hexdigest()
        
        self.dbc_data = {
            "version": "v0.3",
            "type": "DBC",
            "agent_name": agent_name or f"Agent-{uuid.uuid4().hex[:8]}",
            "custodian_id": custodian_id or "System",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "creation_reason": "Auto-generated for audit signing",
            "hardware_sig": "SIMULATED",
            "parent_dbc": None,
            "public_key": public_key,
            "merkle_root": hashlib.sha256(public_key.encode()).hexdigest(),
            "dbc_id": f"DBC-{uuid.uuid4().hex[:16]}",
        }
        
        # Ensure directory exists
        self.dbc_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.dbc_path, 'w', encoding='utf-8') as f:
            json.dump(self.dbc_data, f, indent=2)
            
        self._loaded = True
        return self
    
    @property
    def dbc_id(self) -> str:
        """[FACT] Return DBC identifier."""
        return self.dbc_data.get("dbc_id", "UNKNOWN")
    
    @property
    def agent_name(self) -> str:
        """[FACT] Return agent name from DBC."""
        return self.dbc_data.get("agent_name", "Unknown")
    
    @property
    def public_key(self) -> str:
        """[FACT] Return public key for signature verification."""
        # If DBC has public_key field, use it
        if "public_key" in self.dbc_data:
            return self.dbc_data["public_key"]
        # Otherwise derive from merkle_root (legacy DBCs)
        return self.dbc_data.get("merkle_root", "UNKNOWN")
    
    def sign(self, data: bytes) -> str:
        """[FACT] Sign data using DBC-linked private key.
        
        [HYPOTHESIS] HMAC-SHA256 provides sufficient non-repudiation
        for audit trails within the Helix federation.
        
        [ASSUMPTION] Private key is derived from DBC creation entropy
        and stored securely (simulated here for architecture).
        
        Args:
            data: Raw bytes to sign.
            
        Returns:
            Hex-encoded signature string.
        """
        if not self._loaded:
            self.load()
            
        # In production: use proper HSM or key management
        # Here we simulate deterministic signing from DBC
        private_key = self._get_private_key()
        
        # HMAC-SHA256 signature
        import hmac
        signature = hmac.new(
            private_key.encode(),
            data,
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _get_private_key(self) -> str:
        """[FACT] Retrieve or derive private key for signing.
        
        [ASSUMPTION] In production, this interfaces with HSM/TPM.
        [ASSUMPTION] For simulation, we derive from DBC entropy.
        """
        if self._private_key:
            return self._private_key
            
        # Derive deterministic key from DBC data
        # In production: retrieve from secure storage
        dbc_entropy = f"{self.dbc_id}:{self.dbc_data.get('merkle_root', '')}"
        self._private_key = hashlib.sha256(dbc_entropy.encode()).hexdigest()
        return self._private_key
    
    def verify(self, data: bytes, signature: str) -> bool:
        """[FACT] Verify signature against DBC public key.
        
        Args:
            data: Raw bytes that were signed.
            signature: Hex-encoded signature to verify.
            
        Returns:
            True if signature is valid.
        """
        expected = self.sign(data)
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected, signature)


class CheckpointIdentitySigner:
    """[FACT] Signs constitutional checkpoints with DBC identity.
    
    [HYPOTHESIS] Linking checkpoints to DBC creates non-repudiable audit.
    [ASSUMPTION] Each checkpoint hash is signed by the agent that created it.
    """
    
    def __init__(self, identity: Optional[DBCIdentity] = None):
        """[FACT] Initialize signer with DBC identity.
        
        Args:
            identity: DBC identity to use. If None, loads from default location.
        """
        self.identity = identity or DBCIdentity().load_or_create()
        
    def sign_checkpoint(self, checkpoint_hash: str) -> dict:
        """[FACT] Sign checkpoint hash with DBC identity.
        
        Args:
            checkpoint_hash: Hash of the checkpoint data.
            
        Returns:
            Signature bundle with metadata for verification.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Create signed payload
        payload = f"{checkpoint_hash}:{timestamp}:{self.identity.dbc_id}"
        signature = self.identity.sign(payload.encode())
        
        return {
            "signature": signature,
            "dbc_id": self.identity.dbc_id,
            "agent_name": self.identity.agent_name,
            "public_key": self.identity.public_key,
            "timestamp": timestamp,
            "algorithm": "HMAC-SHA256",
        }
    
    def verify_checkpoint(self, checkpoint_hash: str, signature_bundle: dict) -> bool:
        """[FACT] Verify checkpoint signature against DBC identity.
        
        Args:
            checkpoint_hash: Hash of the checkpoint data.
            signature_bundle: Signature bundle from sign_checkpoint.
            
        Returns:
            True if signature is valid.
        """
        # Reconstruct payload
        timestamp = signature_bundle.get("timestamp")
        dbc_id = signature_bundle.get("dbc_id")
        payload = f"{checkpoint_hash}:{timestamp}:{dbc_id}"
        
        # Verify signature matches
        expected = self.identity.sign(payload.encode())
        import hmac
        return hmac.compare_digest(expected, signature_bundle.get("signature", ""))
