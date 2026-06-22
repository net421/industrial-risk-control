#!/usr/bin/env python
"""Validate the evidence-linked vertical-cycle artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED = ("literature/OPENALEX_RECORDS.json", "literature/CORPUS.csv", "literature/GAP_MAP.md", "hypotheses/HYPOTHESES_RANKED.csv", "experiments/FROZEN_EXPERIMENT.json", "claims/CLAIM_EVIDENCE_MATRIX.csv", "results/pilot/summary.json", "reports/PORTFOLIO_REPORT.md", "reports/SKEPTICAL_REVIEW.md", "VERTICAL_CYCLE_STATUS.json", "VERTICAL_CYCLE_MANIFEST.json", "CHECKSUMS.sha256")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    root = parser.parse_args().run_dir.resolve()
    errors = [f"missing: {p}" for p in REQUIRED if not (root / p).is_file() or (root / p).stat().st_size == 0]
    status_path = root / "VERTICAL_CYCLE_STATUS.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        if status.get("status") != "complete" or not status.get("live_literature_search"):
            errors.append("cycle did not complete live retrieval")
        if status.get("novelty_established") is not False or status.get("paper_ready") is not False:
            errors.append("scientific boundary missing")
    manifest_path = root / "VERTICAL_CYCLE_MANIFEST.json"
    if manifest_path.exists():
        for item in json.loads(manifest_path.read_text(encoding="utf-8")).get("files", []):
            path = root / item["path"]
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                errors.append(f"checksum mismatch: {item['path']}")
    if errors:
        print("VERTICAL CYCLE VALIDATION FAILED")
        print("\n".join(f"- {e}" for e in errors))
        return 1
    print("VERTICAL CYCLE VALIDATION PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
