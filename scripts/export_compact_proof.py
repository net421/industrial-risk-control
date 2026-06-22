#!/usr/bin/env python
"""Export compact, commit-safe evidence from a validated full run."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


FILES = (
    "config.json",
    "summary.json",
    "summary.csv",
    "VALIDATION_REPORT.md",
    "PERFORMANCE_REPORT.md",
    "RUN_REPORT.md",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.run_dir.resolve()
    output = args.output.resolve()
    summary = json.loads((source / "summary.json").read_text(encoding="utf-8"))
    if not summary.get("infrastructure_pass") or summary.get("status") != "complete":
        raise SystemExit("source run has not passed validation")
    output.mkdir(parents=True, exist_ok=True)
    items = []
    for name in FILES:
        source_path = source / name
        target_path = output / name
        lines = source_path.read_text(encoding="utf-8").splitlines()
        if source_path.suffix == ".md":
            lines = [line.rstrip() for line in lines]
        target_path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
        data = target_path.read_bytes()
        items.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    (output / "PROOF_MANIFEST.json").write_text(
        json.dumps({
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "source_run": source.name,
            "excluded_large_files": ["checkpoint.json", "batch_metrics.csv"],
            "files": items,
        }, indent=2),
        encoding="utf-8",
    )
    (output / "CHECKSUMS.sha256").write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in items),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(output), "files": len(items)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
