#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
MINUTES="${1:-10}"
python -m industrial_research_lab.cli --profile cloud-proof --max-minutes "$MINUTES" --output artifacts/local-cloud-proof --fresh
python scripts/validate_portfolio_run.py --run-dir artifacts/local-cloud-proof
