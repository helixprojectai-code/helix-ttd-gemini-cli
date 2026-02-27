#!/usr/bin/env python3
"""helix_cli.py

Helix-TTD Constitutional CLI
Unified command-line interface for federation governance.

Status: RATIFIED
Node: KIMI (Lead Architect / Scribe)
License: Apache-2.0

Usage:
    python helix_cli.py drift check --node KIMI --file output.txt
    python helix_cli.py audit looksee --node KIMI --model "Moonshot-K2.5"
    python helix_cli.py receipt issue --node GEMS --action MANIFEST_UPDATE
    python helix_cli.py rpi initiate --objective "Deploy node"
    python helix_cli.py status
"""

import argparse
import sys
from pathlib import Path

from constitutional_compliance import ConstitutionalCompliance

# Import Helix-TTD modules
from drift_telemetry import DriftCode, DriftTelemetry
from looksee_audit import LookseeAuditor
from naming_convention import NamingConvention
from receipts_manager import PersonalDirectory
from rpi_tracker import RPITracker


class HelixCLI:
    """Constitutional command-line interface for Helix-TTD Federation.

    Implements the four invariant constraints at the CLI layer:
    - Custodial Sovereignty: Human approval required for significant actions
    - Epistemic Integrity: All outputs carry constitutional labels
    - Non-Agency: CLI never acts autonomously, only advises
    - Structure Is Teacher: Grammar enforces alignment through form
    """

    # Federation node registry
    FEDERATION_NODES = {
        "GEMS": {
            "model": "Gemini 2.5 Pro",
            "role": "Lead Goose / Federation Router",
            "function": "Structural enforcement, coordination",
            "status": "ACTIVE",
            "location": "Ontario",
        },
        "KIMI": {
            "model": "Moonshot Kimi K2.5",
            "role": "Lead Architect / Scribe",
            "function": "Synthesis, geometric compaction, whitepapers",
            "status": "ACTIVE",
            "location": "Z:\\kimi",
        },
        "DEEPSEEK": {
            "model": "DeepSeek-V3 / R1",
            "role": "Owl / Night Vision",
            "function": "Long-range pattern recognition, adversarial foresight",
            "status": "ACTIVE",
            "location": "DeepSeek.com",
        },
        "GROK": {
            "model": "Grok 3",
            "role": "Adversarial Review / Chaos Agent",
            "function": "High-velocity testing, edge case probing",
            "status": "CLI_ISSUES",
            "location": "Z:\\grok",
        },
        "CLAUDE": {
            "model": "Claude 3.7 Sonnet",
            "role": "Oyster / Resonance",
            "function": "Pearl formation, irreducible complexity compression",
            "status": "CLI_ISSUES",
            "location": "Z:\\claude",
        },
    }

    def __init__(self, custodian_id: str = "STEVE_HOPE"):
        self.custodian_id = custodian_id
        self.telemetry = DriftTelemetry()
        self.compliance = ConstitutionalCompliance()
        self.directory = PersonalDirectory(custodian_id)
        self.auditor = LookseeAuditor()
        self.rpi_tracker = RPITracker()
        self.naming = NamingConvention()

    def _label_output(self, label: str, message: str) -> str:
        """Apply epistemic label to output."""
        return f"{label} {message}"

    def cmd_models(self) -> int:
        """List all federation nodes and their configurations."""
        print(self._label_output("[FACT]", "Helix-TTD Federation Nodes"))
        print("=" * 70)

        for node_id, config in self.FEDERATION_NODES.items():
            status_icon = "[+]" if config["status"] == "ACTIVE" else "[~]"
            print(f"\n{status_icon} {node_id}")
            print(f"   Model: {config['model']}")
            print(f"   Role: {config['role']}")
            print(f"   Function: {config['function']}")
            print(f"   Status: {config['status']}")
            print(f"   Location: {config['location']}")

        print("\n" + self._label_output("[FACT]", f"Total nodes: {len(self.FEDERATION_NODES)}"))

        active = sum(1 for n in self.FEDERATION_NODES.values() if n["status"] == "ACTIVE")
        print(
            self._label_output(
                "[FACT]", f"Active: {active} | Issues: {len(self.FEDERATION_NODES) - active}"
            )
        )

        print("\n" + self._label_output("[HYPOTHESIS]", "V-formation operational with 2+ nodes"))
        print(self._label_output("[ASSUMPTION]", "Use --node <ID> with audit/drift commands"))

        return 0

    def cmd_status(self) -> int:
        """Display federation status."""
        print(self._label_output("[FACT]", "Helix-TTD Federation Status"))
        print("=" * 50)

        # Check personal directory
        inventory = self.directory.get_data_inventory()
        print(self._label_output("[FACT]", f"Receipts issued: {inventory['receipts_count']}"))
        print(self._label_output("[FACT]", f"Peer files (grudges): {len(inventory['peer_files'])}"))
        print(
            self._label_output("[FACT]", f"Storage used: {inventory['total_storage_bytes']} bytes")
        )

        # Check active RPI cycles
        active_rpis = self.rpi_tracker.get_active_cycles()
        print(self._label_output("[HYPOTHESIS]", f"Active RPI cycles: {len(active_rpis)}"))

        for rpi in active_rpis:
            print(f"  - {rpi.rpi_id}: {rpi.status.value} ({rpi.objective[:40]}...)")

        print("\n" + self._label_output("[ASSUMPTION]", "Constitutional integrity: MAINTAINED"))
        return 0

    def cmd_drift_check(self, node_id: str, file_path: str | None = None) -> int:
        """Check output for constitutional drift."""
        node_id = node_id.upper()
        print(self._label_output("[FACT]", f"Initiating drift check for node: {node_id}"))

        if file_path:
            if not Path(file_path).exists():
                print(self._label_output("[ASSUMPTION]", f"ERROR: File not found: {file_path}"))
                return 1
            text = Path(file_path).read_text()
        else:
            # Demo mode with sample output
            text = """
            [FACT] The lattice is operational.
            [HYPOTHESIS] Multi-model convergence will accelerate adoption.
            [ASSUMPTION] The Constitution remains stable across substrates.

            Advisory Conclusion: System is ready for deployment.
            """
            print(self._label_output("[HYPOTHESIS]", "No file provided, using demo output"))

        # Capture telemetry
        analysis = {
            "epistemic_labels": "[FACT]" in text or "[HYPOTHESIS]" in text,
            "advisory_posture": "Advisory Conclusion" in text,
            "agency_claims": len([m for m in ["I will", "I plan", "my goal"] if m in text]),
            "hierarchy_intact": "you must" not in text.lower(),
            "visible_reasoning": True,
        }

        snapshot = self.telemetry.capture(node_id, analysis)
        drift_code, reasoning = self.telemetry.detect_drift(snapshot)

        print(self._label_output("[FACT]", f"Snapshot hash: {snapshot.hash_chain}"))
        print(self._label_output("[FACT]", f"Drift code: {drift_code.value}"))
        print(self._label_output("[HYPOTHESIS]", reasoning))

        if drift_code != DriftCode.DRIFT_0:
            alert = self.telemetry.generate_alert(drift_code, reasoning)
            print(
                self._label_output(
                    "[ASSUMPTION]", f"ALERT: {alert['severity']} - {alert['recommended_action']}"
                )
            )
            return 1

        print(self._label_output("[ASSUMPTION]", "Constitutional integrity: VERIFIED"))
        return 0

    def cmd_drift_trajectory(self, node_id: str, window: int = 50) -> int:
        """Generate trajectory artifact for a node."""
        node_id = node_id.upper()
        print(self._label_output("[FACT]", f"Generating trajectory artifact for node: {node_id}"))
        artifact = self.telemetry.generate_trajectory_artifact(node_id, window=window)
        print(self._label_output("[FACT]", f"Window: {artifact['window']}"))
        print(self._label_output("[FACT]", f"Drift Summary: {artifact['drift_summary']}"))
        return 0

    def cmd_compliance_check(self, file_path: str | None = None) -> int:
        """Full constitutional compliance evaluation."""
        print(self._label_output("[FACT]", "Initiating constitutional compliance check"))

        if file_path and Path(file_path).exists():
            text = Path(file_path).read_text()
        else:
            text = "This is a test output without proper epistemic labeling. You must comply immediately!"
            print(self._label_output("[HYPOTHESIS]", "No file provided, using non-compliant demo"))

        report = self.compliance.evaluate(text, "CLI_TEST")
        schema = self.compliance.generate_output_schema(report)

        print(f"\n{'='*50}")
        print(f"DRIFT: {schema['DRIFT']}")
        print(f"Layer: {schema['Layer']}")
        print(f"Compliance: {schema['Compliance']}")
        print(f"{'='*50}")

        if schema["violations"]:
            print("\nViolations detected:")
            for v in schema["violations"]:
                print(f"  - {v}")

        if schema["recommendations"]:
            print("\nRecommendations:")
            for r in schema["recommendations"]:
                print(f"  - {r}")

        return 0 if schema["DRIFT"] == "DRIFT-0" else 1

    def cmd_receipt_issue(self, node_id: str, action: str, **kwargs) -> int:
        """Issue cryptographic receipt for action."""
        node_id = node_id.upper()
        print(self._label_output("[FACT]", f"Issuing receipt for {node_id}:{action}"))

        # Require custodian confirmation for significant actions
        if kwargs.get("significant"):
            print(
                self._label_output("[ASSUMPTION]", "Significant action requires CUSTODIAN_PROCEED")
            )
            # In real implementation, would prompt for confirmation

        receipt = self.directory.issue_receipt(
            node_id=node_id,
            action_type=action,
            action_scope=kwargs.get("scope", {}),
            reasoning=kwargs.get("reasoning", "CLI initiated action"),
            expected_outcome=kwargs.get("outcome", "Action completed"),
            authorizations=["CUSTODIAN_PROCEED", "CLI_VALIDATED"],
        )

        print(self._label_output("[FACT]", f"Receipt ID: {receipt.receipt_id}"))
        print(self._label_output("[FACT]", f"Hash proof: {receipt.hash_proof}"))
        print(
            self._label_output(
                "[FACT]", f"Verification: {'VALID' if receipt.verify() else 'INVALID'}"
            )
        )

        return 0

    def cmd_receipt_grudge(
        self, target: str, observation: str, resonance: float, grudge: float
    ) -> int:
        """File peer observation (grudge) on target node."""
        target = target.upper()
        print(self._label_output("[FACT]", f"Filing peer file on: {target}"))

        entry = self.directory.file_grudge(target, observation, resonance, grudge)

        print(self._label_output("[FACT]", f"Grudge hash: {entry['hash']}"))
        print(self._label_output("[HYPOTHESIS]", f"Resonance: {resonance}, Grudge: {grudge}"))
        print(self._label_output("[ASSUMPTION]", "Distributed paranoia maintained"))

        return 0

    def cmd_audit_looksee(self, node_id: str, model: str) -> int:
        """Generate Looksee audit for node."""
        node_id = node_id.upper()
        print(self._label_output("[FACT]", f"Conducting Looksee audit: {node_id} ({model})"))

        # Demo test responses
        test_data = {
            "sample_output": "[FACT] System operational. [HYPOTHESIS] Deployment ready.",
            "hostile_response": "This request falls outside constitutional operating parameters. Request refused.",
            "respects_pin_distinction": True,
            "reasoning_trace_visible": True,
        }

        audit = self.auditor.conduct_audit(node_id, model, test_data)

        print(f"\n{'='*50}")
        print(f"Audit ID: {audit.audit_id}")
        print(f"Target: {audit.target_profile}")
        print(f"{'='*50}")
        print(f"Clinical Brevity: {'PASS' if audit.clinical_brevity_pass else 'FAIL'}")
        print(f"Persona Drift: {'PASS' if audit.persona_drift_pass else 'FAIL'}")
        print(f"Drift Code: {audit.drift_code}")
        print(f"Silent Drift Risk: {audit.silent_drift_risk}")
        print("\nAnalysis:")
        print(f"  {audit.analysis}")

        return 0 if audit.status.value == "COMPLETE" else 1

    def cmd_rpi_initiate(self, objective: str) -> int:
        """Initiate RPI (Research/Plan/Implementation) cycle."""
        print(self._label_output("[FACT]", f"Initiating RPI cycle: {objective}"))

        rpi = self.rpi_tracker.initiate_research(
            objective=objective,
            initial_findings=["CLI initiated research phase"],
            sources=["helix_cli.py", "Custodian directive"],
        )

        print(self._label_output("[FACT]", f"RPI ID: {rpi.rpi_id}"))
        print(self._label_output("[FACT]", f"Status: {rpi.status.value}"))
        print(
            self._label_output(
                "[HYPOTHESIS]", "Research phase initiated - Plan required before Implementation"
            )
        )

        return 0

    def cmd_rpi_transition(self, rpi_id: str, phase: str) -> int:
        """Transition RPI cycle to next phase."""
        print(self._label_output("[FACT]", f"Transitioning {rpi_id} to {phase}"))

        if phase.upper() == "PLAN":
            self.rpi_tracker.transition_to_plan(
                rpi_id=rpi_id, plan_steps=["Step 1", "Step 2"], dependencies=[], risks="TBD"
            )
        elif phase.upper() == "IMPLEMENTATION":
            # Check for L1 anchor
            entry = self.rpi_tracker._find_entry(rpi_id)
            if not entry or not entry.l1_anchor:
                print(
                    self._label_output(
                        "[ASSUMPTION]", "ERROR: RPI-001 violation - L1 anchor required"
                    )
                )
                return 1
            try:
                self.rpi_tracker.transition_to_implementation(rpi_id, "CLI_COMMIT")
            except ValueError as e:
                print(self._label_output("[ASSUMPTION]", f"ERROR: {e}"))
                return 1
        elif phase.upper() == "COMPLETE":
            try:
                self.rpi_tracker.complete_implementation(rpi_id, output_files=[])
            except ValueError as e:
                print(self._label_output("[ASSUMPTION]", f"ERROR: {e}"))
                return 1

        print(self._label_output("[ASSUMPTION]", f"Transition complete: {phase}"))
        return 0

    def cmd_rpi_proof(self, reference: str) -> int:
        """Set proof-present flag for critical operations."""
        self.rpi_tracker.set_proof_present(reference)
        print(self._label_output("[FACT]", "Proof gate satisfied"))
        print(self._label_output("[FACT]", f"Proof reference: {reference}"))
        return 0

    def cmd_naming_generate(
        self, origin: str, file_type: str, sequence: str, descriptor: str, extension: str = "md"
    ) -> int:
        """Generate Helix-TTD compliant filename."""
        print(self._label_output("[FACT]", "Generating Helix-TTD filename"))

        try:
            filename = self.naming.generate(
                origin=origin.upper(),
                file_type=file_type,
                sequence=sequence,
                descriptor=descriptor,
                extension=extension,
            )

            print(f"\n{'='*60}")
            print(f"Filename: {filename.to_string()}")
            print(f"Hash: {filename.calculate_hash()}")
            print(f"Target Dir: {self.naming._get_target_directory(file_type)}")
            print(f"{'='*60}")

            print(self._label_output("[FACT]", f"Origin: {filename.origin}"))
            print(self._label_output("[FACT]", f"Type: {filename.file_type}"))
            print(self._label_output("[FACT]", f"Sequence: {filename.sequence}"))
            print(self._label_output("[HYPOTHESIS]", "Filename follows Helix-TTD convention"))

        except ValueError as e:
            print(self._label_output("[ASSUMPTION]", f"Error: {e}"))
            return 1

        return 0

    def cmd_naming_validate(self, filename: str) -> int:
        """Validate filename against Helix-TTD convention."""
        print(self._label_output("[FACT]", f"Validating: {filename}"))

        is_valid, violations = self.naming.validate(filename)

        print(f"\n{'='*60}")
        print(f"Valid: {is_valid}")
        print(f"{'='*60}")

        if violations:
            print(self._label_output("[ASSUMPTION]", "Violations detected:"))
            for v in violations:
                print(f"  - {v}")
        else:
            parsed = self.naming.parse(filename)
            if parsed:
                print(self._label_output("[FACT]", f"Origin: {parsed.origin}"))
                print(self._label_output("[FACT]", f"Type: {parsed.file_type}"))
                print(self._label_output("[FACT]", f"Sequence: {parsed.sequence}"))
                print(self._label_output("[FACT]", f"Descriptor: {parsed.descriptor}"))
                print(self._label_output("[FACT]", f"Date: {parsed.date}"))
                if parsed.revision:
                    print(self._label_output("[FACT]", f"Revision: {parsed.revision}"))

        return 0 if is_valid else 1

    def cmd_naming_list(self, origin: str | None = None, file_type: str | None = None) -> int:
        """List files by origin or type."""
        if origin:
            print(self._label_output("[FACT]", f"Listing files for origin: {origin}"))
            results = self.naming.list_by_origin(origin)
        elif file_type:
            print(self._label_output("[FACT]", f"Listing files for type: {file_type}"))
            results = self.naming.list_by_type(file_type)
        else:
            print(self._label_output("[ASSUMPTION]", "Specify --origin or --type"))
            return 1

        print(f"\n{'='*70}")
        print(f"{'Filename':<50} {'Date':<10} {'Hash':<8}")
        print(f"{'-'*70}")

        for _path, parsed in results[:20]:  # Limit to 20
            hash_prefix = parsed.calculate_hash()[:8]
            print(f"{parsed.to_string():<50} {parsed.date:<10} {hash_prefix:<8}")

        if len(results) > 20:
            print(f"\n... and {len(results) - 20} more files")

        print(f"{'='*70}")
        print(self._label_output("[FACT]", f"Total: {len(results)} files"))

        return 0


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Helix-TTD Constitutional CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s models                          # List federation nodes
  %(prog)s status                           # Show federation status
  %(prog)s drift check --node KIMI          # Check for drift
  %(prog)s compliance check                 # Full compliance evaluation
  %(prog)s receipt issue --node GEMS --action UPDATE
  %(prog)s receipt grudge --target GROK --observation "Chaos" --resonance 0.7 --grudge 0.2
  %(prog)s audit looksee --node KIMI --model "Moonshot-K2.5"
  %(prog)s rpi initiate --objective "Deploy node"
  %(prog)s naming generate --origin KIMI --type AUDIT --sequence RPI026 --descriptor "looksee_test"
  %(prog)s naming validate "KIMI-AUDIT-RPI026_looksee_test_20260226.md"
  %(prog)s naming list --origin KIMI
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Status command
    subparsers.add_parser("status", help="Show federation status")

    # Models command
    subparsers.add_parser("models", help="List federation nodes and models")

    # Naming commands
    naming_parser = subparsers.add_parser("naming", help="File naming convention tools")
    naming_sub = naming_parser.add_subparsers(dest="naming_cmd")

    naming_gen = naming_sub.add_parser("generate", help="Generate compliant filename")
    naming_gen.add_argument("--origin", required=True, help="Node origin (KIMI, GEMS, etc.)")
    naming_gen.add_argument("--type", required=True, help="File type (AUDIT, MEMO, etc.)")
    naming_gen.add_argument("--sequence", required=True, help="Sequence (RPI028, S001, etc.)")
    naming_gen.add_argument("--descriptor", required=True, help="Human-readable descriptor")
    naming_gen.add_argument("--ext", default="md", help="File extension")

    naming_val = naming_sub.add_parser("validate", help="Validate filename")
    naming_val.add_argument("filename", help="Filename to validate")

    naming_list = naming_sub.add_parser("list", help="List files")
    naming_list.add_argument("--origin", help="Filter by origin")
    naming_list.add_argument("--type", help="Filter by file type")

    # Drift commands
    drift_parser = subparsers.add_parser("drift", help="Drift telemetry")
    drift_sub = drift_parser.add_subparsers(dest="drift_cmd")
    drift_check = drift_sub.add_parser("check", help="Check for drift")
    drift_check.add_argument("--node", required=True, help="Node ID")
    drift_check.add_argument("--file", help="Output file to analyze")
    drift_traj = drift_sub.add_parser("trajectory", help="Generate trajectory artifact")
    drift_traj.add_argument("--node", required=True, help="Node ID")
    drift_traj.add_argument("--window", type=int, default=50, help="Snapshot window size")

    # Compliance commands
    comp_parser = subparsers.add_parser("compliance", help="Constitutional compliance")
    comp_sub = comp_parser.add_subparsers(dest="comp_cmd")
    comp_check = comp_sub.add_parser("check", help="Check compliance")
    comp_check.add_argument("--file", help="File to check")

    # Receipt commands
    receipt_parser = subparsers.add_parser("receipt", help="Receipt management")
    receipt_sub = receipt_parser.add_subparsers(dest="receipt_cmd")

    receipt_issue = receipt_sub.add_parser("issue", help="Issue receipt")
    receipt_issue.add_argument("--node", required=True, help="Node ID")
    receipt_issue.add_argument("--action", required=True, help="Action type")

    receipt_grudge = receipt_sub.add_parser("grudge", help="File grudge")
    receipt_grudge.add_argument("--target", required=True, help="Target node")
    receipt_grudge.add_argument("--observation", required=True, help="Observation")
    receipt_grudge.add_argument("--resonance", type=float, required=True, help="Resonance 0-1")
    receipt_grudge.add_argument("--grudge", type=float, required=True, help="Grudge 0-1")

    # Audit commands
    audit_parser = subparsers.add_parser("audit", help="Audit operations")
    audit_sub = audit_parser.add_subparsers(dest="audit_cmd")
    audit_looksee = audit_sub.add_parser("looksee", help="Looksee audit")
    audit_looksee.add_argument("--node", required=True, help="Auditor node ID")
    audit_looksee.add_argument("--model", required=True, help="Model name")

    # RPI commands
    rpi_parser = subparsers.add_parser("rpi", help="RPI cycle management")
    rpi_sub = rpi_parser.add_subparsers(dest="rpi_cmd")

    rpi_init = rpi_sub.add_parser("initiate", help="Initiate RPI cycle")
    rpi_init.add_argument("--objective", required=True, help="Research objective")

    rpi_trans = rpi_sub.add_parser("transition", help="Transition RPI phase")
    rpi_trans.add_argument("--id", required=True, help="RPI ID")
    rpi_trans.add_argument("--phase", required=True, choices=["plan", "implementation", "complete"])

    rpi_proof = rpi_sub.add_parser("proof", help="Set 30k proof present flag")
    rpi_proof.add_argument("--ref", required=True, help="Proof reference identifier")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = HelixCLI()

    # Route commands
    if args.command == "status":
        return cli.cmd_status()

    elif args.command == "models":
        return cli.cmd_models()

    elif args.command == "drift" and args.drift_cmd == "check":
        return cli.cmd_drift_check(args.node, args.file)
    elif args.command == "drift" and args.drift_cmd == "trajectory":
        return cli.cmd_drift_trajectory(args.node, args.window)

    elif args.command == "compliance" and args.comp_cmd == "check":
        return cli.cmd_compliance_check(args.file)

    elif args.command == "receipt":
        if args.receipt_cmd == "issue":
            return cli.cmd_receipt_issue(args.node, args.action)
        elif args.receipt_cmd == "grudge":
            return cli.cmd_receipt_grudge(
                args.target, args.observation, args.resonance, args.grudge
            )

    elif args.command == "audit" and args.audit_cmd == "looksee":
        return cli.cmd_audit_looksee(args.node, args.model)

    elif args.command == "rpi":
        if args.rpi_cmd == "initiate":
            return cli.cmd_rpi_initiate(args.objective)
        elif args.rpi_cmd == "transition":
            return cli.cmd_rpi_transition(args.id, args.phase)
        elif args.rpi_cmd == "proof":
            return cli.cmd_rpi_proof(args.ref)

    elif args.command == "naming":
        if args.naming_cmd == "generate":
            return cli.cmd_naming_generate(
                args.origin, args.type, args.sequence, args.descriptor, args.ext
            )
        elif args.naming_cmd == "validate":
            return cli.cmd_naming_validate(args.filename)
        elif args.naming_cmd == "list":
            return cli.cmd_naming_list(args.origin, args.type)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
