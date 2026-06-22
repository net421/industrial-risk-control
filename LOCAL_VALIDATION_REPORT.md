# Local Validation Report

**Status:** PASS
**Date:** 2026-06-21
**Execution location:** Local Windows computer

## Passed Commands And Gates

- `python -m pytest -q`: 13 tests passed.
- `python scripts/validate_repository.py`: 8 workflows parsed; full cycle manual;
  no obvious secret filenames.
- CI profile: 192 trajectories; infrastructure and checksums passed.
- Smoke profile: 12,000 trajectories; infrastructure and checksums passed.
- Cloud-proof equivalent: 6,667,500 trajectories in 10.00 minutes; passed.
- Full profile: 50,955,000 trajectories in 90.005 minutes; passed.
- Research-discovery automation: every declared stage artifact produced and validated.
- Original factory validator: 16 required outputs passed.
- PowerShell fallback scripts: CI, smoke, cloud-proof wrapper, and discovery passed.
- Bash fallback scripts: syntax validated with Git Bash.
- Workflow YAML: all files parsed locally.
- Compact proof manifest and SHA-256 files: passed.

## Evidence Boundaries

- The 90-minute full run was performed once locally and was not repeated.
- The cloud-proof result is a local equivalent, not a GitHub-hosted run.
- GitHub Actions have not run because `gh` authentication is expired.
- The discovery automation completed locally from a local-corpus baseline; a live
  systematic literature comparison and publishability assessment did not occur.
- No AWS/Oracle VM or self-hosted runner has been configured.
