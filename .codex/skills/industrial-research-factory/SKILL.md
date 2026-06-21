---
name: industrial-research-factory
description: Run bounded, gated, reproducible research cycles for near-critical industrial stochastic systems. Use when Codex must coordinate literature-gap screening, hypothesis ranking, mathematical formalization, Python/Numba pilots, replication, statistical audit, skeptical review, and portfolio reporting from a CYCLE_SPEC.yaml protocol.
---

# Industrial Research Factory

## Execute The Cycle

1. Read `AGENTS.md`, `protocol/CYCLE_SPEC.yaml`, and `protocol/RUN_STATE.json`.
2. Treat the primary thread as Integration Agent and sole shared-file owner.
3. Run Literature/Novelty as a read-only audit while the primary Integration
   role performs the Industrial/Journal Fit assessment.
4. Rank candidates and freeze one falsifiable claim before computation.
5. Run Theory/Experiment Design as a read-only formalization audit.
6. Have Computation/Reproducibility propose code and tests; Integration writes and executes them.
7. Run Statistics/Skeptical Review only from compact CSV/JSON summaries.
8. Integrate required reports and validate the artifact contract.
9. Update `RUN_STATE.json` after every gate.

## Enforce Boundaries

- Label microcycle evidence preliminary and non-publishable.
- Reject individual hypotheses without blocking the cycle.
- Reserve `BLOCKER_REPORT.md` for systemic infrastructure failure.
- Do not claim novelty without verified external literature comparison.
- Do not run multiple heavy local simulations concurrently.
- Do not edit outside the cycle workspace.

## Compute Correctly

- Profile or time before optimizing.
- Compare a Python/NumPy reference with Numba on identical inputs.
- Use `parallel=True` and `prange` only for independent trajectories.
- Generate random inputs or child seeds outside parallel kernels.
- Keep pandas, plotting, file I/O, and reports outside Numba.
- Record warm-up separately from steady-state runtime.
- Accept Numba only when results meet the frozen tolerance.

## Validate Outputs

Read `references/artifact-contract.md` before final integration. Run
`scripts/validate_cycle.py` and do not mark the cycle complete unless it passes.
