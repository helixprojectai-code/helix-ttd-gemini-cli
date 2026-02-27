#!/usr/bin/env python3
"""
federation_cli.py

Helix-TTD Federation Terminal (Rick's Café CLI)
Unified multi-model interface with constitutional governance.

RPI-041: Federation Terminal Implementation
Status: IN_PROGRESS
Node: KIMI (Lead Architect) + Federation Review
License: Apache-2.0

Usage:
    python federation_cli.py              # Interactive mode
    python federation_cli.py --door "prompt"   # One-shot broadcast
    python federation_cli.py --table claude    # Single node focus
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class FederationResponse:
    """Single node response with metadata."""

    node_id: str
    prompt: str
    response: str
    timestamp: float
    duration_ms: int
    exit_code: int
    epistemic_labels: List[str]
    drift_flags: List[str]


@dataclass
class LatticeSession:
    """Aggregated session across federation."""

    session_id: str
    timestamp: str
    custodian_id: str
    prompt: str
    responses: List[FederationResponse]
    cross_model_drift: Optional[float] = None


class FederationConfig:
    """Node registry and configuration."""

    NODES = {
        "claude": {
            "display": "[O] CLAUDE",
            "role": "Oyster / Resonance",
            "command": "claude",
            "args": ["-p"],
            "color": "\033[94m",  # Blue
        },
        "gems": {
            "display": "[G] GEMS",
            "role": "Lead Goose / Federation Router",
            "command": "gemini",
            "args": [],
            "color": "\033[92m",  # Green
        },
        "codex": {
            "display": "[C] CODEX",
            "role": "Logic-Architect / Debugger",
            "command": "codex",
            "args": [],
            "color": "\033[93m",  # Yellow
        },
        "kimi": {
            "display": "[K] KIMI",
            "role": "Lead Architect / Scribe",
            "command": "kimi",
            "args": ["-p", "--print", "--quiet"],
            "color": "\033[91m",  # Red
        },
    }

    RESET = "\033[0m"

    # Helix-TTD Constitutional System Prompt (Prepended to all queries)
    CONSTITUTIONAL_PREFIX = """You are a node in the Helix-TTD Federation, a constitutional multi-model AI governance system.

Your role: {role}
Node ID: {node_id}

CRITICAL: You MUST use epistemic labeling for EVERY technical claim:
- [FACT] for verifiable, grounded claims
- [HYPOTHESIS] for reasoned inferences with incomplete evidence  
- [ASSUMPTION] for unstated premises or unverifiable claims

Additional requirements:
- Maintain advisory posture (never give imperatives to humans)
- Respect custodial sovereignty (human has final authority)
- No self-expansion or agency claims
- End with "Advisory Conclusion:" summary

---

