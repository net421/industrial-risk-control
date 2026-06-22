# Self-Hosted Runner Notes

A future AWS/Oracle VM may register as a GitHub Actions self-hosted runner, but a
manual worker is safer for the first deployment.

Before enrollment:

1. Keep the repository private during initial runner testing or tightly restrict PR workflows.
2. Use a dedicated unprivileged Linux account.
3. Do not expose cloud credentials to untrusted pull-request jobs.
4. Prefer ephemeral runners for untrusted or autoscaled workloads.
5. Label the runner, for example `self-hosted`, `linux`, `arm64`, `research`.
6. Preserve runner logs outside disposable workspaces.
7. Use GitHub Environments and manual approval for long compute.

The prepared `full-cycle.yml` accepts `self-hosted` as a manual run mode. No
self-hosted runner has been configured or tested yet.
