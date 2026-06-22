# GitHub Publish Status

The repository is published at
`https://github.com/net421/industrial-risk-control` and tracks `origin/main`.

## Verification

From this repository directory, run:

```powershell
gh auth status
git remote -v
gh workflow list
gh run list --workflow ci.yml --limit 5
```

Never paste an authentication token into a repository file, log, or chat message.
