"""Deterministic first-passage simulation kernels and statistics."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
from numba import njit, prange


@dataclass(frozen=True)
class ModelConfig:
    capacity: int = 100
    initial_inventory: int = 50
    drift_margin: float = 2.0
    horizon: int = 500

    def demand_rate(self, disruption_probability: float) -> float:
        return (1.0 - disruption_probability) * self.capacity - self.drift_margin


def simulate_reference(
    uniforms: np.ndarray,
    demands: np.ndarray,
    disruption_probability: float,
    capacity: int,
    initial_inventory: int,
) -> tuple[np.ndarray, np.ndarray]:
    n_runs, horizon = uniforms.shape
    taus = np.full(n_runs, horizon + 1, dtype=np.int64)
    collapsed = np.zeros(n_runs, dtype=np.uint8)
    for run_index in range(n_runs):
        inventory = initial_inventory
        for period in range(horizon):
            production = 0 if uniforms[run_index, period] < disruption_probability else capacity
            inventory += production - int(demands[run_index, period])
            if inventory <= 0:
                taus[run_index] = period + 1
                collapsed[run_index] = 1
                break
    return taus, collapsed


@njit(cache=True, parallel=True, fastmath=False)
def simulate_numba(
    uniforms: np.ndarray,
    demands: np.ndarray,
    disruption_probability: float,
    capacity: int,
    initial_inventory: int,
) -> tuple[np.ndarray, np.ndarray]:
    n_runs, horizon = uniforms.shape
    taus = np.full(n_runs, horizon + 1, dtype=np.int64)
    collapsed = np.zeros(n_runs, dtype=np.uint8)
    for run_index in prange(n_runs):
        inventory = initial_inventory
        for period in range(horizon):
            production = 0 if uniforms[run_index, period] < disruption_probability else capacity
            inventory += production - demands[run_index, period]
            if inventory <= 0:
                taus[run_index] = period + 1
                collapsed[run_index] = 1
                break
    return taus, collapsed


def derive_batch_seed(
    master_seed: int,
    replication_index: int,
    configuration_index: int,
    batch_index: int,
) -> int:
    sequence = np.random.SeedSequence(
        [master_seed, replication_index, configuration_index, batch_index]
    )
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def generate_batch(
    n_runs: int,
    horizon: int,
    demand_rate: float,
    batch_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    uniform_seed, demand_seed = np.random.SeedSequence(batch_seed).spawn(2)
    uniforms = np.random.default_rng(uniform_seed).random((n_runs, horizon))
    demands = np.random.default_rng(demand_seed).poisson(
        demand_rate, size=(n_runs, horizon)
    ).astype(np.int16)
    return uniforms, demands


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    estimate = successes / total
    denominator = 1.0 + z * z / total
    center = (estimate + z * z / (2.0 * total)) / denominator
    radius = z * math.sqrt(
        estimate * (1.0 - estimate) / total + z * z / (4.0 * total**2)
    ) / denominator
    return center - radius, center + radius


def warm_numba() -> float:
    uniforms = np.full((4, 8), 0.5, dtype=np.float64)
    demands = np.full((4, 8), 80, dtype=np.int16)
    started = time.perf_counter()
    simulate_numba(uniforms, demands, 0.1, 100, 50)
    return time.perf_counter() - started


def run_batch(
    model: ModelConfig,
    disruption_probability: float,
    n_runs: int,
    batch_seed: int,
    reference_runs: int = 0,
) -> dict[str, object]:
    demand_rate = model.demand_rate(disruption_probability)
    generated_at = time.perf_counter()
    uniforms, demands = generate_batch(n_runs, model.horizon, demand_rate, batch_seed)
    generation_seconds = time.perf_counter() - generated_at

    simulated_at = time.perf_counter()
    taus, collapsed = simulate_numba(
        uniforms,
        demands,
        disruption_probability,
        model.capacity,
        model.initial_inventory,
    )
    simulation_seconds = time.perf_counter() - simulated_at

    reference_exact = True
    seed_replay_exact = True
    reference_seconds = 0.0
    if reference_runs:
        check_runs = min(reference_runs, n_runs)
        replay_uniforms, replay_demands = generate_batch(
            check_runs, model.horizon, demand_rate, batch_seed
        )
        seed_replay_exact = bool(
            np.array_equal(uniforms[:check_runs], replay_uniforms)
            and np.array_equal(demands[:check_runs], replay_demands)
        )
        reference_at = time.perf_counter()
        ref_taus, ref_collapsed = simulate_reference(
            uniforms[:check_runs],
            demands[:check_runs],
            disruption_probability,
            model.capacity,
            model.initial_inventory,
        )
        reference_seconds = time.perf_counter() - reference_at
        reference_exact = bool(
            np.array_equal(taus[:check_runs], ref_taus)
            and np.array_equal(collapsed[:check_runs], ref_collapsed)
        )

    collapsed_mask = collapsed.astype(bool)
    return {
        "n_runs": n_runs,
        "collapses": int(collapsed.sum()),
        "tau_sum": int(taus.sum()),
        "collapsed_tau_sum": int(taus[collapsed_mask].sum()),
        "collapsed_tau_count": int(collapsed_mask.sum()),
        "generation_seconds": generation_seconds,
        "simulation_seconds": simulation_seconds,
        "reference_seconds": reference_seconds,
        "reference_exact": reference_exact,
        "seed_replay_exact": seed_replay_exact,
    }

