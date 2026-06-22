import numpy as np

from industrial_research_lab.model import (
    ModelConfig,
    derive_batch_seed,
    generate_batch,
    run_batch,
    wilson_interval,
)
from industrial_research_lab.pipeline import PROFILES, configurations, profile_fingerprint


def test_batch_seed_is_deterministic_and_distinct():
    first = derive_batch_seed(1234, 0, 0, 0)
    assert first == derive_batch_seed(1234, 0, 0, 0)
    assert first != derive_batch_seed(1234, 0, 0, 1)
    assert first != derive_batch_seed(1234, 1, 0, 0)


def test_vectorized_generation_replays_exactly():
    first = generate_batch(8, 12, 88.0, 1234)
    replay = generate_batch(8, 12, 88.0, 1234)
    assert np.array_equal(first[0], replay[0])
    assert np.array_equal(first[1], replay[1])


def test_batch_reference_and_numba_agree():
    result = run_batch(ModelConfig(horizon=32), 0.1, 16, 5678, reference_runs=16)
    assert result["reference_exact"] is True
    assert result["seed_replay_exact"] is True
    assert result["n_runs"] == 16


def test_profile_fingerprint_changes_with_profile():
    assert profile_fingerprint(PROFILES["ci"]) != profile_fingerprint(PROFILES["smoke"])
    assert len(configurations(PROFILES["ci"])) == 3
    assert PROFILES["cloud-proof"].max_minutes == 10.0


def test_wilson_interval_contains_estimate():
    low, high = wilson_interval(60, 100)
    assert low < 0.6 < high
