# Microcycle Preregistration

**Status:** Frozen before computation. Infrastructure smoke test only.

## Model And Claim

For `C=100`, `X0=50`, `delta=2`, and horizon `T=500`, set
`lambda=(1-p)C-delta` at `p={0.02,0.10,0.20}`. The frozen directional claim is

`P(tau<=500 | p=.02) < P(tau<=500 | p=.10) < P(tau<=500 | p=.20)`.

This concerns disruption-demand composition at equal drift. It is not a claim
that variance alone causally determines collapse.

## Samples And Seeds

- Pilot: 250 trajectories per configuration, seed 20260429.
- Confirmation: 500 trajectories per configuration, seed 20260430.
- No post-generation exclusions.

## Outcomes And Uncertainty

- Primary: collapse probability by period 500.
- Effects: adjacent absolute risk differences.
- Secondary: restricted mean first-passage time with non-collapse coded 501;
  conditional mean collapse time is descriptive.
- Wilson 95% intervals for probabilities.
- Deterministic bootstrap 95% intervals for risk differences.

## Gates

Python and Numba outputs must agree exactly. Pilot adjacent differences must be
positive and at least 0.02; confirmation differences must be positive and retain
the ordering. Confirmation difference `<=0` rejects the claim. Preserved order
with weak pilot effects or broad uncertainty is inconclusive. Backend mismatch
is infrastructure failure.

