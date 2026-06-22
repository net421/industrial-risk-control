# Automation Proof

## 1. Already Run Locally

- Fast unit and workflow validation.
- CI and smoke profiles.
- One 90-minute full profile on 2026-06-21.
- 50,955,000 trajectories across 20 seed/configuration combinations.
- Exact Python/Numba agreement, fixed-seed replay, and checksum validation.
- One ten-minute local cloud-proof equivalent with 6,667,500 trajectories.
- One bounded local discovery automation cycle producing every declared stage artifact.

All of these proofs ran on the local Windows computer, not GitHub Actions. The
discovery cycle reused a local corpus baseline; it did not perform a live
systematic literature search or establish publishability.

## 2. Actually Run On GitHub Actions

None yet. GitHub CLI authentication is expired and this local repository has no
remote. Workflow files being present is not evidence that Actions executed.

## 3. Prepared But Not Yet Run On GitHub

- Automatic `ci.yml` on push and pull requests.
- Manual `smoke-cycle.yml`.
- Manual `cloud-proof.yml` with a ten-minute default.
- Manual `full-cycle.yml` with a safe short default and server guidance.
- Manual `research-discovery.yml`.
- Scheduled and manual `weekly-validation.yml`.
- `codeql.yml`, dependency updates, and tag-based releases.

## 4. Requires Manual GitHub Authentication

Run `gh auth login -h github.com`, verify with `gh auth status`, then follow
`GITHUB_PUBLISH_INSTRUCTIONS.md`. Publishing and workflow triggering require the
human account owner.

## 5. Requires A Future Server Or Self-Hosted Runner

Long recurring full runs are better placed on a controlled AWS/Oracle VM. The
repository includes Ubuntu, systemd, Ansible, and self-hosted-runner notes, but no
server or runner has been configured.

## Automation Boundary

Code installation, testing, deterministic computation, checkpoints, compact
reports, manifests, checksums, and workflow artifact upload are automated.
Novelty decisions, full-run approval, publication claims, releases, secrets, and
server enrollment remain human-controlled.

Validate compact proof files with their `CHECKSUMS.sha256` and
`PROOF_MANIFEST.json`. Generated run artifacts can be inspected through
`summary.json`, `summary.csv`, and the three Markdown reports without reading
large checkpoints or raw random arrays.
