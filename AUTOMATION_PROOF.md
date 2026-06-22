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

- Automatic CI passed on final commit `e6774d0`: run `27932818188`.
- CodeQL v4 passed on final commit `e6774d0`: run `27932818230`.
- The manual smoke cycle passed all tests, ran deterministic computation,
  validated outputs, and uploaded artifact `smoke-cycle-27932826236` with SHA-256
  digest `a72b48d61c306da78d704fc8982688681162fc310d4e3a25a016d2fad2a3757f`.
- The bounded Research Discovery workflow passed: run `27932618863`.

## 3. Prepared But Not Yet Run On GitHub

- Manual `cloud-proof.yml` with a ten-minute default.
- Manual `full-cycle.yml` with a safe short default and server guidance.
- Scheduled and manual `weekly-validation.yml`.
- Tag-based releases.

## 4. Public Repository

The source and workflow history are public at
`https://github.com/net421/industrial-risk-control`.

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
