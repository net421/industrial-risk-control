#!/usr/bin/env python
"""Run the frozen fixed-slack first-passage micro-experiment."""

from __future__ import annotations

import csv
import json
import math
import os
import platform
import time
from pathlib import Path

import numba
import numpy as np
from numba import njit, prange


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
VALIDATION = RESULTS / "validation"
P_VALUES = (0.02, 0.10, 0.20)
C = 100
X0 = 50
DELTA = 2.0
HORIZON = 500


def simulate_reference(uniforms, demands, p, capacity=C, x0=X0):
    n_runs, horizon = uniforms.shape
    taus = np.full(n_runs, horizon + 1, dtype=np.int64)
    collapsed = np.zeros(n_runs, dtype=np.uint8)
    for i in range(n_runs):
        inventory = x0
        for t in range(horizon):
            production = 0 if uniforms[i, t] < p else capacity
            inventory += production - int(demands[i, t])
            if inventory <= 0:
                taus[i] = t + 1
                collapsed[i] = 1
                break
    return taus, collapsed


# Persistent cache is disabled because this smoke script is both imported by
# tests and executed directly; Numba otherwise records incompatible module names.
@njit(parallel=True, cache=False, fastmath=False)
def simulate_numba(uniforms, demands, p, capacity, x0):
    n_runs, horizon = uniforms.shape
    taus = np.full(n_runs, horizon + 1, dtype=np.int64)
    collapsed = np.zeros(n_runs, dtype=np.uint8)
    for i in prange(n_runs):
        inventory = x0
        for t in range(horizon):
            production = 0 if uniforms[i, t] < p else capacity
            inventory += production - demands[i, t]
            if inventory <= 0:
                taus[i] = t + 1
                collapsed[i] = 1
                break
    return taus, collapsed


def generate_inputs(n_runs, horizon, lam, seed_sequence):
    uniforms = np.empty((n_runs, horizon), dtype=np.float64)
    demands = np.empty((n_runs, horizon), dtype=np.int16)
    for i, child in enumerate(seed_sequence.spawn(n_runs)):
        rng = np.random.default_rng(child)
        uniforms[i] = rng.random(horizon)
        demands[i] = rng.poisson(lam, horizon)
    return uniforms, demands


def wilson_interval(successes, total, z=1.959963984540054):
    p = successes / total
    denominator = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total**2)) / denominator
    return center - radius, center + radius


def bootstrap_difference_ci(low, high, seed, draws=1000):
    rng = np.random.default_rng(seed)
    estimates = np.empty(draws, dtype=np.float64)
    for i in range(draws):
        low_sample = low[rng.integers(0, low.size, low.size)]
        high_sample = high[rng.integers(0, high.size, high.size)]
        estimates[i] = high_sample.mean() - low_sample.mean()
    return tuple(float(x) for x in np.quantile(estimates, [0.025, 0.975]))


def warm_numba():
    uniforms = np.full((4, 8), 0.5, dtype=np.float64)
    demands = np.full((4, 8), 80, dtype=np.int16)
    started = time.perf_counter()
    simulate_numba(uniforms, demands, 0.1, C, X0)
    return time.perf_counter() - started


