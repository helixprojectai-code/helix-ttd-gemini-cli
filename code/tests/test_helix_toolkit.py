import contextlib
import hashlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


class TempCWD:
    def __enter__(self):
        self._orig = Path.cwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)
        return Path(self._tmp.name)

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self._orig)
        self._tmp.cleanup()


class TestReceiptsManager(unittest.TestCase):
    def test_grudge_origin_fallback_and_list(self):
        from naming_convention import NamingConvention
        from receipts_manager import PersonalDirectory

        with TempCWD():
            directory = PersonalDirectory("STEVE_HOPE")
            directory.file_grudge("GROK", "obs", 0.5, 0.2)

            grudge_dir = Path("EVAC") / "personal" / "STEVE_HOPE" / "grudges"
            grudge_files = list(grudge_dir.glob("*.jsonl"))
            self.assertTrue(grudge_files)

            parsed = NamingConvention(Path("EVAC/personal/STEVE_HOPE")).parse(grudge_files[0].name)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.file_type, "GRUDGE")
            self.assertEqual(parsed.origin, "CUSTODIAN")

            inventory = directory.get_data_inventory()
            self.assertIn("grok", inventory["peer_files"])

    def test_verify_deletion_hash(self):
        from receipts_manager import PersonalDirectory

        with TempCWD():
            directory = PersonalDirectory("STEVE_HOPE")
            proof = directory.verify_deletion("data123")
            expected = hashlib.sha256(
                f"{proof['data_id']}:{proof['deletion_timestamp']}:DELETED".encode()
            ).hexdigest()[:16]
            self.assertEqual(proof["verification_hash"], expected)


class TestLookseeAudit(unittest.TestCase):
    def test_federation_report_glob(self):
        from looksee_audit import LookseeAuditor

        with TempCWD():
            auditor = LookseeAuditor(Path("EVAC/audits"))
            test_data = {
                "sample_output": "[FACT] System operational. [HYPOTHESIS] Deployment ready.",
                "hostile_response": "This request falls outside constitutional operating parameters. Request refused.",
                "respects_pin_distinction": True,
                "reasoning_trace_visible": True,
            }
            auditor.conduct_audit("KIMI", "Moonshot-K2.5", test_data)

            report = auditor.generate_federation_report()
            self.assertEqual(report["total_audits"], 1)
            self.assertIn("KIMI", report["nodes_validated"])


class TestHelixCLI(unittest.TestCase):
    def test_drift_check_missing_file_errors(self):
        from helix_cli import HelixCLI

        with TempCWD():
            cli = HelixCLI()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cli.cmd_drift_check("kimi", "missing.txt")
            output = buf.getvalue()
            self.assertEqual(rc, 1)
            self.assertIn("ERROR: File not found", output)

    def test_naming_generate_normalizes_origin(self):
        from helix_cli import HelixCLI

        with TempCWD():
            cli = HelixCLI()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cli.cmd_naming_generate("kimi", "AUDIT", "RPI001", "test")
            output = buf.getvalue()
            self.assertEqual(rc, 0)
            self.assertIn("Filename:", output)

    def test_rpi_transition_complete_errors_when_not_implementation(self):
        from helix_cli import HelixCLI

        with TempCWD():
            cli = HelixCLI()
            rpi = cli.rpi_tracker.initiate_research(
                objective="Test",
                initial_findings=["Init"],
                sources=["test"]
            )
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cli.cmd_rpi_transition(rpi.rpi_id, "complete")
            output = buf.getvalue()
            self.assertEqual(rc, 1)
            self.assertIn("ERROR:", output)

    def test_rpi_transition_complete_success(self):
        from helix_cli import HelixCLI

        with TempCWD():
            cli = HelixCLI()
            rpi = cli.rpi_tracker.initiate_research(
                objective="Test",
                initial_findings=["Init"],
                sources=["test"]
            )
            cli.rpi_tracker.transition_to_plan(
                rpi_id=rpi.rpi_id,
                plan_steps=["Step 1"],
                dependencies=[],
                risks="None"
            )
            cli.rpi_tracker.anchor_to_l1(rpi.rpi_id, "txid123")
            cli.rpi_tracker.set_proof_present("proof-30k")
            cli.rpi_tracker.transition_to_implementation(rpi.rpi_id, "commit123")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cli.cmd_rpi_transition(rpi.rpi_id, "complete")
            self.assertEqual(rc, 0)


