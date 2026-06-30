# Cloud Proof Evidence and Persistent Storage Pilot

This note records the hosted GitHub Actions cloud proof completed for the
industrial-risk-control pipeline and proposes the next storage step for a
cloud-only development and evidence workflow.

## Why This Exists

The repository is being used as a public engineering proof of reproducible
research automation: code, workflows, validation gates, and compact artifacts are
run through GitHub Actions to demonstrate practical development capability.

GitHub Actions is appropriate for the execution proof and short-lived debugging
artifacts. It should not be the only permanent store for research outputs,
because Actions artifacts expire by design.

## Completed Hosted Run

- Workflow: `cloud-proof.yml`
- Run: `28471733458`
- URL: <https://github.com/net421/industrial-risk-control/actions/runs/28471733458>
- Branch: `main`
- Commit: `b1eb8a0ead9c8f79df5861cb1a98da8bcef0d318`
- Job: `cloud-proof`
- Status: `success`
- Trigger: manual `workflow_dispatch`
- Profile: `cloud-proof`
- Budget: 10 minutes
- Stop reason: `time_budget`
- Artifact: `cloud-proof-28471733458-1`
- Artifact id: `7992170424`
- Artifact digest: `sha256:8febc451de90f59309052bae6ab48ee0c0536b805117f5ccfb3dd7d3a9d849b0`
- Artifact created: `2026-06-30T20:02:39Z`
- Artifact expires: `2026-07-14T20:02:38Z`

## Result Summary

The hosted run completed the bounded proof and uploaded compact evidence files.
The validation gate passed.

Observed summary values:

- Total trajectories: `14,297,500`
- Elapsed time: `600.084948874` seconds
- Infrastructure pass: `true`
- Reference and Numba exact agreement: `true`
- Fixed-seed replay exact: `true`
- Configurations with data: `10/10`
- Adjacent risk differences: positive across both independent seeds

The result strengthens the engineering evidence that the deterministic pipeline
can run on hosted cloud infrastructure and produce reproducible, checksummed
artifacts. It remains an engineering proof, not publication-ready scientific
evidence.

## Artifact Contents

The GitHub Actions artifact contains the compact output set:

- `summary.json`
- `summary.csv`
- `VALIDATION_REPORT.md`
- `PERFORMANCE_REPORT.md`
- `RUN_REPORT.md`
- `CHECKSUMS.sha256`

## Current Storage Boundary

GitHub Actions artifacts are useful for short-term inspection and CI evidence,
but they expire. This run's artifact expires on `2026-07-14T20:02:38Z`.

For durable research evidence, completed runs should be copied to deliberate
object storage after validation.

## Proposed Cloud Storage Pilot

Use an object store as the canonical long-term run archive while keeping GitHub
as the development and execution proof surface.

Recommended targets:

1. Cloudflare R2 for low-cost artifact storage.
2. AWS S3 for the most standard cloud-native option.
3. Oracle Cloud Object Storage if Oracle compute is also used for longer runs.
4. Azure Blob Storage or Google Cloud Storage if those environments become the
   preferred cloud platform.

Recommended object layout:

```text
industrial-risk-control-runs/
  runs/
    2026-06-30_cloud-proof_28471733458/
      artifact.zip
      summary.json
      summary.csv
      VALIDATION_REPORT.md
      PERFORMANCE_REPORT.md
      RUN_REPORT.md
      CHECKSUMS.sha256
      RUN_METADATA.json
  indexes/
    RUN_INDEX.json
```

`RUN_METADATA.json` should capture at least:

```json
{
  "repository": "net421/industrial-risk-control",
  "workflow": "cloud-proof.yml",
  "run_id": "28471733458",
  "branch": "main",
  "commit": "b1eb8a0ead9c8f79df5861cb1a98da8bcef0d318",
  "profile": "cloud-proof",
  "status": "success",
  "artifact_name": "cloud-proof-28471733458-1",
  "artifact_digest": "sha256:8febc451de90f59309052bae6ab48ee0c0536b805117f5ccfb3dd7d3a9d849b0",
  "storage_uri": "s3://industrial-risk-control-runs/runs/2026-06-30_cloud-proof_28471733458/artifact.zip"
}
```

## Suggested Workflow Extension

Add an optional upload stage after validation:

1. Run `cloud-proof.yml` or a later `full-cycle.yml` profile.
2. Validate compact artifacts and checksums.
3. Package the run directory as a ZIP.
4. Upload the ZIP and selected compact reports to object storage.
5. Append or regenerate `RUN_INDEX.json`.
6. Keep the GitHub Actions artifact as the temporary UI copy.

The upload stage should be gated by repository secrets, for example:

- `STORAGE_BUCKET`
- `STORAGE_ENDPOINT_URL`
- `STORAGE_ACCESS_KEY_ID`
- `STORAGE_SECRET_ACCESS_KEY`

For AWS S3, GitHub OIDC should be preferred over long-lived keys. For R2 or other
S3-compatible storage, scoped credentials should be used with least privilege.

## Portfolio Framing

This design keeps GitHub focused on what it is good at for a development
portfolio:

- reproducible code execution;
- CI/CD workflow design;
- validation gates;
- traceable run links;
- compact evidence artifacts;
- clear separation between engineering proof and scientific claims.

The persistent object store becomes the durable evidence archive for larger
cloud-only runs, including future full-cycle executions that should not depend on
any local machine.