def run_phase(label, n_runs, seed):
    rows = []
    collapse_vectors = []
    total_reference = 0.0
    total_numba = 0.0
    total_repeat = 0.0
    total_generation = 0.0
    exact_all = True
    reproducible_all = True
    config_sequences = np.random.SeedSequence(seed).spawn(len(P_VALUES))
    replay_sequences = np.random.SeedSequence(seed).spawn(len(P_VALUES))

    for p, sequence, replay_sequence in zip(P_VALUES, config_sequences, replay_sequences):
        lam = (1.0 - p) * C - DELTA
        started = time.perf_counter()
        uniforms, demands = generate_inputs(n_runs, HORIZON, lam, sequence)
        total_generation += time.perf_counter() - started

        started = time.perf_counter()
        ref_taus, ref_collapsed = simulate_reference(uniforms, demands, p)
        reference_seconds = time.perf_counter() - started
        total_reference += reference_seconds

        started = time.perf_counter()
        nb_taus, nb_collapsed = simulate_numba(uniforms, demands, p, C, X0)
        numba_seconds = time.perf_counter() - started
        total_numba += numba_seconds

        started = time.perf_counter()
        repeat_taus, repeat_collapsed = simulate_numba(uniforms, demands, p, C, X0)
        repeat_seconds = time.perf_counter() - started
        total_repeat += repeat_seconds

        replay_uniforms, replay_demands = generate_inputs(
            n_runs, HORIZON, lam, replay_sequence
        )
        seed_regenerated = bool(
            np.array_equal(uniforms, replay_uniforms)
            and np.array_equal(demands, replay_demands)
        )
        replay_taus, replay_collapsed = simulate_numba(
            replay_uniforms, replay_demands, p, C, X0
        )
        seed_regenerated = bool(
            seed_regenerated
            and np.array_equal(nb_taus, replay_taus)
            and np.array_equal(nb_collapsed, replay_collapsed)
        )

        exact = bool(np.array_equal(ref_taus, nb_taus) and np.array_equal(ref_collapsed, nb_collapsed))
        reproducible = bool(
            np.array_equal(nb_taus, repeat_taus)
            and np.array_equal(nb_collapsed, repeat_collapsed)
            and seed_regenerated
        )
        exact_all = exact_all and exact
        reproducible_all = reproducible_all and reproducible
        collapse_vectors.append(nb_collapsed.astype(np.float64))

        successes = int(nb_collapsed.sum())
        probability = successes / n_runs
        ci_low, ci_high = wilson_interval(successes, n_runs)
        hit_taus = nb_taus[nb_collapsed.astype(bool)]
        rows.append({
            "phase": label,
            "p": p,
            "lambda": lam,
            "delta": DELTA,
            "sigma2": p * (1.0 - p) * C * C + lam,
            "n_runs": n_runs,
            "horizon": HORIZON,
            "collapses": successes,
            "collapse_probability": probability,
            "wilson95_low": ci_low,
            "wilson95_high": ci_high,
            "restricted_mean_tau_Tplus1": float(nb_taus.mean()),
            "conditional_mean_tau": float(hit_taus.mean()) if hit_taus.size else None,
            "reference_numba_exact": exact,
            "fixed_input_reproducible": reproducible,
            "fixed_seed_regeneration_reproducible": seed_regenerated,
            "reference_seconds": reference_seconds,
            "numba_seconds": numba_seconds,
            "numba_repeat_seconds": repeat_seconds,
        })

    differences = [
        rows[i + 1]["collapse_probability"] - rows[i]["collapse_probability"]
        for i in range(len(rows) - 1)
    ]
    difference_intervals = [
        bootstrap_difference_ci(collapse_vectors[i], collapse_vectors[i + 1], seed + 7000 + i)
        for i in range(len(rows) - 1)
    ]
    return {
        "label": label,
        "seed": seed,
        "rows": rows,
        "adjacent_risk_differences": differences,
        "adjacent_difference_bootstrap95": difference_intervals,
        "monotone": bool(all(value > 0.0 for value in differences)),
        "exact_all": exact_all,
        "reproducible_all": reproducible_all,
        "timing": {
            "input_generation_seconds": total_generation,
            "reference_seconds": total_reference,
            "numba_seconds": total_numba,
            "numba_repeat_seconds": total_repeat,
            "warmed_speedup": total_reference / total_repeat if total_repeat else None,
        },
    }


