$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$Python = Get-Command python -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1 -ExpandProperty Source
if (-not $Python) { throw "Activate a Python virtual environment or install Python." }
& $Python -m industrial_research_lab.cli --profile smoke --output artifacts/local-smoke --fresh
& $Python scripts/validate_portfolio_run.py --run-dir artifacts/local-smoke
