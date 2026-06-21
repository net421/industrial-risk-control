# Server Deployment Examples

These files prepare the project for a future Ubuntu batch host. They are examples
and are not executed automatically.

- `ubuntu/bootstrap.sh`: creates a virtual environment and validates the repo.
- `ansible/playbook.yml`: idempotent Ubuntu provisioning and repository checkout.
- `systemd/`: validation-only timer and manual full-cycle service examples.

Keep the GitHub-hosted CI path as the trust gate. Do not expose a persistent
self-hosted runner to unreviewed public pull requests.

