# GitHub Automation Report

## Connection Status

- Local Git repository: yes
- Current branch: `main`
- Root commit: `f748b94`
- GitHub CLI: installed (`2.93.0`)
- GitHub authentication: expired for `net421`
- GitHub remote: not configured
- Repository pushed: no
- GitHub Actions executed: no

## Workflow Inventory

| Workflow | Trigger | Cost boundary | Execution status |
|---|---|---|---|
| `ci.yml` | push, pull request | Fast CI profile | Prepared, not run on GitHub |
| `smoke-cycle.yml` | manual | Small deterministic smoke | Prepared, not run on GitHub |
| `cloud-proof.yml` | manual | Ten-minute default | Prepared, not run on GitHub |
| `full-cycle.yml` | manual | Fifteen-minute safe default | Prepared, not run on GitHub |
| `research-discovery.yml` | manual | CI/smoke pilot only | Prepared, not run on GitHub |
| `weekly-validation.yml` | weekly, manual | Validation only | Prepared, not run on GitHub |
| `codeql.yml` | push, PR, weekly | Static security analysis | Prepared, not run on GitHub |
| `release.yml` | version tag | Package and release | Prepared, not run on GitHub |

No workflow status is promoted until a GitHub run completes successfully.

## Local Automation Evidence

- CI fallback: passed.
- Smoke fallback: passed with 12,000 trajectories.
- Cloud-proof equivalent: passed in 10.00 minutes with 6,667,500 trajectories.
- Full local proof: passed in 90.005 minutes with 50,955,000 trajectories.
- Discovery automation: all declared stage artifacts produced and validated;
  live literature verification and publishability remain incomplete.
