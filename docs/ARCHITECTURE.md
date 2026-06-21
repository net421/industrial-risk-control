# Architecture

## Layers

1. **Protocol:** frozen claims, seeds, grids, tests, and stopping rules.
2. **Model:** a readable Python reference and a parallel Numba implementation.
3. **Orchestration:** deterministic round-robin batches with atomic checkpoints.
4. **Evidence:** Wilson intervals, compact summaries, and bounded interpretation.
5. **Integrity:** manifests, SHA-256 checksums, and independent validation.
6. **Delivery:** GitHub Actions artifacts, versioned releases, and Linux examples.

## Failure Model

- A reference/Numba mismatch fails the run.
- A fixed-seed replay mismatch fails the run.
- Missing configurations fail the infrastructure gate.
- Interrupted runs preserve their checkpoint and may resume.
- A time-budget stop occurs only between complete deterministic batches.
- Scientific claims are never promoted merely because engineering gates pass.

## Portability

The same `industrial-lab` CLI runs on Windows, GitHub-hosted Ubuntu, and a future
Ubuntu batch server. Generated artifacts do not depend on Codex reasoning during
computation.

