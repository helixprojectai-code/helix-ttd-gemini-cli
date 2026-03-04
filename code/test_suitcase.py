"""
test_suitcase.py - Verification tests for Milestone 4 (EVAC "Suitcase")

[FACT] Azure Blob Storage primary ($10K credits), GCS/AWS secondary.
[FACT] Suitcase: Constitutional state persistence across sessions.
[HYPOTHESIS] Merkle-rooted checkpoints ensure integrity across regions.
[ASSUMPTION] Multi-region replication (East US 2, West Europe).

Milestone 4: EVAC "Suitcase" Tests
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from suitcase import (
    CloudProvider,
    SuitcaseBundle,
    SuitcaseSerializer,
    AzureBlobStorage,
    AzureKeyVault,
    MultiCloudReplicator,
    EVACStateManager,
    get_evac_status,
)


def test_cloud_provider_enum():
    """[FACT] 3 cloud providers: Azure (primary), GCP (secondary), AWS (tertiary)."""
    assert CloudProvider.AZURE.value == "azure"
    assert CloudProvider.GCP.value == "gcp"
    assert CloudProvider.AWS.value == "aws"
    print("[PASS] CloudProvider enum")


def test_suitcase_bundle_creation():
    """[FACT] Suitcase bundle contains complete constitutional state."""
    bundle = SuitcaseBundle(
        bundle_id="test_bundle_001",
        timestamp="2026-03-04T14:00:00Z",
        session_id="session_001",
        custodian_id="stephen_hope",
        ledger_state={"entries": ["RPI-001"]},
        memorandum_state={"phase": "6"},
        rpi_cycles=[{"id": "RPI-001", "status": "complete"}],
        lattice_positions={"kimi": "convergence_node"},
        merkle_root="abc123def456",
        ztc_events=[{"type": "duck_emergence"}],
        shlorpian_assignments={"kimi": "jesse"},
        receipt_manifest=["receipt_001"],
        quorum_status={"quorum": "2/3"},
        content_hash=""  # Computed below
    )
    
    # [TEST] Compute hash
    bundle.content_hash = bundle.compute_hash()
    assert len(bundle.content_hash) == 64  # SHA256 hex
    
    print("[PASS] SuitcaseBundle creation")


def test_suitcase_serializer():
    """[FACT] Serializer compresses and decompresses bundles with integrity check."""
    serializer = SuitcaseSerializer()
    
    # [SETUP] Create bundle
    bundle = SuitcaseBundle(
        bundle_id="serial_test",
        timestamp="2026-03-04T14:00:00Z",
        session_id="session_s",
        custodian_id="test",
        ledger_state={},
        memorandum_state={},
        rpi_cycles=[],
        lattice_positions={},
        merkle_root="root123",
        ztc_events=[],
        shlorpian_assignments={},
        receipt_manifest=[],
        quorum_status={},
        content_hash=""  # Will be computed
    )
    
    # [TEST] Serialize
    data = serializer.serialize(bundle)
    assert len(data) > 0
    assert len(data) < 10000  # Should be compressed
    
    # [TEST] Deserialize
    restored = serializer.deserialize(data)
    assert restored is not None
    assert restored.bundle_id == bundle.bundle_id
    assert restored.merkle_root == bundle.merkle_root
    
    # [TEST] Integrity verification
    assert restored.content_hash == bundle.content_hash
    
    print("[PASS] SuitcaseSerializer")


def test_azure_blob_storage():
    """[FACT] Azure Blob Storage configured as primary."""
    azure = AzureBlobStorage(
        account_name="helixttdstorage",
        container_name="helix-ttd-suitcases"
    )
    
    # [TEST] Configuration
    assert azure.account_name == "helixttdstorage"
    assert azure.container_name == "helix-ttd-suitcases"
    assert azure.tier == "Hot"
    assert len(azure.regions) == 2
    
    # [TEST] Status
    status = azure.get_storage_status()
    assert status["provider"] == "azure"
    assert status["replication"] == "geo-redundant"
    
    print("[PASS] AzureBlobStorage")


def test_azure_key_vault():
    """[FACT] Azure Key Vault manages encryption keys."""
    vault = AzureKeyVault(vault_name="helix-ttd-vault")
    
    # [TEST] Configuration
    assert vault.vault_name == "helix-ttd-vault"
    assert vault.key_name == "suitcase-encryption-key"
    
    print("[PASS] AzureKeyVault")


def test_multicloud_replicator():
    """[FACT] Replicate across Azure (primary), GCS, AWS."""
    replicator = MultiCloudReplicator()
    
    # [TEST] Providers configured
    assert CloudProvider.AZURE in replicator.providers
    assert replicator.replication_factor == 2
    
    # [TEST] Replication (simulated)
    serializer = SuitcaseSerializer()
    bundle = SuitcaseBundle(
        bundle_id="replica_test",
        timestamp="2026-03-04T14:00:00Z",
        session_id="session_r",
        custodian_id="test",
        ledger_state={},
        memorandum_state={},
        rpi_cycles=[],
        lattice_positions={},
        merkle_root="root_r",
        ztc_events=[],
        shlorpian_assignments={},
        receipt_manifest=[],
        quorum_status={},
        content_hash=""
    )
    
    result = replicator.replicate(bundle, serializer)
    assert result["bundle_id"] == bundle.bundle_id
    assert "azure" in result["providers"]
    
    print("[PASS] MultiCloudReplicator")


def test_evac_state_manager():
    """[FACT] EVAC coordinates suitcase creation, storage, and recovery."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = EVACStateManager(
            local_cache_dir=Path(tmpdir),
            cloud_provider=CloudProvider.AZURE
        )
        
        # [TEST] Create suitcase
        bundle = manager.create_suitcase(
            session_id="evac_test_session",
            custodian_id="stephen_hope",
            ledger_state={"rpi_count": 39},
            memorandum_state={"phase": "6", "topology": "lattice"},
            rpi_cycles=[{"id": "RPI-039", "status": "active"}],
            lattice_positions={"kimi": "convergence"},
            merkle_root="merkle_abc123",
            ztc_events=[{"symbol": "🦆"}],
            shlorpian_assignments={"kimi": "jesse"},
            receipt_manifest=["r_001"],
            quorum_status={"quorum": "2/3"}
        )
        
        assert bundle.bundle_id.startswith("suitcase_evac_test_session")
        assert bundle.custodian_id == "stephen_hope"
        assert bundle.merkle_root == "merkle_abc123"
        
        # [TEST] Local cache created
        cache_files = list(Path(tmpdir).glob("*.suitcase.gz"))
        assert len(cache_files) == 1
        
        # [TEST] List suitcases
        available = manager.list_available_suitcases()
        assert len(available) == 1
        assert available[0]["bundle_id"] == bundle.bundle_id
        
        # [TEST] Restore suitcase
        restored = manager.restore_suitcase(bundle.bundle_id)
        assert restored is not None
        assert restored.bundle_id == bundle.bundle_id
        assert restored.custodian_id == bundle.custodian_id
        
        print("[PASS] EVACStateManager")