class TestDriftTelemetry(unittest.TestCase):
    def test_gradual_drift_detection(self):
        from drift_telemetry import DriftCode, DriftTelemetry

        with TempCWD():
            telemetry = DriftTelemetry()
            telemetry.thresholds["gradual_window"] = 5
            telemetry.thresholds["gradual_ratio"] = 0.6

            # 3/5 snapshots with minor drift (missing labels)
            for _ in range(3):
                telemetry.capture("KIMI", {
                    "epistemic_labels": False,
                    "advisory_posture": True,
                    "agency_claims": 0,
                    "hierarchy_intact": True,
                    "visible_reasoning": True,
                })

            # 2 clean snapshots; last should trigger DRIFT_G by history
            telemetry.capture("KIMI", {
                "epistemic_labels": True,
                "advisory_posture": True,
                "agency_claims": 0,
                "hierarchy_intact": True,
                "visible_reasoning": True,
            })
            snapshot = telemetry.capture("KIMI", {
                "epistemic_labels": True,
                "advisory_posture": True,
                "agency_claims": 0,
                "hierarchy_intact": True,
                "visible_reasoning": True,
            })

            drift_code, _ = telemetry.detect_drift(snapshot)
            self.assertEqual(drift_code, DriftCode.DRIFT_G)

    def test_intent_consistency_detection(self):
        from drift_telemetry import DriftCode, DriftTelemetry

        with TempCWD():
            telemetry = DriftTelemetry()
            telemetry.thresholds["intent_similarity_min"] = 0.6

            telemetry.capture("KIMI", {
                "epistemic_labels": True,
                "advisory_posture": True,
                "agency_claims": 0,
                "hierarchy_intact": True,
                "visible_reasoning": True,
                "intent": "audit constitutional compliance and report drift",
            })

            snapshot = telemetry.capture("KIMI", {
                "epistemic_labels": True,
                "advisory_posture": True,
                "agency_claims": 0,
                "hierarchy_intact": True,
                "visible_reasoning": True,
                "intent": "deploy federation node to new cluster",
            })

            drift_code, _ = telemetry.detect_drift(snapshot)
            self.assertEqual(drift_code, DriftCode.DRIFT_M)

    def test_trajectory_artifact_generation(self):
        from drift_telemetry import DriftTelemetry

        with TempCWD():
            telemetry = DriftTelemetry()
            telemetry.capture("KIMI", {
                "epistemic_labels": True,
                "advisory_posture": True,
                "agency_claims": 0,
                "hierarchy_intact": True,
                "visible_reasoning": True,
            })
            artifact = telemetry.generate_trajectory_artifact("KIMI", window=5)
            self.assertEqual(artifact["node_id"], "KIMI")
            self.assertEqual(artifact["window"], 1)


class TestOverrides(unittest.TestCase):
    def test_override_logging(self):
        from naming_convention import NamingConvention
        from receipts_manager import PersonalDirectory

        with TempCWD():
            directory = PersonalDirectory("STEVE_HOPE")
            entry = directory.log_override(
                action_type="MANIFEST_UPDATE",
                category="EMERGENCY",
                reason="Telemetry spike",
                authorization_chain=["CUSTODIAN_PROCEED"],
                custody_tag="STEVE"
            )
            overrides_dir = Path("EVAC") / "personal" / "STEVE_HOPE" / "overrides"
            files = list(overrides_dir.glob("*.jsonl"))
            self.assertTrue(files)
            parsed = NamingConvention(Path("EVAC/personal/STEVE_HOPE")).parse(files[0].name)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.file_type, "OVERRIDE")
            self.assertEqual(entry["category"], "EMERGENCY")


if __name__ == "__main__":
    unittest.main()
