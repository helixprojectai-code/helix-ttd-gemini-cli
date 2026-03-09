#!/usr/bin/env python3
"""Publish production alert summaries to Cloud Logging."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import logging as cloud_logging

SEVERITY_BY_STATUS = {
    "pass": "INFO",
    "warn": "WARNING",
    "page": "ERROR",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish a production alert summary JSON document to Cloud Logging."
    )
    parser.add_argument("--input", required=True, help="Path to the alert summary JSON file.")
    parser.add_argument(
        "--log-name",
        default="helix-production-alerts",
        help="Cloud Logging log name.",
    )
    parser.add_argument(
        "--component",
        default="constitutional-guardian",
        help="Component label to attach to the log entry.",
    )
    return parser.parse_args()


def load_summary(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    args = parse_args()
    summary_path = Path(args.input)
    summary = load_summary(summary_path)
    overall_status = str(summary.get("overall_status", "unknown")).lower()
    severity = SEVERITY_BY_STATUS.get(overall_status, "DEFAULT")

    payload = {
        **summary,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source": "github-actions-production-alert-check",
    }

    client = cloud_logging.Client()
    logger = client.logger(args.log_name)
    logger.log_struct(
        payload,
        severity=severity,
        labels={
            "component": args.component,
            "overall_status": overall_status,
        },
    )
    print(f"Published production alert summary to log '{args.log_name}' with severity {severity}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
