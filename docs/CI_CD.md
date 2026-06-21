# CI/CD Design

## Continuous Integration

`ci.yml` runs unit tests and a deterministic CI profile across supported Python
versions. It validates generated artifacts before upload.

`codeql.yml` performs Python security analysis. Dependabot proposes updates for
Python and GitHub Actions dependencies.

## Controlled Research Automation

`smoke-cycle.yml` runs manually and on a weekly validation schedule. It is small
enough for hosted runners and never promotes a scientific claim automatically.

`full-cycle.yml` is manual only. It uses a bounded time input, preserves a
checkpoint, validates the completed run, and uploads compact artifacts.

## Continuous Delivery

`release.yml` packages the exact Git tree on version tags, generates a checksum,
and creates a GitHub release. A future server deployment should consume a tagged
release, create a fresh virtual environment, run validation, and require manual
approval before a full cycle.

The deployment unit is validated code and configuration, not an automatically
accepted scientific conclusion.

