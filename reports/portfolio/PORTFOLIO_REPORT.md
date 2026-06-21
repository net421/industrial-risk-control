# Portfolio Report

## Decision

The microcycle infrastructure passes. The selected claim receives
`preliminary_supported` status under the frozen smoke-test rules and should be
considered only for a larger confirmatory design.

## Evidence

At fixed mean drift `delta=2`, estimated collapse probabilities increased across
the tested disruption-demand compositions:

| Phase | p=.02 | p=.10 | p=.20 | Adjacent differences |
|---|---:|---:|---:|---|
| Pilot, n=250 | 0.416 | 0.708 | 0.792 | 0.292, 0.084 |
| Confirmation, n=500 | 0.442 | 0.704 | 0.818 | 0.262, 0.114 |

Confirmation bootstrap intervals were `[0.204, 0.320]` and `[0.062, 0.164]`.
Python and Numba outputs agreed exactly, and fresh regeneration from each fixed
seed reproduced the inputs and outputs.

## Portfolio Interpretation

The pipeline exercised protocol freezing, local-corpus discovery, hypothesis
ranking, formalization, reference/Numba computation, pilot, confirmation,
uncertainty, skeptical review, and integration. The evidence does not establish
causality, general monotonicity, novelty, independent replication, industrial
policy value, or publication readiness.

