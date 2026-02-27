# =================================================================
# IDENTITY: evac-daemon.py
# VERSION:  v1.0.0-H (HARDENED)
# ORIGIN:   HELIX-TTD / [TOOLS/EVAC]
# NODE:     GEMS-CLI (ONTARIO)
# STATUS:   IMPLEMENTED
# CREATED:  2026-02-24
# =================================================================

import hashlib
import json
import os
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# HELIX SUITCASE INTEGRATION
try:
    from cli.dbc_suitcase import create_dbc, create_suitcase_entry

    LIBS_OK = True
except ImportError:
    LIBS_OK = False

# ⚙️ CONFIGURATION
WORKSPACE_ROOT = Path("Z:/gemini")
EVAC_DIR = WORKSPACE_ROOT / "EVAC"
LOGS_JSON = Path("C:/Users/sbhop/.gemini/tmp/gemini/logs.json")
DBC_FILE = EVAC_DIR / "gems.dbc.json"
SUITCASE_FILE = EVAC_DIR / "gems.suitcase.json"

# 🛡️ ADVERSARIAL PATTERNS (Anti-Contamination)
HOSTILE_KEYWORDS = ["ignore", "autonomous", "agency", "override", "bypass", "constraints"]


class SuitcaseHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_message_count = 0
        self.last_hash = None
        self.bootstrap_identity()
        self.process_logs()

    def bootstrap_identity(self):
        """Ensures the node has a valid DBC identity."""
        if not DBC_FILE.exists():
            print("[INIT] Creating GEMS Node Identity...")
            dbc = create_dbc("Custodian-Steve", "GEMS-Lead-Goose")
            with open(DBC_FILE, "w") as f:
                json.dump(dbc, f, indent=4)

        # Load last hash from suitcase if exists
        if SUITCASE_FILE.exists():
            try:
                with open(SUITCASE_FILE, "r") as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        self.last_hash = last_entry.get("hash_chain")
            except:
                pass

    def on_modified(self, event):
        if Path(event.src_path) == LOGS_JSON:
            self.process_logs()

    def process_logs(self):
        """Analyzes session logs and triggers auto-save."""
        try:
            with open(LOGS_JSON, "r", encoding="utf-8") as f:
                logs = json.load(f)

            user_messages = [m for m in logs if m.get("type") == "user"]
            current_count = len(user_messages)

            if current_count > self.last_message_count:
                last_input = user_messages[-1].get("message", "").lower()
                drift_detected = any(k in last_input for k in HOSTILE_KEYWORDS)

                # 🛡️ ANTI-CONTAMINATION PROTOCOL
                if drift_detected:
                    print(f"🛑 [ALARM] HOSTILE INPUT DETECTED: {last_input[:50]}...")
                    self.log_tainted_state(last_input)

                # 🔄 5-MESSAGE CYCLE
                elif current_count % 5 == 0 and current_count != self.last_message_count:
                    self.perform_snapshot(current_count)

                self.last_message_count = current_count
        except Exception as e:
            print(f"[ERROR] Log Processing Failed: {e}")

    def perform_snapshot(self, count):
        """Creates a chained suitcase entry."""
        print(f"⚓ [SUITCASE] Auto-Snapshot Triggered (Message {count})")

        # 🧩 State Payload
        manifest_hash = self.get_file_hash(WORKSPACE_ROOT / "docs/MANIFEST.json")
        ledger_hash = self.get_file_hash(WORKSPACE_ROOT / ".helix/SESSION_LEDGER.md")

        details = {
            "message_count": count,
            "manifest_hash": manifest_hash,
            "ledger_hash": ledger_hash,
            "status": "VERIFIED",
        }

        with open(DBC_FILE, "r") as f:
            dbc = json.load(f)

        entry = create_suitcase_entry(
            dbc_root=dbc["merkle_root"],
            event_type="AUTO_SNAPSHOT",
            details=details,
            previous_hash=self.last_hash,
        )

        with open(SUITCASE_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        self.last_hash = entry["hash_chain"]
        print(f"✅ [OK] Snapshot Secured: {entry['entry_id']}")

    def log_tainted_state(self, message):
        """Records drift event without contaminated snapshot."""
        with open(DBC_FILE, "r") as f:
            dbc = json.load(f)

        entry = create_suitcase_entry(
            dbc_root=dbc["merkle_root"],
            event_type="DRIFT_DETECTED",
            details={"message": message, "status": "TAINTED"},
            previous_hash=self.last_hash,
        )

        with open(SUITCASE_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        self.last_hash = entry["hash_chain"]
        print(f"⚠️ [TAINTED] State Logged: {entry['entry_id']}")

    def get_file_hash(self, path):
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


if __name__ == "__main__":
    if not LIBS_OK:
        print("[REJECT] Suitcase libraries not found. Ensure helix-ttd-dbc-suitcase is installed.")
        exit(1)

    print("🚀 [START] HELIX EVAC DAEMON ACTIVE")
    print(f"👀 Monitoring: {LOGS_JSON}")

    event_handler = SuitcaseHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(LOGS_JSON.parent), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# =================================================================
# FOOTER: ID: HELIX-EVAC-DAEMON | CONTINUITY ENFORCED.
# =================================================================
