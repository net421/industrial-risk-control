# Reproducibility

Each batch seed is derived from:

```text
master seed + replication index + configuration index + batch index
```

Uniform disruption draws and Poisson demand draws use separate child streams.
The parallel Numba kernel contains no random-number generation, so scheduling
does not alter inputs. The first batch of every configuration is replayed and
checked against the Python reference.

The run directory records:

- effective profile and time budget
- software and hardware metadata
- every batch seed and timing
- atomic checkpoint state
- compact CSV and JSON summaries
- validation and performance reports
- file manifest and SHA-256 checksums

Time-budgeted runs may complete different numbers of batches on different
hardware. Reproduce an exact workload by retaining the checkpoint and completed
batch count; reproduce the operational policy by retaining the time budget.

