#!/usr/bin/env python3
"""GCP-native production checker for Constitutional Guardian."""

from __future__ import annotations

import argparse
import json
import math
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from google.cloud import logging as cloud_logging
from google.cloud import storage

SEVERITY_BY_STATUS = {
    "pass": "INFO",
    "warn": "WARNING",
    "page": "ERROR",
    "failed": "CRITICAL",
}


@dataclass
class MetricSample:
    name: str
    labels: dict[str, str]
    value: float


class MonitorIntegrityError(RuntimeError):
    """Raised when the monitor itself cannot authenticate or scrape production."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the production monitoring check and publish a structured summary."
    )
    parser.add_argument(
        "--service-url",
        default="https://constitutional-guardian-231586465188.us-central1.run.app",
    )
    parser.add_argument("--admin-token", default=os.getenv("HELIX_ADMIN_TOKEN", ""))
    parser.add_argument(
        "--state-gcs-uri",
        default="gs://helix-ai-deploy-receipts/ops/production-alert-state.json",
    )
    parser.add_argument("--log-name", default="helix-production-alerts")
    parser.add_argument("--component", default="constitutional-guardian-monitor")
    parser.add_argument("--artifact-grace-minutes", type=int, default=30)
    parser.add_argument("--state-retention-hours", type=int, default=24)
    parser.add_argument("--fail-on-alert", action="store_true")
    return parser.parse_args()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_gcs_uri(uri: str) -> tuple[str, str]:
    if not uri.startswith("gs://"):
        raise ValueError(f"Unsupported GCS URI: {uri}")
    without_scheme = uri[5:]
    bucket, _, blob = without_scheme.partition("/")
    if not bucket or not blob:
        raise ValueError(f"Expected gs://bucket/path form: {uri}")
    return bucket, blob


def http_get(url: str, headers: dict[str, str]) -> tuple[int, str]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.getcode(), response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def get_json(url: str, headers: dict[str, str]) -> dict[str, Any]:
    status, body = http_get(url, headers)
    if status != 200:
        raise MonitorIntegrityError(f"JSON scrape failed for {url} with status {status}")
    return json.loads(body)


def get_text(url: str, headers: dict[str, str]) -> str:
    status, body = http_get(url, headers)
    if status != 200:
        raise MonitorIntegrityError(f"Text scrape failed for {url} with status {status}")
    return body


def parse_labels(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    labels: dict[str, str] = {}
    for part in raw.split(","):
        key, _, value = part.partition("=")
        if not key or not value:
            continue
        labels[key] = value.strip().strip('"')
    return labels


def parse_prometheus_text(text: str) -> list[MetricSample]:
    samples: list[MetricSample] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        name_and_labels, _, value_text = stripped.rpartition(" ")
        if not value_text:
            continue
        if "{" in name_and_labels and name_and_labels.endswith("}"):
            metric_name, label_blob = name_and_labels.split("{", 1)
            labels = parse_labels(label_blob[:-1])
        else:
            metric_name = name_and_labels
            labels = {}
        try:
            value = float(value_text)
        except ValueError:
            continue
        samples.append(MetricSample(name=metric_name, labels=labels, value=value))
    return samples


def metric_value(
    samples: list[MetricSample],
    name: str,
    labels: dict[str, str] | None = None,
    default: float = math.nan,
) -> float:
    expected = labels or {}
    for sample in samples:
        if sample.name != name:
            continue
        if all(sample.labels.get(key) == value for key, value in expected.items()):
            return sample.value
    return default


def metric_label_value(
    samples: list[MetricSample],
    name: str,
    label: str,
    labels: dict[str, str] | None = None,
    default: str = "missing",
) -> str:
    expected = labels or {}
    for sample in samples:
        if sample.name != name:
            continue
        if all(sample.labels.get(key) == value for key, value in expected.items()):
            return sample.labels.get(label, default)
    return default


def load_state(storage_client: storage.Client, state_uri: str) -> dict[str, Any]:
    bucket_name, blob_name = parse_gcs_uri(state_uri)
    blob = storage_client.bucket(bucket_name).blob(blob_name)
    if not blob.exists():
        return {"snapshots": []}
    raw = blob.download_as_text()
    if not raw.strip():
        return {"snapshots": []}
    return json.loads(raw)


def save_state(storage_client: storage.Client, state_uri: str, state: dict[str, Any]) -> None:
    bucket_name, blob_name = parse_gcs_uri(state_uri)
    blob = storage_client.bucket(bucket_name).blob(blob_name)
    blob.upload_from_string(json.dumps(state, indent=2), content_type="application/json")


def baseline_snapshot(
    snapshots: list[dict[str, Any]], now: datetime, window_minutes: int
) -> dict[str, Any] | None:
    target = now - timedelta(minutes=window_minutes)
    eligible = [
        snapshot
        for snapshot in snapshots
        if datetime.fromisoformat(snapshot["timestamp"]) <= target
    ]
    if not eligible:
        return None
    eligible.sort(key=lambda snapshot: snapshot["timestamp"], reverse=True)
    return eligible[0]


def counter_delta(
    current: dict[str, Any], baseline: dict[str, Any] | None, field: str
) -> float | None:
    if baseline is None:
        return None
    return max(float(current["counters"][field]) - float(baseline["counters"][field]), 0.0)


def make_check(name: str, severity: str, passed: bool, details: str) -> dict[str, Any]:
    return {"Check": name, "Severity": severity, "Passed": passed, "Details": details}


def publish_summary(summary: dict[str, Any], log_name: str, component: str) -> None:
    severity = SEVERITY_BY_STATUS.get(summary.get("overall_status", "failed"), "DEFAULT")
    client = cloud_logging.Client()
    logger = client.logger(log_name)
    logger.log_struct(
        summary,
        severity=severity,
        labels={
            "component": component,
            "overall_status": str(summary.get("overall_status", "failed")),
            "monitor_integrity_status": str(summary.get("monitor_integrity_status", "unknown")),
        },
    )


def build_failure_summary(now: datetime, service_url: str, details: str) -> dict[str, Any]:
    check = make_check("monitor-integrity", "page", False, details)
    return {
        "evaluated_at": now.isoformat(),
        "service_url": service_url,
        "overall_status": "failed",
        "monitor_integrity_status": "failed",
        "artifact_status": "unknown",
        "artifact_image": "unknown",
        "storage_backend": "unknown",
        "storage_mode": "unknown",
        "page_failures": [check],
        "warn_failures": [],
        "checks": [check],
    }


def main() -> int:
    args = parse_args()
    if not args.admin_token:
        summary = build_failure_summary(
            utcnow(),
            args.service_url,
            "HELIX_ADMIN_TOKEN is required for Cloud Run Job monitoring.",
        )
        print(json.dumps(summary, indent=2))
        publish_summary(summary, args.log_name, args.component)
        return 1

    headers = {"X-Helix-Admin-Token": args.admin_token}
    now = utcnow()

    try:
        preflight_status, _ = http_get(
            f"{args.service_url.rstrip('/')}/api/runtime-config", headers
        )
        if preflight_status != 200:
            raise MonitorIntegrityError(
                f"Runtime-config preflight auth failed with status {preflight_status}"
            )

        metrics_text = get_text(f"{args.service_url.rstrip('/')}/metrics", headers)
        security_body = get_json(
            f"{args.service_url.rstrip('/')}/api/security-transparency", headers
        )
    except MonitorIntegrityError as exc:
        summary = build_failure_summary(now, args.service_url, str(exc))
        print(json.dumps(summary, indent=2))
        publish_summary(summary, args.log_name, args.component)
        return 1

    samples = parse_prometheus_text(metrics_text)
    storage_client = storage.Client()
    state = load_state(storage_client, args.state_gcs_uri)

    artifact_status = metric_label_value(samples, "helix_artifact_analysis_state", "status")
    artifact_image = metric_label_value(samples, "helix_artifact_analysis_state", "image_uri")
    storage_backend = metric_label_value(samples, "helix_receipt_storage_backend", "backend")
    storage_mode = metric_label_value(samples, "helix_receipt_storage_backend", "mode")
    origin_enforced = metric_value(samples, "helix_guardian_origin_enforced")
    auth_enforced = metric_value(samples, "helix_operator_auth_enforced")

    current_snapshot = {
        "timestamp": now.isoformat(),
        "counters": {
            "operator_auth_failure": metric_value(
                samples, "helix_security_events_total", {"event": "operator_auth_failure"}, 0
            ),
            "operator_rate_limit": metric_value(
                samples, "helix_security_events_total", {"event": "operator_rate_limit"}, 0
            ),
            "audio_rate_limit": metric_value(
                samples, "helix_security_events_total", {"event": "audio_rate_limit"}, 0
            ),
            "websocket_auth_failure": metric_value(
                samples, "helix_security_events_total", {"event": "websocket_auth_failure"}, 0
            ),
        },
    }

    retention_cutoff = now - timedelta(hours=args.state_retention_hours)
    kept_snapshots = [
        snapshot
        for snapshot in state.get("snapshots", [])
        if datetime.fromisoformat(snapshot["timestamp"]) >= retention_cutoff
    ]
    all_snapshots = [*kept_snapshots, current_snapshot]
    save_state(storage_client, args.state_gcs_uri, {"snapshots": all_snapshots})

    results: list[dict[str, Any]] = []
    results.append(
        make_check("operator-auth-enforced", "page", auth_enforced == 1, f"value={auth_enforced}")
    )
    results.append(
        make_check(
            "guardian-origin-enforced", "page", origin_enforced == 1, f"value={origin_enforced}"
        )
    )
    results.append(
        make_check(
            "receipt-backend-posture",
            "page",
            storage_backend == "gcs+local" and storage_mode == "dual",
            f"backend={storage_backend}; mode={storage_mode}",
        )
    )

    latest_scan_timestamp_raw = str(security_body.get("latest_scan_timestamp", "unavailable"))
    artifact_scan_timestamp_raw = str(
        security_body.get("artifact_analysis", {}).get("scan_timestamp", "unavailable")
    )
    artifact_details = f"status={artifact_status}; image_uri={artifact_image}"
    artifact_passed = True
    if artifact_status == "unverified":
        deploy_anchor: datetime | None = None
        if latest_scan_timestamp_raw and latest_scan_timestamp_raw != "unavailable":
            try:
                deploy_anchor = datetime.fromisoformat(
                    latest_scan_timestamp_raw.replace("Z", "+00:00")
                ).astimezone(timezone.utc)
            except ValueError:
                deploy_anchor = None
        if deploy_anchor is None:
            artifact_passed = False
            artifact_details += "; unverified_for_minutes=unknown"
        else:
            age_minutes = round((now - deploy_anchor).total_seconds() / 60.0, 1)
            artifact_passed = age_minutes <= args.artifact_grace_minutes
            artifact_details += f"; unverified_for_minutes={age_minutes}"
    elif artifact_status == "clean":
        artifact_details += f"; verified_at={artifact_scan_timestamp_raw}"
    results.append(
        make_check("artifact-verification-window", "warn", artifact_passed, artifact_details)
    )

    thresholds = [
        {
            "name": "operator-auth-failure-burst-5m",
            "severity": "warn",
            "field": "operator_auth_failure",
            "window": 5,
            "threshold": 5,
        },
        {
            "name": "operator-auth-failure-burst-15m",
            "severity": "page",
            "field": "operator_auth_failure",
            "window": 15,
            "threshold": 20,
        },
        {
            "name": "operator-rate-limit-burst-10m",
            "severity": "warn",
            "field": "operator_rate_limit",
            "window": 10,
            "threshold": 10,
        },
        {
            "name": "operator-rate-limit-burst-15m",
            "severity": "page",
            "field": "operator_rate_limit",
            "window": 15,
            "threshold": 50,
        },
        {
            "name": "audio-rate-limit-burst-5m",
            "severity": "warn",
            "field": "audio_rate_limit",
            "window": 5,
            "threshold": 10,
        },
        {
            "name": "audio-rate-limit-burst-10m",
            "severity": "page",
            "field": "audio_rate_limit",
            "window": 10,
            "threshold": 30,
        },
        {
            "name": "websocket-auth-failure-burst-5m",
            "severity": "warn",
            "field": "websocket_auth_failure",
            "window": 5,
            "threshold": 5,
        },
        {
            "name": "websocket-auth-failure-burst-15m",
            "severity": "page",
            "field": "websocket_auth_failure",
            "window": 15,
            "threshold": 20,
        },
    ]

    for rule in thresholds:
        baseline = baseline_snapshot(all_snapshots, now, rule["window"])
        if baseline is None:
            results.append(
                make_check(
                    rule["name"],
                    rule["severity"],
                    True,
                    f"insufficient_history=true; window_minutes={rule['window']}",
                )
            )
            continue
        delta = counter_delta(current_snapshot, baseline, rule["field"])
        passed = delta is not None and delta < rule["threshold"]
        results.append(
            make_check(
                rule["name"],
                rule["severity"],
                passed,
                f"delta={delta}; threshold={rule['threshold']}; window_minutes={rule['window']}",
            )
        )

    page_failures = [
        check for check in results if not check["Passed"] and check["Severity"] == "page"
    ]
    warn_failures = [
        check for check in results if not check["Passed"] and check["Severity"] == "warn"
    ]

    overall_status = "pass"
    if page_failures:
        overall_status = "page"
    elif warn_failures:
        overall_status = "warn"

    summary = {
        "evaluated_at": now.isoformat(),
        "service_url": args.service_url,
        "overall_status": overall_status,
        "monitor_integrity_status": "ok",
        "artifact_status": artifact_status,
        "artifact_image": artifact_image,
        "storage_backend": storage_backend,
        "storage_mode": storage_mode,
        "page_failures": page_failures,
        "warn_failures": warn_failures,
        "checks": results,
    }

    print(json.dumps(summary, indent=2))
    publish_summary(summary, args.log_name, args.component)

    if args.fail_on_alert and overall_status != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
