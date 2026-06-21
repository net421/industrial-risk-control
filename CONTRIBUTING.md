# Contributing

1. Create a focused branch from `main`.
2. Freeze claim and experiment changes before generating results.
3. Add or update tests for every numerical or artifact-contract change.
4. Run `pytest -q` and the `ci` profile locally.
5. Keep generated `artifacts/` out of commits; attach them to workflow runs.
6. Describe scientific limitations and engineering impact separately in the PR.

Do not weaken exact reference/Numba agreement, seed replay, or checksum gates to
make a workflow pass.

