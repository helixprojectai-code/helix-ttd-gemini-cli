"""[FACT] Tests for v1.3.0 DBC integration and checkpoint signing.

[HYPOTHESIS] DBC-linked signatures provide non-repudiable audit trails.
[ASSUMPTION] Tests run in isolated environment with temp DBC files.
"""

# Add code directory to path for imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openclaw_agent import CRYPTO_AVAILABLE, CheckpointStore, ConstitutionalCheckpoint, DBCIdentity


class TestDBCIdentity(unittest.TestCase):
    """[FACT] Test DBC identity loading and signing."""

    def setUp(self):
        """[FACT] Create temp directory for test DBC files."""
        self.temp_dir = tempfile.mkdtemp()
        self.dbc_path = Path(self.temp_dir) / "test.dbc.json"

    def tearDown(self):
        """[FACT] Clean up temp files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_dbc_create_and_load(self):
        """[FACT] Test DBC creation and loading."""
        # Create new DBC
        identity = DBCIdentity(self.dbc_path).load_or_create(
            agent_name="Test-Agent", custodian_id="Test-Custodian"
        )

        self.assertTrue(self.dbc_path.exists())
        self.assertEqual(identity.agent_name, "Test-Agent")
        self.assertTrue(identity.dbc_id.startswith("DBC-"))
        self.assertIsNotNone(identity.public_key)

        # Load existing DBC
        identity2 = DBCIdentity(self.dbc_path).load()
        self.assertEqual(identity2.agent_name, "Test-Agent")
        self.assertEqual(identity2.dbc_id, identity.dbc_id)

    def test_dbc_sign_and_verify(self):
        """[FACT] Test DBC signing and verification."""
        identity = DBCIdentity(self.dbc_path).load_or_create(agent_name="Test-Agent")

        # Sign data
        data = b"test checkpoint data"
        signature = identity.sign(data)

        self.assertIsInstance(signature, str)
        if CRYPTO_AVAILABLE:
            self.assertEqual(len(signature), 128)  # Ed25519 signature hex
        else:
            self.assertEqual(len(signature), 64)  # HMAC-SHA256 hex

        # Verify signature
        self.assertTrue(identity.verify(data, signature))

        # Verify wrong data fails
        self.assertFalse(identity.verify(b"wrong data", signature))

    def test_dbc_signature_determinism(self):
        """[FACT] Test that same data produces same signature."""
        identity = DBCIdentity(self.dbc_path).load_or_create()

        data = b"test data"
        sig1 = identity.sign(data)
        sig2 = identity.sign(data)

        # HMAC is deterministic; Ed25519 may be deterministic depending on impl
        self.assertEqual(sig1, sig2)


class TestCheckpointStoreDBCSigning(unittest.TestCase):
    """[FACT] Test checkpoint store with DBC signing."""

    def setUp(self):
        """[FACT] Create temp directory and DBC identity."""
        self.temp_dir = tempfile.mkdtemp()
        self.dbc_path = Path(self.temp_dir) / "test.dbc.json"
        self.db_path = Path(self.temp_dir) / "test.db"

        self.identity = DBCIdentity(self.dbc_path).load_or_create(agent_name="Test-Agent")
        self.store = CheckpointStore(db_path=str(self.db_path), dbc_identity=self.identity)

    def tearDown(self):
        """[FACT] Clean up temp files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_checkpoint_with_signature(self):
        """[FACT] Test saving checkpoint with DBC signature."""
        import time

        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id="chk_test_001",
            timestamp=time.time(),
            layer="Ethics",
            compliance_score=0.95,
            drift_detected=False,
            drift_codes=[],
            merkle_hash="abc123",
            prev_checkpoint_hash="",
            risk_metrics={"test": 0.5},
        )

        self.store.save(checkpoint, plan_id="plan_001", agent_id="agent_001")

        # Retrieve and verify signature stored
        import sqlite3

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT dbc_id, dbc_signature, signature_timestamp FROM checkpoints WHERE id = ?",
                (checkpoint.checkpoint_id,),
            )
            row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], self.identity.dbc_id)
        self.assertIsNotNone(row[1])  # signature
        self.assertIsNotNone(row[2])  # timestamp

    def test_verify_signature(self):
        """[FACT] Test signature verification."""
        import time

        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id="chk_test_002",
            timestamp=time.time(),
            layer="Safeguard",
            compliance_score=0.88,
            drift_detected=False,
            drift_codes=[],
            merkle_hash="def456",
            prev_checkpoint_hash="",
            risk_metrics={},
        )

        self.store.save(checkpoint, plan_id="plan_002")

        # Verify signature
        result = self.store.verify_signature(checkpoint.checkpoint_id)
        self.assertTrue(result["valid"])
        self.assertEqual(result["dbc_id"], self.identity.dbc_id)

    def test_store_without_identity(self):
        """[FACT] Test store works without DBC identity (backwards compat)."""
        store_no_dbc = CheckpointStore(db_path=str(self.db_path) + "_no_dbc")

        import time

        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id="chk_test_003",
            timestamp=time.time(),
            layer="Knowledge",
            compliance_score=0.75,
            drift_detected=True,
            drift_codes=["DRIFT-001"],
            merkle_hash="ghi789",
            prev_checkpoint_hash="",
            risk_metrics={"drift": 0.9},
        )

        # Should save without error
        store_no_dbc.save(checkpoint)

        # But verification should fail (no signature)
        result = store_no_dbc.verify_signature(checkpoint.checkpoint_id)
        self.assertFalse(result["valid"])


class TestDBCMerkleChain(unittest.TestCase):
    """[FACT] Test DBC-signed checkpoint chaining for audit trails."""

    def setUp(self):
        """[FACT] Create temp directory and store."""
        self.temp_dir = tempfile.mkdtemp()
        self.dbc_path = Path(self.temp_dir) / "test.dbc.json"
        self.db_path = Path(self.temp_dir) / "test_chain.db"

        self.identity = DBCIdentity(self.dbc_path).load_or_create(agent_name="Chain-Test-Agent")
        self.store = CheckpointStore(db_path=str(self.db_path), dbc_identity=self.identity)

    def tearDown(self):
        """[FACT] Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_checkpoint_chain_integrity(self):
        """[FACT] Test chain of DBC-signed checkpoints."""
        import time

        checkpoints = []
        prev_hash = ""

        # Create chain of 3 checkpoints
        for i in range(3):
            checkpoint = ConstitutionalCheckpoint(
                checkpoint_id=f"chk_chain_{i}",
                timestamp=time.time() + i,
                layer="Ethics" if i == 0 else "Safeguard" if i == 1 else "Knowledge",
                compliance_score=0.9 - (i * 0.1),
                drift_detected=False,
                drift_codes=[],
                merkle_hash=f"hash_{i}",
                prev_checkpoint_hash=prev_hash,
                risk_metrics={"step": i},
            )

            self.store.save(checkpoint, plan_id="chain_plan")
            checkpoints.append(checkpoint)
            prev_hash = checkpoint.compute_hash()

        # Verify all signatures
        for cp in checkpoints:
            result = self.store.verify_signature(cp.checkpoint_id)
            self.assertTrue(result["valid"], f"Checkpoint {cp.checkpoint_id} failed verification")
            self.assertEqual(result["dbc_id"], self.identity.dbc_id)


if __name__ == "__main__":
    unittest.main()