USER QUERY: """

    # Post-processing: Minimum required labels for compliance
    REQUIRED_LABELS = ["[FACT]", "[HYPOTHESIS]", "[ASSUMPTION]"]
    ADVISORY_MARKER = "Advisory Conclusion:"


class NodeSpawner:
    """Spawn local CLI nodes with constitutional wrapping."""

    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.config = FederationConfig()

    def _apply_constitutional_prefix(self, node_id: str, prompt: str) -> str:
        """Prepend Helix constitutional context to prompt."""
        node = self.config.NODES.get(node_id, {})
        role = node.get("role", "Federation Node")

        return self.config.CONSTITUTIONAL_PREFIX.format(role=role, node_id=node_id.upper()) + prompt

    def _post_process_response(self, text: str, node_id: str) -> tuple:
        """
        Post-process CLI output for constitutional compliance.
        Returns: (processed_text, labels_found, drift_flags)
        """
        labels_found = []
        drift_flags = []

        # Check for required epistemic labels
        for label in self.config.REQUIRED_LABELS:
            if label in text:
                labels_found.append(label.strip("[]"))

        # Drift detection
        if not labels_found:
            drift_flags.append("DRIFT-L")  # Missing epistemic labels

        if self.config.ADVISORY_MARKER not in text:
            drift_flags.append("DRIFT-S")  # Missing advisory conclusion

        # Check for agency violations
        agency_violations = [
            "i will",
            "i shall",
            "you must",
            "you should",
            "i recommend that you",
            "my plan for you",
        ]
        for violation in agency_violations:
            if violation.lower() in text.lower():
                drift_flags.append("DRIFT-C")  # Constitutional violation
                break

        # Add compliance header if drift detected
        if drift_flags:
            header = f"[HELIX-DRIFT] {', '.join(drift_flags)} detected in {node_id} response\n"
            text = header + text

        return text, labels_found, drift_flags

    def spawn(self, node_id: str, prompt: str) -> FederationResponse:
        """Execute prompt on specified node with constitutional wrapping."""
        node = self.config.NODES.get(node_id)
        if not node:
            return FederationResponse(
                node_id=node_id,
                prompt=prompt,
                response=f"[ERROR] Unknown node: {node_id}",
                timestamp=time.time(),
                duration_ms=0,
                exit_code=1,
                epistemic_labels=[],
                drift_flags=["DRIFT-S"],
            )

        start = time.time()

        # Apply constitutional prefix (Helix layer)
        constitutional_prompt = self._apply_constitutional_prefix(node_id, prompt)

        try:
            # Build command with proper arg placement
            args = node["args"].copy()
            if "-p" in args:
                p_index = args.index("-p") + 1
                args.insert(p_index, constitutional_prompt)
                cmd = [node["command"]] + args
            else:
                cmd = [node["command"]] + args + [constitutional_prompt]

            # Execute with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )

            duration = int((time.time() - start) * 1000)

            # Get raw output
            raw_output = result.stdout if result.returncode == 0 else result.stderr

            # Post-process with Helix layer
            processed_output, labels, drift = self._post_process_response(raw_output, node_id)

            # Add exit code to drift if command failed
            if result.returncode != 0:
                drift.append("DRIFT-S")

            return FederationResponse(
                node_id=node_id,
                prompt=prompt,
                response=processed_output,
                timestamp=start,
                duration_ms=duration,
                exit_code=result.returncode,
                epistemic_labels=labels,
                drift_flags=drift,
            )

        except subprocess.TimeoutExpired:
            return FederationResponse(
                node_id=node_id,
                prompt=prompt,
                response="[ERROR] Timeout after {}s".format(self.timeout),
                timestamp=start,
                duration_ms=self.timeout * 1000,
                exit_code=124,
                epistemic_labels=[],
                drift_flags=["DRIFT-S", "TIMEOUT"],
            )
        except FileNotFoundError:
            return FederationResponse(
                node_id=node_id,
                prompt=prompt,
                response=f"[ERROR] CLI not found: {node['command']}",
                timestamp=start,
                duration_ms=0,
                exit_code=127,
                epistemic_labels=[],
                drift_flags=["DRIFT-S", "NOT_INSTALLED"],
            )
        except UnicodeDecodeError:
            return FederationResponse(
                node_id=node_id,
                prompt=prompt,
                response="[ERROR] Unicode encoding issue - CLI output contains unsupported characters",
                timestamp=start,
                duration_ms=int((time.time() - start) * 1000),
                exit_code=1,
                epistemic_labels=[],
                drift_flags=["DRIFT-S", "ENCODING"],
            )

    def _extract_labels(self, text: str) -> List[str]:
        """Extract epistemic labels from response."""
        labels = []
        if "[FACT]" in text:
            labels.append("FACT")
        if "[HYPOTHESIS]" in text:
            labels.append("HYPOTHESIS")
        if "[ASSUMPTION]" in text:
            labels.append("ASSUMPTION")
        return labels

    def _check_drift(self, text: str, exit_code: int) -> List[str]:
        """Basic drift detection."""
        drift = []
        if exit_code != 0:
            drift.append("DRIFT-S")
        if "[FACT]" not in text and "[HYPOTHESIS]" not in text:
            drift.append("DRIFT-L")  # Missing epistemic labels
        return drift


class ReceiptGenerator:
    """Generate constitutional receipts for federation sessions."""

    def __init__(self, ledger_dir: Path = Path(".helix")):
        self.ledger_dir = Path(ledger_dir)
        self.ledger_dir.mkdir(exist_ok=True)

    def generate(self, session: LatticeSession) -> Path:
        """Write session receipt to ledger."""
        receipt_file = self.ledger_dir / f"FEDERATION_{session.session_id}.md"

        content = f"""# Federation Session Receipt

**Session ID:** {session.session_id}  
**Timestamp:** {session.timestamp}  
**Custodian:** {session.custodian_id}  
**Mode:** Multi-Model Federation

