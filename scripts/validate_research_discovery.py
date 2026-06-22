#!/usr/bin/env python
"""Validate bounded research-discovery outputs and checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED = (
    "literature/GAP_MAP.md",
    "hypotheses/HYPOTHESES_RANKED.csv",
    "experiments/EXPERIMENT_PLAN.md",
    "claims/CLAIM_EVIDENCE_MATRIX.csv",
    "results/validation/VALIDATION_REPORT.md",
    "reports/portfolio/PORTFOLIO_REPORT.md",
    "reports/portfolio/PAPER_OPPORTUNITIES.md",
    "reports/portfolio/NEXT_ACTIONS.md",
    "DISCOVERY_STATUS.json",
    "DISCOVERY_MANIFEST.json",
    "CHECKSUMS.sha256",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.run_dir.resolve()
    errors = []
    for relative in REQUIRED:
        path = root / relative
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty: {relative}")
    status_path = root / "DISCOVERY_STATUS.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "complete":
            errors.append("discovery status is not complete")
        if status.get("publishability_established") is not False:
            errors.append("publishability boundary is missing")
    manifest_path = root / "DISCOVERY_MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("files", []):
            path = root / item["path"]
            if not path.exists():
                errors.append(f"manifest path missing: {item['path']}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                errors.append(f"checksum mismatch: {item['path']}")
    if errors:
        print("RESEARCH DISCOVERY VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESEARCH DISCOVERY VALIDATION PASSED")
    print("- all required stages produced artifacts")
    print("- publishability remains unestablished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
