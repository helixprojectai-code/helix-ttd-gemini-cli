#!/usr/bin/env python3
"""
Constitutional Compliance Check
Validates code against Helix-TTD constitutional principles.
Part of CI/CD hardening for helix-ttd-gemini v1.4.0
"""

import re
import sys
from pathlib import Path

# Directories to scan
SCAN_DIRS = ["code", "helix-ttd-gemini-cli-fresh"]
EXCLUDE_PATTERNS = ["__pycache__", ".pyc", "check_constitutional.py"]

# Constitutional patterns to check
CONSTITUTIONAL_CHECKS = {
    "creator_intent": {
        "pattern": re.compile(r"CREATOR_INTENT|CreatorIntent|creator_intent", re.IGNORECASE),
        "required": False,
        "description": "References to CREATOR_INTENT principle",
    },
    "sovereignty": {
        "pattern": re.compile(r"sovereign|sov_|SOVEREIGN", re.IGNORECASE),
        "required": False,
        "description": "Sovereignty-related terminology",
    },
    "epistemic": {
        "pattern": re.compile(r"epistemic|uncertainty|confidence", re.IGNORECASE),
        "required": False,
        "description": "Epistemic labeling patterns",
    },
}

# Forbidden patterns (anti-patterns)
FORBIDDEN_PATTERNS = {
    "hardcoded_secret": {
        "pattern": re.compile(
            r'(password|secret|key|token)\s*=\s*["\'][^"\']{3,}["\']', re.IGNORECASE
        ),
        "exclude_files": ["test_", "_test.py", "example", "sample"],
        "description": "Hardcoded credentials in production code",
    },
    "debug_print": {
        "pattern": re.compile(r"^\s*print\s*\(", re.MULTILINE),
        "exclude_files": ["test_", "_test.py", "cli", "debug"],
        "description": "Debug print statements (use logging)",
        "warning_only": True,
    },
}


def get_python_files() -> list[Path]:
    """Find all Python files in scan directories."""
    files = []
    for dir_name in SCAN_DIRS:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob("*.py"):
            if any(pat in str(py_file) for pat in EXCLUDE_PATTERNS):
                continue
            files.append(py_file)
    return files


def check_file(file_path: Path) -> dict[str, list[dict[str, object]]]:
    """Check a single file for constitutional compliance."""
    results: dict[str, list[dict[str, object]]] = {
        "constitutional_hits": [],
        "violations": [],
        "warnings": [],
    }

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
    except (OSError, UnicodeDecodeError):
        return results

    # Check for constitutional patterns
    for name, check in CONSTITUTIONAL_CHECKS.items():
        pattern: re.Pattern[str] = check["pattern"]
        matches = pattern.findall(content)
        if matches:
            results["constitutional_hits"].append(
                {
                    "check": name,
                    "description": check["description"],
                    "count": len(matches),
                }
            )

    # Check for forbidden patterns
    for name, check in FORBIDDEN_PATTERNS.items():
        # Skip excluded files
        if any(excl in str(file_path) for excl in check.get("exclude_files", [])):
            continue

        for line_num, line in enumerate(lines, 1):
            pattern: re.Pattern[str] = check["pattern"]
            if pattern.search(line):
                # Skip lines with # nosec or # noqa
                if "# nosec" in line or "# noqa" in line:
                    continue

                issue = {
                    "check": name,
                    "description": check["description"],
                    "line": line_num,
                    "content": line.strip()[:80],
                }

                if check.get("warning_only"):
                    results["warnings"].append(issue)
                else:
                    results["violations"].append(issue)

    return results


def main() -> int:
    """Main entry point."""
    print("[CONSTITUTIONAL] Helix Compliance Check")
    print("=" * 50)

    files = get_python_files()
    if not files:
        print("[WARN] No Python files found")
        return 0

    print(f"[INFO] Scanning {len(files)} files...")

    total_violations = 0
    total_warnings = 0
    constitutional_files = 0

    for file_path in files:
        results = check_file(file_path)

        if results["constitutional_hits"]:
            constitutional_files += 1

        if results["violations"]:
            print(f"\n[VIOLATION] {file_path}")
            for v in results["violations"]:
                print(f"  Line {v['line']}: {v['description']}")
                print(f"    {v['content']}")
                total_violations += 1

        if results["warnings"]:
            for w in results["warnings"]:
                print(f"[WARNING] {file_path}:{w['line']} - {w['description']}")
                total_warnings += 1

    print("\n" + "=" * 50)
    print(f"[SUMMARY] Files scanned: {len(files)}")
    print(f"[SUMMARY] Constitutional files: {constitutional_files}")
    print(f"[SUMMARY] Violations: {total_violations}")
    print(f"[SUMMARY] Warnings: {total_warnings}")

    if total_violations > 0:
        print("\n[FAIL] Constitutional violations detected")
        return 1

    print("\n[PASS] Constitutional compliance verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
