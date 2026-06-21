# Quality-Max Microcycle Report

## Outcome

**Pipeline status:** passed after one repaired infrastructure defect.

**Scientific status:** preliminary, non-novel, non-publishable smoke evidence.

## Completed Stages

- Protocol and state initialization
- Five-candidate local-corpus discovery and ranking
- Mathematical formalization and preregistration
- Pure Python reference and Numba implementation
- Five unit and invariant tests
- Pilot and independent-seed confirmation
- Wilson and deterministic bootstrap uncertainty
- Computation/reproducibility and statistical/skeptical audits
- Industrial and portfolio integration

## Infrastructure Finding

The initial execution exposed a Numba cache module-name mismatch between test
imports and direct script execution. Persistent cache was disabled for this
dual-use harness, after which all gates passed. Fresh fixed-seed regeneration
and uncertainty-aware promotion checks were added following independent audit.

## Compact Result

Collapse probability increased across all three tested configurations under both
seeds. Adjacent confirmation differences were 0.262 and 0.114, with bootstrap
95% intervals excluding zero. Reference and Numba outputs matched exactly.
Local computation, including compilation and both phases, took about five
seconds on four logical CPU threads.

## Boundary

This run validates the workflow. It does not establish novelty, causal isolation
of variance, general monotonicity, independent scientific replication, an
optimal policy, or a publishable result.

