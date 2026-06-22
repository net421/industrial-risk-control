# Reproducibility

The simulation uses a deterministic hierarchy of master seed, replication,
configuration, and batch indices. Random arrays are generated outside Numba;
the parallel kernel consumes fixed inputs. Every configuration performs exact
Python-reference comparison and fixed-seed replay.

Run the fast proof:

```bash
python -m pytest
python -m industrial_research_lab.cli --profile ci
python scripts/validate_portfolio_run.py --run-dir artifacts/ci-local
```

Run the local cloud equivalent:

```bash
python -m industrial_research_lab.cli --profile cloud-proof --max-minutes 10
```

The completed 90-minute local proof is documented in
`LOCAL_FULL_RUN_SUMMARY.md`; its compact evidence is under
`proof/local-full-20260621/`. Checkpoint and per-batch files remain untracked.

See `docs/REPRODUCIBILITY.md` for the complete seed and artifact contract.
