#!/usr/bin/env python
"""Create a deterministic artifact manifest and SHA-256 checksum list."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "MANIFEST.json"
CHECKSUMS = ROOT / "results" / "CHECKSUMS.sha256"


def included(path: Path) -> bool:
    if not path.is_file() or path in (MANIFEST, CHECKSUMS):
        return False
    return not any(part in {"__pycache__", ".pytest_cache"} for part in path.parts)


files = []
for path in sorted(ROOT.rglob("*")):
    if included(path):
        data = path.read_bytes()
        files.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })

payload = {
    "cycle": "quality_max_microcycle_01",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "status": "complete",
    "scientific_status": "preliminary_non_publishable",
    "artifact_count": len(files),
    "files": files,
}
MANIFEST.write_text(json.dumps(payload, indent=2), encoding="utf-8")
CHECKSUMS.write_text(
    "".join(f"{item['sha256']}  {item['path']}\n" for item in files),
    encoding="utf-8",
)
print(json.dumps({"artifact_count": len(files), "manifest": str(MANIFEST)}, indent=2))