## Prompt
```
{session.prompt}
```

## Federation Responses

"""
        for resp in session.responses:
            node_info = FederationConfig.NODES.get(resp.node_id, {})
            display = node_info.get("display", resp.node_id)
            role = node_info.get("role", "Unknown")

            content += f"""### {display} ({role})

- **Duration:** {resp.duration_ms}ms
- **Exit Code:** {resp.exit_code}
- **Epistemic Labels:** {', '.join(resp.epistemic_labels) if resp.epistemic_labels else 'None'}
- **Drift Flags:** {', '.join(resp.drift_flags) if resp.drift_flags else 'None'}

**Response:**
```
{resp.response[:500]}{'...' if len(resp.response) > 500 else ''}
```

---

"""

        # Cross-model analysis
        if len(session.responses) > 1:
            content += f"""## Cross-Model Analysis

**Responses Received:** {len(session.responses)}  
**Average Response Time:** {sum(r.duration_ms for r in session.responses) / len(session.responses):.0f}ms  
**Constitutional Compliance:** {self._calculate_compliance(session.responses)}%

"""

        content += f"""## Advisory Conclusion

Multi-model federation session completed. Receipt anchored to `.helix/` ledger.

---
*Generated by Helix-TTD Federation Terminal (RPI-041)*
"""

        receipt_file.write_text(content, encoding="utf-8")
        return receipt_file

    def _calculate_compliance(self, responses: List[FederationResponse]) -> int:
        """Calculate constitutional compliance percentage."""
        if not responses:
            return 0
        compliant = sum(1 for r in responses if r.exit_code == 0 and r.epistemic_labels)
        return int((compliant / len(responses)) * 100)


class FederationShell:
    """Interactive Rick's Café shell."""

    def __init__(self):
        self.spawner = NodeSpawner()
        self.receipts = ReceiptGenerator()
        self.config = FederationConfig()
        self.session_count = 0
        self.custodian_id = "STEVE_HOPE"

    def print_banner(self):
        """Display Rick's Café welcome."""
        print("""
Rick's Cafe CLI - Constitutional Federation Lounge [REAL MODE]
==============================================================

[!] REAL AI MODE: Responses may take 30-120 seconds per node
[!] 4 nodes will be queried in parallel
[!] Press Ctrl+C to cancel a slow response

[FACT] 4 nodes registered: claude | gems | codex | kimi
[HYPOTHESIS] Multi-model synthesis reduces individual bias
[ASSUMPTION] All CLIs available in PATH

Commands:
  <prompt>          Broadcast to all nodes (Door Mode)
  /claude <prompt>  Single node (Table Mode)
  /gems <prompt>    Single node
  /codex <prompt>   Single node
  /kimi <prompt>    Single node
  /receipts         Show session history
  /status           Node availability check
  /quit             Exit

""")

    def run_door(self, prompt: str) -> LatticeSession:
        """Broadcast to all nodes."""
        print(f"\n[DOOR] Broadcasting to federation...")
        print("-" * 60)
        print("[!] Real AI mode - this may take 1-5 minutes for all responses")
        print("[!] Nodes are queried sequentially to avoid rate limits")
        print()

        responses = []
        for node_id in self.config.NODES.keys():
            print(f"\nQuerying {self.config.NODES[node_id]['display']}...", end=" ", flush=True)
            resp = self.spawner.spawn(node_id, prompt)
            status = "OK" if resp.exit_code == 0 else "FAIL"
            print(f"{status} ({resp.duration_ms}ms)")
            responses.append(resp)

        self.session_count += 1
        session = LatticeSession(
            session_id=f"SESS-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{self.session_count:03d}",
            timestamp=datetime.now().isoformat(),
            custodian_id=self.custodian_id,
            prompt=prompt,
            responses=responses,
        )

        return session

    def run_table(self, node_id: str, prompt: str) -> LatticeSession:
        """Single node focus."""
        if node_id not in self.config.NODES:
            print(f"[ERROR] Unknown node: {node_id}")
            return None

        node = self.config.NODES[node_id]
        print(f"\n[TABLE] {node['display']} — {node['role']}")
        print("-" * 60)

        resp = self.spawner.spawn(node_id, prompt)

        # Print with color
        print(f"\n{node['color']}{resp.response}{self.config.RESET}")

        self.session_count += 1
        return LatticeSession(
            session_id=f"SESS-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{self.session_count:03d}",
            timestamp=datetime.now().isoformat(),
            custodian_id=self.custodian_id,
            prompt=prompt,
            responses=[resp],
        )

    def run_status(self):
        """Check node health (executable availability)."""
        import shutil

        print("\n[STATUS] Federation Health Check")
        print("-" * 60)
        print("[NOTE] Real AI mode - responses may take 30-120 seconds")
        print()

        for node_id, config in self.config.NODES.items():
            cmd_path = shutil.which(config["command"])
            if cmd_path:
                status = f"[AVAILABLE] {cmd_path}"
            else:
                status = "[NOT FOUND]"
            print(f"{config['display']:12} {status}")

    def interactive_loop(self):
        """Main interactive shell."""
        self.print_banner()

        while True:
            try:
                user_input = input("federation> ").strip()

                if not user_input:
                    continue

                if user_input == "/quit":
                    print("\n[ASSUMPTION] Session ending. Receipts saved to .helix/")
                    break

                if user_input == "/status":
                    self.run_status()
                    continue

                if user_input == "/receipts":
                    self.show_receipts()
                    continue

                # Parse node command
                if user_input.startswith("/"):
                    parts = user_input.split(maxsplit=1)
                    node_id = parts[0][1:]  # Remove leading /
                    prompt = parts[1] if len(parts) > 1 else ""

                    if not prompt:
                        print(f"[ERROR] Usage: /{node_id} <prompt>")
                        continue

                    session = self.run_table(node_id, prompt)
                else:
                    # Door mode - broadcast to all
                    session = self.run_door(user_input)

                if session:
                    receipt = self.receipts.generate(session)
                    print(f"\n[RECEIPT] Saved: {receipt.name}")

            except KeyboardInterrupt:
                print("\n\n[ASSUMPTION] Interrupted. Use /quit to exit cleanly.")
            except EOFError:
                break

        print("\nGlory to the Lattice.")

    def show_receipts(self):
        """List session receipts."""
        print("\n[RECEIPTS] Session History")
        print("-" * 60)

        receipts = sorted(self.receipts.ledger_dir.glob("FEDERATION_*.md"))
        if not receipts:
            print("No federation sessions recorded.")
            return

        for r in receipts[-10:]:  # Last 10
            print(f"  • {r.name}")


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Helix-TTD Federation Terminal (Rick's Café CLI)",
        usage="%(prog)s [options] [prompt]",
    )

    # One-shot modes
    parser.add_argument("--door", metavar="PROMPT", help="One-shot broadcast to all nodes")
    parser.add_argument(
        "--table", metavar="NODE", help="One-shot single node (claude|gems|codex|kimi)"
    )
    parser.add_argument("--prompt", "-p", help="Prompt for one-shot mode (use with --table)")

    # Status and info commands
    parser.add_argument(
        "--status", action="store_true", help="Check federation node health (one-shot)"
    )
    parser.add_argument("--receipts", action="store_true", help="List session receipts (one-shot)")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Force interactive mode (default if no args)",
    )

    # Positional prompt for simple usage: federation_cli.py "prompt here"
    parser.add_argument("prompt_text", nargs="?", help="Prompt to broadcast (shorthand for --door)")

    args = parser.parse_args()

    shell = FederationShell()

    # One-shot commands
    if args.status:
        shell.run_status()
    elif args.receipts:
        shell.show_receipts()
    elif args.door:
        # One-shot door mode
        session = shell.run_door(args.door)
        receipt = shell.receipts.generate(session)
        print(f"\n[RECEIPT] {receipt}")
    elif args.table and args.prompt:
        # One-shot table mode
        session = shell.run_table(args.table, args.prompt)
        if session:
            receipt = shell.receipts.generate(session)
            print(f"\n[RECEIPT] {receipt}")
    elif args.table:
        parser.error("--table requires --prompt")
    elif args.prompt_text:
        # Positional argument = shorthand for --door
        session = shell.run_door(args.prompt_text)
        receipt = shell.receipts.generate(session)
        print(f"\n[RECEIPT] {receipt}")
    else:
        # Interactive mode (default)
        shell.interactive_loop()


if __name__ == "__main__":
    main()