def classify_claim(pilot, confirmation, infrastructure_pass):
    pilot_signal = bool(
        pilot["monotone"]
        and all(value >= 0.02 for value in pilot["adjacent_risk_differences"])
    )
    confirmation_signal = bool(
        confirmation["monotone"]
        and all(interval[0] > 0.0 for interval in confirmation["adjacent_difference_bootstrap95"])
    )
    if not infrastructure_pass:
        return "infrastructure_failure"
    if pilot_signal and confirmation_signal:
        return "preliminary_supported"
    if not confirmation["monotone"]:
        return "rejected_on_tested_grid"
    return "inconclusive"


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    RESULTS.mkdir(exist_ok=True)
    VALIDATION.mkdir(exist_ok=True)
    started = time.perf_counter()
    warmup_seconds = warm_numba()
    pilot = run_phase("pilot", 250, 20260429)
    confirmation = run_phase("confirmation", 500, 20260430)

    infrastructure_pass = bool(
        pilot["exact_all"] and pilot["reproducible_all"]
        and confirmation["exact_all"] and confirmation["reproducible_all"]
    )
    claim_status = classify_claim(pilot, confirmation, infrastructure_pass)

    summary = {
        "cycle": "quality_max_microcycle_01",
        "scientific_status": "preliminary_non_publishable",
        "claim_status": claim_status,
        "model": {"C": C, "X0": X0, "delta": DELTA, "horizon": HORIZON, "p_values": P_VALUES},
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpus": os.cpu_count(),
            "numpy": np.__version__,
            "numba": numba.__version__,
            "numba_threads": numba.get_num_threads(),
        },
        "jit_warmup_seconds": warmup_seconds,
        "pilot": pilot,
        "confirmation": confirmation,
        "infrastructure_pass": infrastructure_pass,
        "total_seconds": time.perf_counter() - started,
    }
    write_csv(RESULTS / "pilot_summary.csv", pilot["rows"])
    write_csv(RESULTS / "confirmation_summary.csv", confirmation["rows"])
    (RESULTS / "compact_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    performance = f"""# Performance Report

- JIT warm-up/compilation: {warmup_seconds:.6f} s
- Pilot reference runtime: {pilot['timing']['reference_seconds']:.6f} s
- Pilot warmed Numba repeat: {pilot['timing']['numba_repeat_seconds']:.6f} s
- Pilot warmed speedup: {pilot['timing']['warmed_speedup']:.2f}x
- Confirmation reference runtime: {confirmation['timing']['reference_seconds']:.6f} s
- Confirmation warmed Numba repeat: {confirmation['timing']['numba_repeat_seconds']:.6f} s
- Confirmation warmed speedup: {confirmation['timing']['warmed_speedup']:.2f}x
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
"""
    (VALIDATION / "PERFORMANCE_REPORT.md").write_text(performance, encoding="utf-8")

    validation = f"""# Validation Report

- Infrastructure pass: {infrastructure_pass}
- Claim status: {claim_status}
- Pilot reference/Numba exact: {pilot['exact_all']}
- Confirmation reference/Numba exact: {confirmation['exact_all']}
- Pilot fixed-input reproduction: {pilot['reproducible_all']}
- Confirmation fixed-input reproduction: {confirmation['reproducible_all']}
- Fresh fixed-seed regeneration and output reproduction: {confirmation['reproducible_all']}
- Pilot monotone ordering: {pilot['monotone']}
- Confirmation monotone ordering: {confirmation['monotone']}
- Pilot adjacent differences: {pilot['adjacent_risk_differences']}
- Confirmation adjacent differences: {confirmation['adjacent_risk_differences']}
- Wilson intervals and deterministic bootstrap intervals: recorded in compact summary
- Bootstrap method: 1,000 deterministic percentile resamples per adjacent contrast
- Confirmation bootstrap intervals: {confirmation['adjacent_difference_bootstrap95']}

This microcycle does not establish novelty, causal attribution to variance,
generality beyond the tested grid, or publication-ready evidence.
"""
    (VALIDATION / "VALIDATION_REPORT.md").write_text(validation, encoding="utf-8")
    print(json.dumps({
        "infrastructure_pass": infrastructure_pass,
        "claim_status": claim_status,
        "pilot_differences": pilot["adjacent_risk_differences"],
        "confirmation_differences": confirmation["adjacent_risk_differences"],
        "pilot_speedup": pilot["timing"]["warmed_speedup"],
        "confirmation_speedup": confirmation["timing"]["warmed_speedup"],
        "total_seconds": summary["total_seconds"],
    }, indent=2))
    return 0 if infrastructure_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
