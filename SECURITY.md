# Security Policy

- Never commit credentials, SSH keys, cloud tokens, or `.env` files.
- Treat pull-request code as untrusted.
- Do not expose a persistent self-hosted runner to unreviewed public workflows.
- Use least-privilege GitHub workflow permissions.
- Keep full research runs manual; scheduled automation is validation-only.
- Report suspected credential exposure privately and rotate affected secrets.

This project does not require inbound network services or public notebooks.

