.PHONY: install test ci smoke full validate

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

ci:
	python -m industrial_research_lab.cli --profile ci --output artifacts/ci-local --fresh
	python scripts/validate_portfolio_run.py --run-dir artifacts/ci-local

smoke:
	python -m industrial_research_lab.cli --profile smoke --output artifacts/smoke-local --fresh
	python scripts/validate_portfolio_run.py --run-dir artifacts/smoke-local

full:
	python -m industrial_research_lab.cli --profile full --max-minutes 90 --output artifacts/full-local-proof --fresh

validate:
	python scripts/validate_portfolio_run.py --run-dir artifacts/full-local-proof
