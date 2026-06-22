# Experiment Plan

1. Freeze the model, parameter grid, outcomes, seeds, and stopping policy.
2. Generate deterministic batch seeds outside the parallel kernel.
3. Generate Bernoulli disruption and Poisson-demand arrays outside Numba.
4. Require exact Python-reference and Numba agreement on every configuration.
5. Require fixed-seed input replay on every configuration.
6. Execute pilot and replication seeds independently.
7. Report Wilson intervals and adjacent risk differences.
8. Preserve atomic checkpoints and compact CSV/JSON/Markdown artifacts.
9. Keep CI, cloud-proof, and full profiles operationally distinct.
10. Treat results as preliminary until novelty and external validity are verified.
