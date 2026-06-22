#!/usr/bin/env python
"""Run a bounded research-discovery automation cycle from frozen seed artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from industrial_research_lab.pipeline import PROFILES, run_profile


ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "literature/GAP_MAP.md",
    "hypotheses/HYPOTHESES_RANKED.csv",
    "experiments/EXPERIMENT_PLAN.md",
    "claims/CLAIM_EVIDENCE_MATRIX.csv",
    "protocol/PREREGISTRATION.md",
    "reports/portfolio/PORTFOLIO_REPORT.md",
    "reports/portfolio/PAPER_OPPORTUNITIES.md",
    "reports/portfolio/NEXT_ACTIONS.md",
)


def copy_source(relative: str, output_root: Path) -> None:
    source = ROOT / relative
    target = output_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_manifest(output_root: Path) -> None:
    manifest_path = output_root / "DISCOVERY_MANIFEST.json"
    checksum_path = output_root / "CHECKSUMS.sha256"
    files = []
    for path in sorted(output_root.rglob("*")):
        if not path.is_file() or path in {manifest_path, checksum_path}:
            continue
        data = path.read_bytes()
        files.append({
            "path": path.relative_to(output_root).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    manifest_path.write_text(
        json.dumps({
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "scientific_status": "exploratory_local_corpus_only",
            "files": files,
        }, indent=2),
        encoding="utf-8",
    )
    checksum_path.write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in files),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=Path("artifacts/research-discovery"))
    parser.add_argument("--pilot-profile", choices=("ci", "smoke"), default="ci")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    for relative in SOURCES:
        copy_source(relative, output_root)

    pilot = run_profile(
        PROFILES[args.pilot_profile],
        output_root / "results" / "pilot",
        resume=not args.fresh,
    )
    validation_dir = output_root / "results" / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        output_root / "results" / "pilot" / "VALIDATION_REPORT.md",
        validation_dir / "VALIDATION_REPORT.md",
    )
    status = {
        "status": "complete" if pilot["infrastructure_pass"] else "failed",
        "scientific_status": "exploratory_local_corpus_only",
        "publishability_established": False,
        "literature_live_search_completed": False,
        "stages": [
            "literature_gap_map",
            "hypothesis_generation_and_ranking",
            "experiment_design",
            "preregistration",
            "pilot",
            "validation",
            "portfolio_report",
            "paper_opportunities_screen",
            "next_actions",
        ],
        "pilot_profile": args.pilot_profile,
        "pilot_infrastructure_pass": pilot["infrastructure_pass"],
    }
    (output_root / "DISCOVERY_STATUS.json").write_text(
        json.dumps(status, indent=2), encoding="utf-8"
    )
    write_manifest(output_root)
    print(json.dumps(status, indent=2))
    return 0 if status["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
