#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python -m pytest -q
python scripts/validate_repository.py
python -m industrial_research_lab.cli --profile ci --output artifacts/local-ci --fresh
python scripts/validate_portfolio_run.py --run-dir artifacts/local-ci