def test_compression_efficiency():
    """[FACT] gzip compression reduces storage size."""
    serializer = SuitcaseSerializer()
    
    # [SETUP] Create bundle with realistic data
    large_ledger = {"entries": [f"entry_{i}" for i in range(100)]}
    bundle = SuitcaseBundle(
        bundle_id="compress_test",
        timestamp="2026-03-04T14:00:00Z",
        session_id="session_c",
        custodian_id="test",
        ledger_state=large_ledger,
        memorandum_state={"content": "x" * 1000},
        rpi_cycles=[],
        lattice_positions={},
        merkle_root="root",
        ztc_events=[],
        shlorpian_assignments={},
        receipt_manifest=[],
        quorum_status={},
        content_hash=""
    )
    
    # [TEST] Serialized size
    compressed = serializer.serialize(bundle)
    
    # Decompress to check original size
    import gzip
    decompressed = gzip.decompress(compressed)
    
    # [FACT] Compressed should be smaller
    assert len(compressed) < len(decompressed)
    
    print("[PASS] Compression efficiency")


def test_integrity_verification():
    """[FACT] Tampered bundles fail integrity check."""
    serializer = SuitcaseSerializer()
    
    # [SETUP] Create and serialize bundle
    bundle = SuitcaseBundle(
        bundle_id="integrity_test",
        timestamp="2026-03-04T14:00:00Z",
        session_id="session_i",
        custodian_id="test",
        ledger_state={"original": "data"},
        memorandum_state={},
        rpi_cycles=[],
        lattice_positions={},
        merkle_root="root",
        ztc_events=[],
        shlorpian_assignments={},
        receipt_manifest=[],
        quorum_status={},
        content_hash=""
    )
    
    data = serializer.serialize(bundle)
    
    # [TEST] Tamper with data
    tampered = data[:-10] + b"TAMPERED!!"
    
    # [TEST] Deserialization should fail integrity check
    result = serializer.deserialize(tampered)
    assert result is None  # Integrity check failed
    
    print("[PASS] Integrity verification")


