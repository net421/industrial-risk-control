#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m pytest -q
python scripts/validate_repository.py
python -m industrial_research_lab.cli --profile ci --output artifacts/ci-validation --fresh
python scripts/validate_portfolio_run.py --run-dir artifacts/ci-validation
python .codex/skills/industrial-research-factory/scripts/validate_cycle.py
