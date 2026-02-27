"""[FACT] Helix-TTD Python Toolkit package root.

[HYPOTHESIS] Constitutional AI governance utilities for the Helix-TTD Federation.

[ASSUMPTION] All submodules are importable and functional.

Version: 1.0.0
License: Apache-2.0

Modules:
    - naming_convention: [FACT] File naming enforcement
    - drift_telemetry: [FACT] Constitutional monitoring
    - constitutional_compliance: [FACT] Civic Firmware Stack
    - receipts_manager: [FACT] Personal directory and receipts
    - looksee_audit: [FACT] Phase 6 validation
    - rpi_tracker: [FACT] RPI cycle management

Usage:
    [ASSUMPTION] Import and instantiate classes as needed.
    from helix_cli import HelixCLI
    cli = HelixCLI()
    cli.cmd_status()
"""

__version__ = "1.0.0"
__author__ = "Stephen Hope"
__license__ = "Apache-2.0"

from constitutional_compliance import ConstitutionalCompliance
from drift_telemetry import DriftCode, DriftTelemetry
from looksee_audit import LookseeAudit, LookseeAuditor

# Make key classes available at package level
from naming_convention import HelixFilename, NamingConvention
from receipts_manager import PersonalDirectory, Receipt
from rpi_tracker import RPIPhase, RPITracker

__all__ = [
    "NamingConvention",
    "HelixFilename",
    "DriftTelemetry",
    "DriftCode",
    "ConstitutionalCompliance",
    "PersonalDirectory",
    "Receipt",
    "LookseeAuditor",
    "LookseeAudit",
    "RPITracker",
    "RPIPhase",
]
