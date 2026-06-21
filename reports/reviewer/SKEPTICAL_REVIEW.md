# Skeptical Review

## Gate Recommendation

Pass Gate D for infrastructure validation and preliminary directional support
only. The status `preliminary_supported` follows the frozen smoke-test rules.

## Evidence

- Pilot adjacent risk differences: 0.292 and 0.084; both exceed 0.02.
- Confirmation differences: 0.262 and 0.114; ordering is preserved.
- Confirmation bootstrap 95% intervals: [0.204, 0.320] and [0.062, 0.164].
- Python and Numba outputs agree exactly under both seeds.
- Fixed-input repeated Numba runs are identical.

## Objections And Limits

- The confirmation changes seed and sample size; it is not an independent implementation.
- Three points do not establish general monotonicity.
- Changing p also changes higher moments and demand/disruption composition.
- The second pilot interval had a lower bound of only 0.008.
- Bootstrap intervals use 1,000 deterministic percentile resamples and are descriptive.
- Kernel timings are extremely short and exclude input generation; speedups are indicative.
- Novelty, causal attribution, and publication readiness are not established.

