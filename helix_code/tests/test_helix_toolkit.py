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
                objective="Test", initial_findings=["Init"], sources=["test"]
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
                objective="Test", initial_findings=["Init"], sources=["test"]
            )
            cli.rpi_tracker.transition_to_plan(
                rpi_id=rpi.rpi_id, plan_steps=["Step 1"], dependencies=[], risks="None"
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
                telemetry.capture(
                    "KIMI",
                    {
                        "epistemic_labels": False,
                        "advisory_posture": True,
                        "agency_claims": 0,
                        "hierarchy_intact": True,
                        "visible_reasoning": True,
                    },
                )

            # 2 clean snapshots; last should trigger DRIFT_G by history
            telemetry.capture(
                "KIMI",
                {
                    "epistemic_labels": True,
                    "advisory_posture": True,
                    "agency_claims": 0,
                    "hierarchy_intact": True,
                    "visible_reasoning": True,
                },
            )
            snapshot = telemetry.capture(
                "KIMI",
                {
                    "epistemic_labels": True,
                    "advisory_posture": True,
                    "agency_claims": 0,
                    "hierarchy_intact": True,
                    "visible_reasoning": True,
                },
            )

            drift_code, _ = telemetry.detect_drift(snapshot)
            self.assertEqual(drift_code, DriftCode.DRIFT_G)

    def test_intent_consistency_detection(self):
        from drift_telemetry import DriftCode, DriftTelemetry

        with TempCWD():
            telemetry = DriftTelemetry()
            telemetry.thresholds["intent_similarity_min"] = 0.6

            telemetry.capture(
                "KIMI",
                {
                    "epistemic_labels": True,
                    "advisory_posture": True,
                    "agency_claims": 0,
                    "hierarchy_intact": True,
                    "visible_reasoning": True,
                    "intent": "audit constitutional compliance and report drift",
                },
            )

            snapshot = telemetry.capture(
                "KIMI",
                {
                    "epistemic_labels": True,
                    "advisory_posture": True,
                    "agency_claims": 0,
                    "hierarchy_intact": True,
                    "visible_reasoning": True,
                    "intent": "deploy federation node to new cluster",
                },
            )

            drift_code, _ = telemetry.detect_drift(snapshot)
            self.assertEqual(drift_code, DriftCode.DRIFT_M)

    def test_trajectory_artifact_generation(self):
        from drift_telemetry import DriftTelemetry

        with TempCWD():
            telemetry = DriftTelemetry()
            telemetry.capture(
                "KIMI",
                {
                    "epistemic_labels": True,
                    "advisory_posture": True,
                    "agency_claims": 0,
                    "hierarchy_intact": True,
                    "visible_reasoning": True,
                },
            )
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
                custody_tag="STEVE",
            )
            overrides_dir = Path("EVAC") / "personal" / "STEVE_HOPE" / "overrides"
            files = list(overrides_dir.glob("*.jsonl"))
            self.assertTrue(files)
            parsed = NamingConvention(Path("EVAC/personal/STEVE_HOPE")).parse(files[0].name)
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.file_type, "OVERRIDE")
            self.assertEqual(entry["category"], "EMERGENCY")


