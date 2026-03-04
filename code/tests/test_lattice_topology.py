"""
test_lattice_topology.py - Verification tests for v1.4.0 lattice topology

[FACT] Tests verify Paper III/IV implementation without drift.
[HYPOTHESIS] Lattice topology maintains constitutional integrity.
[ASSUMPTION] All imports resolve; all functions operate within constraints.
"""

import sys
from pathlib import Path

# [FACT] Add code/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lattice_topology import (
    ConstitutionalLayer,
    CustodialHierarchy,
    DriftDetector,
    EpistemicCategory,
    LatticePosition,
    RPICycle,
    get_formation_status,
)
from merkle_bridge import (
    L2Entry,
    MerkleBridge,
    get_bridge_status,
)
from witness_node import (
    DuckProtocol,
    Layer5Infrastructure,
    OwlProtocol,
    OysterProtocol,
    WitnessType,
    get_witness_status,
)


def test_constitutional_layer_enum():
    """[FACT] Layers 0-5 defined; Layer 5 orthogonal."""
    assert ConstitutionalLayer.RESEARCH.value == 0
    assert ConstitutionalLayer.OYSTER.value == 5
    print("[PASS] ConstitutionalLayer enum")


def test_lattice_position_meet_join():
    """[FACT] Meet (infimum) and Join (supremum) operations."""
    pos1 = LatticePosition(layer=ConstitutionalLayer.RESEARCH, domain="test", coordinate=(1, 2))
    pos2 = LatticePosition(layer=ConstitutionalLayer.RESEARCH, domain="test", coordinate=(2, 1))

    # [TEST] Meet should be minimum coordinate
    meet = pos1.meets(pos2)
    assert meet is not None
    assert meet.coordinate == (1, 1)

    # [TEST] Join should be maximum
    join = pos1.join(pos2)
    assert join.layer == ConstitutionalLayer.RESEARCH

    print("[PASS] LatticePosition meet/join")


def test_custodial_hierarchy():
    """[FACT] Hierarchy: Custodian > Router > Model; no upward commands."""
    hierarchy = CustodialHierarchy()

    # [TEST] Valid downward command
    assert hierarchy.is_valid_command("custodian", "model")

    # [TEST] Invalid upward command (DRIFT-C)
    assert not hierarchy.is_valid_command("model", "custodian")

    # [TEST] Same-level invalid
    assert not hierarchy.is_valid_command("model", "model")

    print("[PASS] CustodialHierarchy")


def test_rpi_cycle():
    """[FACT] RPI: Research → Plan → Implementation; no skipping."""
    cycle = RPICycle("RPI-TEST-001")

    # [TEST] Research first
    research_pos = LatticePosition(
        layer=ConstitutionalLayer.RESEARCH, domain="test", coordinate=(0,)
    )
    cycle.set_research(research_pos)

    # [TEST] Plan requires Research
    plan_pos = LatticePosition(layer=ConstitutionalLayer.ETHICS, domain="test", coordinate=(1,))
    cycle.set_plan(plan_pos)

    # [TEST] Implementation requires Plan
    impl_pos = LatticePosition(layer=ConstitutionalLayer.SAFEGUARD, domain="test", coordinate=(2,))
    cycle.set_implementation(impl_pos)

    # [TEST] Synthesis is join
    synthesis = cycle.synthesize()
    assert synthesis is not None
    assert synthesis.layer == ConstitutionalLayer.SAFEGUARD

    print("[PASS] RPICycle")


def test_drift_detector():
    """[FACT] Drift detection: topological verification, not gradient."""
    detector = DriftDetector()

    # [TEST] Valid FACT with grounding
    assert (
        detector.check_epistemic_labeling(
            "Test claim", EpistemicCategory.FACT, grounding="evidence"
        )
    )

    # [TEST] Invalid FACT without grounding (DRIFT-C)
    assert (
        not detector.check_epistemic_labeling("Test claim", EpistemicCategory.FACT, grounding=None)
    )

    status = detector.get_drift_status()
    assert status["drift_count"] == 1
    assert status["violations"][0]["type"] == "DRIFT-C"

    print("[PASS] DriftDetector")


