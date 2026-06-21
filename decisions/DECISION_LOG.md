# Decision Log

## Gate A: Discovery

- Reviewed five local sources; external novelty was not assessed.
- Generated and scored five bounded candidates on a 1-5 scale.
- Selected the fixed-slack disruption-composition claim for feasibility and
  exact reference/Numba comparability, not because it is known to be novel.
- Deferred policy-miscalibration and persistence hypotheses because their
  additional kernels would exceed the 20-minute infrastructure budget.

## Gate B: Formalization

- Narrowed the selected candidate to a finite-horizon composition claim.
- Fixed C=100, X0=50, delta=2, T=500, three p values, both sample sizes,
  seeds, outcomes, uncertainty methods, and decision thresholds.
- Prohibited causal variance, novelty, general monotonicity, and publication claims.

## Pilot Infrastructure Repair

- Initial direct execution encountered a Numba cache module-name mismatch because
  tests imported `scripts.run_micro_experiment` while execution used `__main__`.
- Disabled persistent caching for this dual-use smoke harness and retained JIT
  warm-up timing. Production kernels should use stable installed-module imports.

## Gates C And D

- Three unit tests passed before the pilot.
- Exact Python/Numba and fixed-input reproducibility gates passed for both seeds.
- Pilot and confirmation preserved the preregistered ordering.
- Accepted `preliminary_supported` only under smoke rules.
- Explicitly rejected novelty, independent-replication, causal-variance,
  general-monotonicity, and publication-ready interpretations.

## Audit Hardening

- Added fresh fixed-seed input regeneration and output comparison.
- Enforced positive confirmation bootstrap lower bounds in promotion logic.
- Renamed the secondary time statistic to make its T+1 censoring convention explicit.