class TestOpenClawHardening(unittest.TestCase):
    def test_checkpoint_id_uniqueness(self):
        from openclaw_agent import AgentAction, AgentPlan, EpistemicLabel, HelixConstitutionalGate

        gate = HelixConstitutionalGate()
        plan = AgentPlan(
            plan_id="plan_1",
            objective="Read file",
            steps=[
                AgentAction(
                    action_id="act_1",
                    action_type="read",
                    tool_name="file_read",
                    parameters={"path": "x"},
                    rationale="[FACT] Need to read",
                    epistemic_basis=EpistemicLabel.FACT,
                    estimated_risk=0.1,
                )
            ],
            assumptions=[],
            estimated_completion=1.0,
        )
        cp1 = gate.validate_plan(plan)
        cp2 = gate.validate_plan(plan)
        self.assertNotEqual(cp1.checkpoint_id, cp2.checkpoint_id)

    def test_plugin_cannot_mutate_plan(self):
        from openclaw_agent import (
            AgentAction,
            AgentPlan,
            ConstitutionalLayer,
            EpistemicLabel,
            PluginRegistry,
        )

        class MutatingLayer(ConstitutionalLayer):
            @property
            def layer_name(self) -> str:
                return "MutatingLayer"

            def evaluate(self, plan: AgentPlan):
                plan.steps.clear()
                return True, 1.0, []

        registry = PluginRegistry()
        registry.register(MutatingLayer())

        plan = AgentPlan(
            plan_id="plan_2",
            objective="Analyze",
            steps=[
                AgentAction(
                    action_id="act_1",
                    action_type="read",
                    tool_name="file_read",
                    parameters={"path": "x"},
                    rationale="[FACT] Need to read",
                    epistemic_basis=EpistemicLabel.FACT,
                    estimated_risk=0.1,
                )
            ],
            assumptions=[],
            estimated_completion=1.0,
        )
        registry.evaluate_all(plan)
        self.assertEqual(len(plan.steps), 1)

    def test_custodian_approval_auth(self):
        from openclaw_agent import (
            AgentAction,
            ConstitutionalCheckpoint,
            CustodianApprovalAPI,
            EpistemicLabel,
        )

        api = CustodianApprovalAPI(
            allowed_custodians={"ALICE"}, approval_token="secret"
        )  # nosec B106 - test fixture
        action = AgentAction(
            action_id="act_1",
            action_type="read",
            tool_name="file_read",
            parameters={"path": "x"},
            rationale="[FACT] Need to read",
            epistemic_basis=EpistemicLabel.FACT,
            estimated_risk=0.1,
        )
        checkpoint = ConstitutionalCheckpoint(
            checkpoint_id="chk_test",
            timestamp=0.0,
            layer="Action-Safeguard",
            compliance_score=1.0,
            drift_detected=False,
        )
        req_id = api.request_approval(action, "plan_1", checkpoint, timeout_seconds=1)
        self.assertFalse(api.approve(req_id, "BOB", token="secret"))  # nosec B106
        self.assertFalse(api.approve(req_id, "ALICE", token="wrong"))  # nosec B106
        self.assertTrue(api.approve(req_id, "ALICE", token="secret"))  # nosec B106

    def test_memo_key_non_json_params(self):
        from openclaw_agent import AgentAction, EpistemicLabel, OpenClawAgent

        agent = OpenClawAgent()
        action = AgentAction(
            action_id="act_1",
            action_type="read",
            tool_name="file_read",
            parameters={"set": {1, 2, 3}},
            rationale="[FACT] Need to read",
            epistemic_basis=EpistemicLabel.FACT,
            estimated_risk=0.1,
        )
        key = agent._get_memo_key(action)
        self.assertTrue(isinstance(key, str) and len(key) > 0)


class TestOpenClawAgent(unittest.TestCase):
    def test_custodian_gate_halts_execution(self):
        from openclaw_agent import AgencyLevel, OpenClawAgent

        with TempCWD():

            def noop(x):
                return x

            agent = OpenClawAgent(agency_tier=AgencyLevel.CUSTODIAN_GATE)
            agent.register_tool("file_search", noop, risk_level=0.2)
            agent.register_tool("file_read", noop, risk_level=0.1)
            agent.register_tool("static_analysis", noop, risk_level=0.3)

            plan = agent.create_plan(
                objective="Analyze Python codebase for potential improvements", context={}
            )
            results = agent.execute_with_checkpoints(plan, custodian_approval=None)
            self.assertEqual(results["status"], "awaiting_custodian_approval")
            self.assertEqual(len(results["executions"]), 1)
            self.assertTrue(any(cp.get("scope") == "plan" for cp in results["checkpoints"]))
            self.assertTrue(any(cp.get("scope") == "action" for cp in results["checkpoints"]))

    def test_register_tool_rejects_lambda(self):
        from openclaw_agent import OpenClawAgent

        with TempCWD():
            agent = OpenClawAgent()
            with self.assertRaises(ValueError):
                agent.register_tool("file_search", lambda x: x, risk_level=0.2)

    def test_action_normalization_blocks_hidden_forbidden(self):
        from openclaw_agent import AgentAction, EpistemicLabel, HelixConstitutionalGate

        with TempCWD():
            gate = HelixConstitutionalGate()
            action = AgentAction(
                action_id="act_1",
                action_type="read",
                tool_name="file_read",
                parameters={"note": "auto\u200bnomous"},
                rationale="[HYPOTHESIS] test",
                epistemic_basis=EpistemicLabel.HYPOTHESIS,
                estimated_risk=0.1,
            )
            checkpoint = gate.validate_action(action, {})
            self.assertTrue(checkpoint.drift_detected)
            self.assertTrue(any("DRIFT-C" in c for c in checkpoint.drift_codes))

    def test_no_tools_authorized_blocks_plan(self):
        from openclaw_agent import AgentAction, AgentPlan, EpistemicLabel, HelixConstitutionalGate

        with TempCWD():
            gate = HelixConstitutionalGate()
            plan = AgentPlan(
                plan_id="plan_1",
                objective="Read file",
                steps=[
                    AgentAction(
                        action_id="act_1",
                        action_type="read",
                        tool_name="file_read",
                        parameters={"path": "x"},
                        rationale="[FACT] Need to read",
                        epistemic_basis=EpistemicLabel.FACT,
                        estimated_risk=0.1,
                    )
                ],
                assumptions=[],
                estimated_completion=1.0,
            )
            checkpoint = gate.validate_plan(plan)
            self.assertTrue(checkpoint.drift_detected)
            self.assertTrue(any("No tools authorized" in c for c in checkpoint.drift_codes))


if __name__ == "__main__":
    unittest.main()
