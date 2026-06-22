# GitHub Publish Instructions

Publication is blocked only by expired GitHub CLI authentication.

From this repository directory, run:

```powershell
gh auth login -h github.com
gh auth status
gh repo create industrial-risk-control --public --source . --remote origin --push
```

Choose HTTPS and browser-based authentication when prompted. Never paste the
authentication token into a repository file or chat message.

If `net421/industrial-risk-control` already exists, use:

```powershell
git remote add origin https://github.com/net421/industrial-risk-control.git
git push -u origin main
```

After pushing, verify:

```powershell
git remote -v
gh workflow list
gh run list --workflow ci.yml --limit 5
```

The push should trigger CI and CodeQL. Do not report them as passed until their
GitHub run statuses are successful.
