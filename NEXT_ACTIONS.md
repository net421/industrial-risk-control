# Next Actions

1. Run `gh auth login -h github.com` on the local computer.
2. Create and push `net421/industrial-risk-control` using the publish instructions.
3. Wait for automatic CI and CodeQL; inspect their real GitHub statuses.
4. Manually run `smoke-cycle.yml`.
5. Optionally run `cloud-proof.yml` for ten minutes on a hosted runner.
6. Create an AWS/Oracle Ubuntu worker only after the hosted workflows are stable.
7. Enroll a self-hosted runner only with repository and secret protections.
8. Perform live literature verification before any publishability claim.
