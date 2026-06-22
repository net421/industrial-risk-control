param([double]$MaxMinutes = 90)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$Python = Get-Command python -All -ErrorAction SilentlyContinue | Where-Object { $_.Source -notlike '*WindowsApps*' } | Select-Object -First 1 -ExpandProperty Source
if (-not $Python) { throw "Activate a Python virtual environment or install Python." }
Write-Host "Manual full run requested for $MaxMinutes minutes."
& $Python -m industrial_research_lab.cli --profile full --max-minutes $MaxMinutes --output artifacts/local-full
& $Python scripts/validate_portfolio_run.py --run-dir artifacts/local-full
