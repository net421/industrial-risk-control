#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$HOME/industrial-risk-control}"
cd "$ROOT"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
mkdir -p artifacts logs
bash scripts/run_validation_only.sh
