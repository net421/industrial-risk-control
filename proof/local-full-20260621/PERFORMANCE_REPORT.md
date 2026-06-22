# Performance Report

- Profile: `full`
- Total trajectories: 50,955,000
- JIT warm-up: 0.883326 s
- Input generation: 4615.232942 s
- Numba simulation: 26.613415 s
- Reference validation: 0.238777 s
- End-to-end elapsed: 5400.300153 s
- Fastmath: disabled
- Parallel RNG inside Numba: disabled
- Batch seeds: deterministic hierarchy recorded in batch_metrics.csv

Input generation and Numba execution are reported separately. This is an
engineering benchmark, not a general hardware performance claim.
