# GitHub Actions Runbook

After authentication and publication:

```bash
gh workflow list
gh run list --limit 10
```

Trigger the small manual smoke:

```bash
gh workflow run smoke-cycle.yml
```

Trigger a ten-minute hosted cloud proof:

```bash
gh workflow run cloud-proof.yml \
  -f max_minutes=10 \
  -f profile=cloud-proof \
  -f fresh_or_resume=fresh \
  -f upload_artifacts=true
```

Trigger bounded discovery:

```bash
gh workflow run research-discovery.yml -f pilot_profile=ci
```

Inspect a run and download compact artifacts:

```bash
gh run list --workflow cloud-proof.yml --limit 5
gh run view RUN_ID --log
gh run download RUN_ID
```

Do not trigger `full-cycle.yml` at 90 minutes merely to duplicate the completed
local proof. Use a cloud/server worker when a new scientific design warrants it.
