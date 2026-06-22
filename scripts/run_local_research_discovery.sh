#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
python scripts/run_research_discovery.py --output-root artifacts/research-discovery --pilot-profile ci --fresh
python scripts/validate_research_discovery.py --run-dir artifacts/research-discovery
