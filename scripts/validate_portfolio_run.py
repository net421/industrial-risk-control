#!/usr/bin/env python
"""Validate a generated portfolio-run artifact directory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    errors = []
    required = (
        "summary.json", "summary.csv", "batch_metrics.csv", "checkpoint.json",
        "RUN_REPORT.md", "PERFORMANCE_REPORT.md", "VALIDATION_REPORT.md",
        "RUN_MANIFEST.json", "CHECKSUMS.sha256",
    )
    for name in required:
        path = run_dir / name
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty: {name}")

    summary_path = run_dir / "summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if not summary.get("infrastructure_pass"):
            errors.append("infrastructure_pass is not true")
        if summary.get("status") != "complete":
            errors.append("run status is not complete")

    manifest_path = run_dir / "RUN_MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("files", []):
            path = run_dir / item["path"]
            if not path.exists():
                errors.append(f"manifest path missing: {item['path']}")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != item["sha256"]:
                errors.append(f"checksum mismatch: {item['path']}")

    if errors:
        print("PORTFOLIO RUN VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PORTFOLIO RUN VALIDATION PASSED")
    print(f"- run directory: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

