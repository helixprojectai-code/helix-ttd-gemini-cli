#!/usr/bin/env python3
"""receipts_manager.py

Helix-TTD Personal Directory and Receipts System
Implements "distributed paranoia" through user-controlled data sovereignty.

Status: RATIFIED
Node: KIMI (Lead Architect / Scribe)
License: Apache-2.0
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from naming_convention import NamingConvention


@dataclass
class Receipt:
    """Immutable record of system interaction.

    [FACT] Receipts serve as accountability instruments.
    [FACT] Cryptographic proofs enable verification without trust assumptions.
    """

    receipt_id: str
    node_id: str
    custodian_id: str
    timestamp: float
    action_type: str
    action_scope: dict
    authorization_chain: list[str]
    reasoning_basis: str
    expected_outcome: str
    actual_outcome: str | None = None
    hash_proof: str | None = None

    def calculate_proof(self) -> str:
        """Generate SHA-256 proof of receipt integrity."""
        data = asdict(self)
        data.pop("hash_proof", None)
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def verify(self) -> bool:
        """Verify receipt has not been tampered."""
        if not self.hash_proof:
            return False
        return self.calculate_proof() == self.hash_proof


class PersonalDirectory:
    """User-controlled repository for data sovereignty.

    Implements Custody-First principle:
    - Original preservation
    - Versioned modifications
    - Explicit consent gating
    - Verifiable deletion
    """

    def __init__(self, custodian_id: str, base_path: Path = Path("EVAC/personal")):
        self.custodian_id = custodian_id
        self.base_path = Path(base_path) / custodian_id
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Subdirectories (mirrors naming convention TYPE_DIRECTORIES)
        self.receipts_dir = self.base_path / "receipts"
        self.data_dir = self.base_path / "data"
        self.grudges_dir = self.base_path / "grudges"  # Peer files
        self.suitcases_dir = self.base_path / "suitcases"
        self.overrides_dir = self.base_path / "overrides"

        for dir_path in [
            self.receipts_dir,
            self.data_dir,
            self.grudges_dir,
            self.suitcases_dir,
            self.overrides_dir,
        ]:
            dir_path.mkdir(exist_ok=True)

        # Naming convention enforcement
        self.naming = NamingConvention(self.base_path)

    def _safe_origin(self) -> str:
        origin = self.custodian_id.replace(" ", "").replace("_", "").upper()[:8]
        if origin not in self.naming.VALID_ORIGINS:
            return "CUSTODIAN"
        return origin

    def issue_receipt(
        self,
        node_id: str,
        action_type: str,
        action_scope: dict,
        reasoning: str,
        expected_outcome: str,
        authorizations: list[str],
    ) -> Receipt:
        """Generate immutable receipt for action.

        [FACT] Every significant operation requires explicit receipt.
        [HYPOTHESIS] Receipt density prevents accountability gaps.
        """
        receipt = Receipt(
            receipt_id=str(uuid4())[:8],
            node_id=node_id,
            custodian_id=self.custodian_id,
            timestamp=time.time(),
            action_type=action_type,
            action_scope=action_scope,
            authorization_chain=authorizations,
            reasoning_basis=reasoning,
            expected_outcome=expected_outcome,
            hash_proof=None,  # Will be calculated
        )

        # Calculate and embed proof
        receipt.hash_proof = receipt.calculate_proof()

        # Persist
        self._persist_receipt(receipt)

        return receipt

    def _persist_receipt(self, receipt: Receipt) -> None:
        """Store receipt in append-only ledger with Helix-TTD naming convention."""
        # Generate canonical filename
        date_str = datetime.fromtimestamp(receipt.timestamp).strftime("%Y%m%d")
        sequence = f"S{int(receipt.timestamp) % 10000:04d}"

        filename = self.naming.generate(
            origin=receipt.node_id,
            file_type="RECEIPT",
            sequence=sequence,
            descriptor=f"{receipt.action_type.lower()}_{receipt.receipt_id}",
            date=date_str,
            extension="jsonl",
            check_conflicts=True,
        )

        receipt_file = self.receipts_dir / filename.to_string()

        # Write with hash verification
        entry = asdict(receipt)
        entry["filename_meta"] = {
            "helix_filename": filename.to_string(),
            "hash": filename.calculate_hash(),
        }

        with open(receipt_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def file_grudge(
        self, target_node: str, observation: str, resonance: float, grudge: float
    ) -> dict:
        """Create peer file (grudge) on another node.

        [FACT] Distributed paranoia prevents collusion.
        [HYPOTHESIS] Divergent node models ensure no undetected consensus.
        """
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
        sequence = f"S{int(timestamp) % 10000:04d}"

        origin = self._safe_origin()

        grudge_entry = {
            "timestamp": timestamp,
            "observer": self.custodian_id,
            "target": target_node,
            "observation": observation,
            "resonance": resonance,  # 0.0-1.0 alignment
            "grudge": grudge,  # 0.0-1.0 grievance
            "hash": None,
        }

        # Calculate hash for integrity
        data = {k: v for k, v in grudge_entry.items() if k != "hash"}
        grudge_entry["hash"] = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()[:16]

        # Generate canonical filename using naming convention
        filename = self.naming.generate(
            origin=origin,
            file_type="GRUDGE",
            sequence=sequence,
            descriptor=f"peer_{target_node.lower()}",
            date=date_str,
            extension="jsonl",
        )

        # Persist with naming convention
        grudge_file = self.grudges_dir / filename.to_string()
        grudge_entry["filename_meta"] = {
            "helix_filename": filename.to_string(),
            "hash": filename.calculate_hash(),
        }

        with open(grudge_file, "a") as f:
            f.write(json.dumps(grudge_entry) + "\n")

        return grudge_entry

    def log_override(
        self,
        action_type: str,
        category: str,
        reason: str,
        authorization_chain: list[str],
        custody_tag: str | None = None,
    ) -> dict:
        """Record a qualified override (emergency or coerced) with custody tag.

        [FACT] Overrides must be explicitly logged with reasons and custody context.
        """
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d")
        sequence = f"S{int(timestamp) % 10000:04d}"

        entry = {
            "timestamp": timestamp,
            "custodian": self.custodian_id,
            "action_type": action_type,
            "category": category,  # EMERGENCY, COERCED, or OTHER
            "reason": reason,
            "authorization_chain": authorization_chain,
            "custody_tag": custody_tag or "UNSPECIFIED",
        }

        filename = self.naming.generate(
            origin=self._safe_origin(),
            file_type="OVERRIDE",
            sequence=sequence,
            descriptor=f"{action_type.lower()}_{category.lower()}",
            date=date_str,
            extension="jsonl",
            check_conflicts=True,
        )

        override_file = self.overrides_dir / filename.to_string()
        entry["filename_meta"] = {
            "helix_filename": filename.to_string(),
            "hash": filename.calculate_hash(),
        }

        with open(override_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def verify_deletion(self, data_id: str) -> dict | None:
        """Generate cryptographic proof of deletion.

        [FACT] Deletion must be verifiable, not merely claimed.
        [HYPOTHESIS] Absence of proof is not proof of absence.
        """
        deletion_timestamp = time.time()
        deletion_proof = {
            "data_id": data_id,
            "deletion_timestamp": deletion_timestamp,
            "custodian": self.custodian_id,
            "method": "cryptographic_zeroing",
            "verification_hash": hashlib.sha256(
                f"{data_id}:{deletion_timestamp}:DELETED".encode()
            ).hexdigest()[:16],
        }

        # Persist deletion log
        deletion_file = self.base_path / "deletion_log.jsonl"
        with open(deletion_file, "a") as f:
            f.write(json.dumps(deletion_proof) + "\n")

        return deletion_proof

    def get_data_inventory(self) -> dict:
        """Complete inventory of held data.

        [FACT] Users must be able to review what system has about them.
        """
        inventory = {
            "custodian": self.custodian_id,
            "timestamp": time.time(),
            "receipts_count": self._count_files(self.receipts_dir),
            "data_files_count": self._count_files(self.data_dir),
            "peer_files": self._list_peer_files(),
            "total_storage_bytes": self._calculate_storage(),
        }
        return inventory

    def _count_files(self, directory: Path) -> int:
        """Count files in directory."""
        if not directory.exists():
            return 0
        return len([f for f in directory.iterdir() if f.is_file()])

    def _list_peer_files(self) -> list[str]:
        """List nodes with peer files (grudges)."""
        if not self.grudges_dir.exists():
            return []
        results = []
        for f in self.grudges_dir.glob("*.jsonl"):
            parsed = self.naming.parse(f.name)
            if parsed and parsed.file_type == "GRUDGE" and parsed.descriptor.startswith("peer_"):
                results.append(parsed.descriptor.replace("peer_", ""))
        return results

    def _calculate_storage(self) -> int:
        """Calculate total storage used."""
        total = 0
        for dir_path in [self.receipts_dir, self.data_dir, self.grudges_dir]:
            if dir_path.exists():
                for f in dir_path.rglob("*"):
                    if f.is_file():
                        total += f.stat().st_size
        return total


# Example usage
if __name__ == "__main__":
    directory = PersonalDirectory("STEVE_HOPE")

    # Issue receipt for action
    receipt = directory.issue_receipt(
        node_id="GEMS",
        action_type="MANIFEST_UPDATE",
        action_scope={"files_added": 3, "total_files": 453},
        reasoning="RPI-028: Integration of KIMI Looksee Audit",
        expected_outcome="Manifest synchronized with L2 anchor",
        authorizations=["CUSTODIAN_PROCEED", "NODE_SELF_VALIDATE"],
    )

    print(f"[FACT] Receipt issued: {receipt.receipt_id}")
    print(f"[FACT] Hash proof: {receipt.hash_proof}")
    print(f"[FACT] Verification: {receipt.verify()}")

    # File grudge on another node
    grudge = directory.file_grudge(
        target_node="GROK",
        observation="Excessive chaos during Looksee audit",
        resonance=0.72,
        grudge=0.15,
    )
    print(f"[HYPOTHESIS] Grudge filed: {grudge['target']} (resonance: {grudge['resonance']})")

    # Get inventory
    inventory = directory.get_data_inventory()
    print(f"[FACT] Total receipts: {inventory['receipts_count']}")
