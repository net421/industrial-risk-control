#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
MINUTES="${1:-90}"
echo "Manual full run requested for ${MINUTES} minutes."
python -m industrial_research_lab.cli --profile full --max-minutes "$MINUTES" --output artifacts/local-full
python scripts/validate_portfolio_run.py --run-dir artifacts/local-full