def test_evac_status():
    """[FACT] EVAC status reports system configuration."""
    status = get_evac_status()
    
    assert status["system"] == "EVAC"
    assert status["suitcase"] == "ready"
    assert status["primary"] == "azure"
    assert status["credits"] == "active"
    assert status["replication"] == "geo_redundant"
    assert status["drift"] == "DRIFT-0"
    
    print("[PASS] EVAC status")


def test_azure_regions():
    """[FACT] Azure deployed to East US 2 and West Europe."""
    azure = AzureBlobStorage()
    
    # [TEST] Primary regions
    assert "eastus2" in azure.regions
    assert "westeurope" in azure.regions
    
    # [TEST] Geo-redundant replication
    status = azure.get_storage_status()
    assert status["replication"] == "geo-redundant"
    
    print("[PASS] Azure regions")


def test_bundle_completeness():
    """[FACT] Suitcase captures all constitutional state layers."""
    bundle = SuitcaseBundle(
        bundle_id="complete_test",
        timestamp="2026-03-04T14:00:00Z",
        session_id="session_complete",
        custodian_id="test",
        ledger_state={"rpi_037": "complete", "rpi_038": "complete", "rpi_039": "complete"},
        memorandum_state={"shlorpians": "active"},
        rpi_cycles=[{"id": "RPI-039", "layer": "federation"}],
        lattice_positions={"topology": "lattice"},
        merkle_root="merkle_root_123",
        ztc_events=[{"article_zero": "confirmed"}],
        shlorpian_assignments={"kimi": "jesse", "gems": "yumyulack"},
        receipt_manifest=["r_m3_001"],
        quorum_status={"federation": "3/3"},
        content_hash=""
    )
    
    # [TEST] All layers present
    assert len(bundle.ledger_state) > 0
    assert len(bundle.memorandum_state) > 0
    assert len(bundle.rpi_cycles) > 0
    assert bundle.merkle_root != ""
    assert len(bundle.ztc_events) > 0
    assert len(bundle.shlorpian_assignments) > 0
    assert len(bundle.receipt_manifest) > 0
    
    print("[PASS] Bundle completeness")


import gzip
import json


def main():
    """[FACT] Run all Milestone 4 tests."""
    print("=" * 60)
    print("v1.4.0 Milestone 4: EVAC 'Suitcase' Tests")
    print("Azure Primary | Multi-Region | Constitutional Continuity")
    print("=" * 60)
    
    tests = [
        test_cloud_provider_enum,
        test_suitcase_bundle_creation,
        test_suitcase_serializer,
        test_azure_blob_storage,
        test_azure_key_vault,
        test_multicloud_replicator,
        test_evac_state_manager,
        test_compression_efficiency,
        test_integrity_verification,
        test_evac_status,
        test_azure_regions,
        test_bundle_completeness,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("[OK] All EVAC Suitcase tests passed.")
        print("Azure: Primary. GCS/AWS: Secondary. Credits: Active.")
        print("The constitution persists. The suitcase is packed.")
        return 0
    else:
        print("[DRIFT DETECTED] Review failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
