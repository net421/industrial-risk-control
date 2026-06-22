# GitHub Actions Runner Notes

GitHub-hosted runners should execute only bounded jobs:

- automatic CI profile;
- manual smoke;
- ten-minute cloud proof;
- inexpensive discovery pilot;
- weekly validation;
- CodeQL and release packaging.

The full wrapper defaults to 15 minutes and manual dispatch. A 90-minute run must
be an intentional choice and is normally better on a local or AWS/Oracle worker.
Upload compact reports only; checkpoints and batch metrics remain local unless
needed for recovery.
