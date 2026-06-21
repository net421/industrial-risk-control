#!/usr/bin/env python
"""Dependency-free validator for an industrial research cycle workspace."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "protocol" / "CYCLE_SPEC.yaml"


def output_paths(text: str) -> list[str]:
    paths = []
    inside = False
    for line in text.splitlines():
        if line == "outputs:":
            inside = True
            continue
        if inside and line and not line.startswith("  "):
            break
        if inside:
            match = re.match(r"^  [a-zA-Z0-9_]+:\s*(.+?)\s*$", line)
            if match:
                paths.append(match.group(1))
    return paths


errors = []
if not SPEC.exists():
    errors.append("missing protocol/CYCLE_SPEC.yaml")
else:
    for relative in output_paths(SPEC.read_text(encoding="utf-8")):
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing {relative}")
        elif path.stat().st_size == 0:
            errors.append(f"empty {relative}")

for relative in (
    "protocol/RUN_STATE.json",
    "results/compact_summary.json",
    "results/MANIFEST.json",
):
    path = ROOT / relative
    if path.exists():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON {relative}: {exc}")

state_path = ROOT / "protocol" / "RUN_STATE.json"
summary_path = ROOT / "results" / "compact_summary.json"
if state_path.exists() and json.loads(state_path.read_text(encoding="utf-8")).get("status") != "complete":
    errors.append("RUN_STATE status is not complete")
if summary_path.exists() and not json.loads(summary_path.read_text(encoding="utf-8")).get("infrastructure_pass"):
    errors.append("compact summary infrastructure_pass is not true")

skill = ROOT / ".codex" / "skills" / "industrial-research-factory" / "SKILL.md"
if skill.exists():
    text = skill.read_text(encoding="utf-8")
    if not re.match(r"^---\s*\nname: industrial-research-factory\s*\ndescription: .+?\n---", text):
        errors.append("skill frontmatter is invalid")
else:
    errors.append("missing project skill")

if errors:
    print("CYCLE VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("CYCLE VALIDATION PASSED")
print(f"- required outputs: {len(output_paths(SPEC.read_text(encoding='utf-8')))}")
print("- JSON documents: valid")
print("- infrastructure gate: passed")
print("- skill frontmatter: valid")