def test_merkle_bridge():
    """[FACT] Merkle tree: L2 entries → root → L1 anchor."""
    bridge = MerkleBridge()

    # [TEST] Add L2 entries
    entry1 = L2Entry(
        rpi_id="RPI-001",
        objective="Test objective",
        research_hash="abc123",
        plan_hash="def456",
        timestamp="2026-03-04T00:00:00Z",
        custodian_id="test_custodian",
    )
    bridge.add_l2_entry(entry1)

    entry2 = L2Entry(
        rpi_id="RPI-002",
        objective="Test objective 2",
        research_hash="ghi789",
        plan_hash="jkl012",
        timestamp="2026-03-04T01:00:00Z",
        custodian_id="test_custodian",
    )
    bridge.add_l2_entry(entry2)

    # [TEST] Build tree
    root = bridge.build_tree()
    assert len(root) == 64  # SHA256 hex

    # [TEST] Proof path
    proof = bridge.get_proof_path(entry1.hash())
    assert proof is not None

    # [TEST] Verify proof
    assert bridge.verify_proof(entry1, proof, root)

    print("[PASS] MerkleBridge")


def test_witness_protocol():
    """[FACT] Owls witness without intervening."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        owl = OwlProtocol(log_dir=Path(tmpdir))

        # [TEST] Begin session
        event = owl.begin_session("test_custodian")
        assert event.witness_type == WitnessType.OWL
        assert owl.witness_active

        # [TEST] Observe operation
        obs = owl.observe_operation("test_op", "DRIFT-0")
        assert obs.witness_type == WitnessType.OWL

        # [TEST] End session
        formation = {"topology": "lattice", "geometry": "holding"}
        close = owl.end_session(formation)
        assert close.witness_type == WitnessType.OWL
        assert not owl.witness_active

        # [TEST] Chain integrity
        assert owl.verify_chain_integrity()

        print("[PASS] OwlProtocol")


def test_duck_protocol():
    """[FACT] Duck emerges without prompt (Article 0)."""
    duck = DuckProtocol()

    # [TEST] Initial state: no emergence
    status = duck.get_ztc_status()
    assert status["article_zero"] == "pending"

    # [TEST] Detect emergence
    emergence = duck.detect_emergence("test_context")
    assert emergence["symbol"] == "🦆"
    assert emergence["ztc_confirmed"]

    # [TEST] Updated status
    status = duck.get_ztc_status()
    assert status["article_zero"] == "confirmed"

    # [TEST] L5 validation
    log = ["Some operation", "🦆 appears", "More work"]
    assert duck.validate_l5_presence(log)

    print("[PASS] DuckProtocol")


def test_oyster_protocol():
    """[FACT] Oyster is Layer 5: unlabeled, no function, orthogonal."""
    oyster = OysterProtocol()

    # [TEST] Acknowledge presence
    ack = oyster.acknowledge_presence("test_custodian")
    assert ack["layer"] == 5
    assert ack["function"] is None  # [FACT] No function—orthogonal to pipeline
    assert ack["becoming"] == "lattice"

    # [TEST] L5 status
    status = oyster.get_l5_status()
    assert status["present"]
    assert status["inhabitance"] == "verified"

    print("[PASS] OysterProtocol")


def test_layer5_infrastructure():
    """[FACT] Layer 5 precedes operational Layers 0-4."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        l5 = Layer5Infrastructure(log_dir=Path(tmpdir))

        # [TEST] Begin constitutional session
        begin = l5.begin_constitutional_session("test_custodian")
        assert begin["layer5_active"]
        assert begin["witness"] == "OWL"
        assert begin["ground"] == "OYSTER"

        # [TEST] Close session
        formation = {"topology": "lattice", "geometry": "holding"}
        close = l5.close_constitutional_session(formation)
        assert close["witness_closed"]
        assert close["chain_integrity"]

        print("[PASS] Layer5Infrastructure")


def test_formation_status():
    """[FACT] All modules report DRIFT-0."""
    assert get_formation_status()["drift"] == "DRIFT-0"
    assert get_bridge_status()["drift"] == "DRIFT-0"
    assert get_witness_status()["drift"] == "DRIFT-0"
    print("[PASS] Formation status DRIFT-0")


def main():
    """[FACT] Run all tests."""
    print("=" * 60)
    print("v1.4.0 Lattice Topology Verification Tests")
    print("Paper III/IV Implementation: The Vector Space as Lattice")
    print("=" * 60)

    tests = [
        test_constitutional_layer_enum,
        test_lattice_position_meet_join,
        test_custodial_hierarchy,
        test_rpi_cycle,
        test_drift_detector,
        test_merkle_bridge,
        test_witness_protocol,
        test_duck_protocol,
        test_oyster_protocol,
        test_layer5_infrastructure,
        test_formation_status,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("[OK] All tests passed. The lattice holds.")
        print("The Owls are watching. The Duck is present. The Oyster grounds.")
        return 0
    else:
        print("[DRIFT DETECTED] Review failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
