import numpy as np

from scripts.run_micro_experiment import (
    C,
    DELTA,
    P_VALUES,
    X0,
    classify_claim,
    generate_inputs,
    simulate_numba,
    simulate_reference,
    wilson_interval,
)


def test_fixed_drift():
    for p in P_VALUES:
        lam = (1.0 - p) * C - DELTA
        assert (1.0 - p) * C - lam == DELTA


def test_reference_numba_exact_small_fixture():
    uniforms = np.array([[0.01, 0.5, 0.5], [0.5, 0.01, 0.5]], dtype=float)
    demands = np.array([[60, 60, 60], [60, 60, 60]], dtype=np.int16)
    expected = simulate_reference(uniforms, demands, 0.1, C, X0)
    actual = simulate_numba(uniforms, demands, 0.1, C, X0)
    assert np.array_equal(expected[0], actual[0])
    assert np.array_equal(expected[1], actual[1])


def test_wilson_interval_contains_estimate():
    low, high = wilson_interval(60, 100)
    assert low < 0.6 < high


def test_seed_regeneration_and_child_distinction():
    first = generate_inputs(4, 8, 88.0, np.random.SeedSequence(1234))
    replay = generate_inputs(4, 8, 88.0, np.random.SeedSequence(1234))
    different = generate_inputs(4, 8, 88.0, np.random.SeedSequence(1235))
    assert np.array_equal(first[0], replay[0])
    assert np.array_equal(first[1], replay[1])
    assert not np.array_equal(first[0], different[0])


def test_promotion_requires_positive_confirmation_intervals():
    pilot = {"monotone": True, "adjacent_risk_differences": [0.2, 0.1]}
    confirmation = {
        "monotone": True,
        "adjacent_difference_bootstrap95": [(0.1, 0.3), (-0.01, 0.2)],
    }
    assert classify_claim(pilot, confirmation, True) == "inconclusive"
