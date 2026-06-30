# Next Actions

1. Preserve the completed hosted proof evidence from `cloud-proof.yml` run `28471733458` before the GitHub Actions artifact expires on `2026-07-14`.
2. Pilot persistent object storage for validated cloud-run artifacts; see `docs/cloud-proof-storage-pilot.md`.
3. Extend `cloud-proof.yml` or a follow-up workflow with an optional post-validation upload step to S3-compatible storage.
4. Create an AWS/Oracle Ubuntu worker only when recurring long runs are needed.
5. Enroll a self-hosted runner only with repository and secret protections.
6. Perform live literature verification before any publishability claim.
7. Create a version tag only when a release artifact is intentionally required.
