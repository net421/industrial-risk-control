# Performance Report

- JIT warm-up/compilation: 3.242793 s
- Pilot reference runtime: 0.211082 s
- Pilot warmed Numba repeat: 0.000289 s
- Pilot warmed speedup: 731.40x
- Confirmation reference runtime: 0.413874 s
- Confirmation warmed Numba repeat: 0.004071 s
- Confirmation warmed speedup: 101.66x
- Correctness tolerance: exact equality of collapse flags and first-passage times
- Seeds: 20260429 pilot; 20260430 confirmation
- Fastmath: disabled
- Persistent Numba cache: disabled for import/direct-execution portability

Input generation is excluded from kernel speedup because both kernels consume
identical pre-generated arrays. This is an infrastructure benchmark, not a
production performance claim.

The warmed kernels complete in milliseconds or less, so timer granularity,
scheduling, and parallel startup can materially affect the ratios. Treat the
speedups as indicative, not stable production benchmark estimates.
