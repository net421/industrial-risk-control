# AWS Or Oracle VM Notes

An Ubuntu VM can serve as a manual execution worker without becoming a GitHub
runner. Clone a tagged or reviewed revision, create a virtual environment, run
validation, then start a bounded profile inside `tmux` or a systemd service.

Recommended placement:

- GitHub-hosted Actions: tests, CI profile, smoke, short cloud proof, security scan.
- AWS/Oracle VM: long confirmation runs, checkpoint resume, scheduled validation.
- Local computer: development and fallback execution.

The VM requires outbound HTTPS and SSH administration only. Do not open notebook,
database, or dashboard ports. Transfer compact summaries rather than raw arrays.
