# Selected Micro-Experiment

1. Generate independent trajectory child seeds outside computational kernels.
2. Pre-generate Bernoulli uniforms and Poisson demands for each configuration.
3. Run pure Python and warmed Numba kernels on identical arrays.
4. Require exact agreement in collapse indicators and first-passage times.
5. Repeat the Numba calculation to verify fixed-seed reproducibility.
6. Run pilot and confirmation seeds separately.
7. Write compact CSV/JSON summaries; keep raw random arrays in memory only.
8. Compute Wilson intervals, deterministic bootstrap intervals, and benchmark
   compilation separately from warmed runtime.

