"""Tests for GTT PSI computation."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from gtt.psi import compute_psi, distance_to_threshold, threshold_sensitivity


def test_psi_balanced():
    """Block margin 0 → PSI exactly 0.5."""
    assert compute_psi(0.0, K=20.0) == 0.5


def test_psi_right_advantage():
    psi = compute_psi(5.0, K=20.0)
    assert psi > 0.5


def test_psi_left_advantage():
    psi = compute_psi(-5.0, K=20.0)
    assert psi < 0.5


def test_psi_clipped_high():
    psi = compute_psi(1000.0, K=20.0)
    assert psi == 1.0


def test_psi_clipped_low():
    psi = compute_psi(-1000.0, K=20.0)
    assert psi == 0.0


def test_psi_deterministic():
    """Same input → same output always."""
    result1 = compute_psi(3.2, K=20.0)
    result2 = compute_psi(3.2, K=20.0)
    assert result1 == result2


def test_psi_k_zero_raises():
    with pytest.raises(ValueError):
        compute_psi(1.0, K=0.0)


def test_distance_to_threshold():
    assert distance_to_threshold(0.5) == 0.0
    assert abs(distance_to_threshold(0.6) - 0.1) < 1e-9
    assert abs(distance_to_threshold(0.4) - 0.1) < 1e-9


def test_threshold_sensitivity_increases_near_zero():
    sens_close = threshold_sensitivity(0.1, epsilon=0.5)
    sens_far   = threshold_sensitivity(5.0, epsilon=0.5)
    assert sens_close > sens_far
