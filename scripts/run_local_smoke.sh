#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python -m industrial_research_lab.cli --profile smoke --output artifacts/local-smoke --fresh
python scripts/validate_portfolio_run.py --run-dir artifacts/local-smoke
