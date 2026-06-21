#!/usr/bin/env python
"""Validate portfolio structure, workflow policy, and obvious secret hygiene."""

from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "pyproject.toml",
    "SECURITY.md",
    "docs/ARCHITECTURE.md",
    "docs/REPRODUCIBILITY.md",
    "docs/CI_CD.md",
    ".github/workflows/ci.yml",
    ".github/workflows/smoke-cycle.yml",
    ".github/workflows/full-cycle.yml",
    ".github/workflows/release.yml",
    ".github/workflows/codeql.yml",
)
FORBIDDEN_NAMES = re.compile(
    r"(^|/)(\.env|id_rsa|id_ed25519|credentials.*|.*\.(pem|key))$",
    re.IGNORECASE,
)


def main() -> int:
    errors = []
    for relative in REQUIRED:
        path = ROOT / relative
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"missing or empty: {relative}")

    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    for workflow in workflows:
        try:
            payload = yaml.safe_load(workflow.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"invalid workflow YAML {workflow.name}: {exc}")
            continue
        if not isinstance(payload, dict) or "jobs" not in payload:
            errors.append(f"workflow lacks jobs: {workflow.name}")
        if "permissions" not in payload:
            errors.append(f"workflow lacks explicit permissions: {workflow.name}")

    full_workflow = (ROOT / ".github" / "workflows" / "full-cycle.yml").read_text(encoding="utf-8")
    trigger_block = full_workflow.split("permissions:", 1)[0]
    if "workflow_dispatch:" not in trigger_block:
        errors.append("full-cycle workflow is not manually dispatchable")
    if "schedule:" in trigger_block:
        errors.append("full-cycle workflow must not be scheduled")

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if any(part in {".git", ".venv", "artifacts", "__pycache__"} for part in path.parts):
            continue
        if FORBIDDEN_NAMES.search(relative):
            errors.append(f"potential secret file: {relative}")

    if errors:
        print("REPOSITORY VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPOSITORY VALIDATION PASSED")
    print(f"- workflows parsed: {len(workflows)}")
    print("- full cycle remains manual")
    print("- no obvious secret filenames found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

