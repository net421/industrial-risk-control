# CI/CD Design

## Continuous Integration

`ci.yml` runs unit tests and a deterministic CI profile across supported Python
versions. It validates generated artifacts before upload.

`codeql.yml` performs Python security analysis. Dependabot proposes updates for
Python and GitHub Actions dependencies.

## Controlled Research Automation

`smoke-cycle.yml` runs manually. `weekly-validation.yml` runs the lightweight CI
profile and validators on a schedule; it never launches expensive research.

`cloud-proof.yml` is a manual, server-like hosted proof with a ten-minute default
and compact-only artifact uploads.

`full-cycle.yml` is manual only and defaults to a safe 15-minute cloud-proof
profile. It accepts a controlled self-hosted runner mode for advanced use.

`research-discovery.yml` is manual and produces gap-map, hypothesis, experiment,
claim, validation, portfolio, paper-opportunity, and next-action artifacts. It
does not establish novelty without live literature comparison.

## Continuous Delivery

`release.yml` packages the exact Git tree on version tags, generates a checksum,
and creates a GitHub release. A future server deployment should consume a tagged
release, create a fresh virtual environment, run validation, and require manual
approval before a full cycle.

The deployment unit is validated code and configuration, not an automatically
accepted scientific conclusion.
