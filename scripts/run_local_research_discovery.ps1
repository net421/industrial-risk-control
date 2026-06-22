$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$Python = Get-Command python -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1 -ExpandProperty Source
if (-not $Python) { throw "Activate a Python virtual environment or install Python." }
& $Python scripts/run_research_discovery.py --output-root artifacts/research-discovery --pilot-profile ci --fresh
& $Python scripts/validate_research_discovery.py --run-dir artifacts/research-discovery
