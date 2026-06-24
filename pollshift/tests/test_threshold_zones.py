"""Tests for GTT zone classification."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gtt.zones import classify_zone


def test_left_stable():
    assert classify_zone(0.20) == "left_stable"


def test_left_lean():
    assert classify_zone(0.45) == "left_lean"


def test_threshold_zone():
    assert classify_zone(0.50) == "threshold"


def test_right_lean():
    assert classify_zone(0.55) == "right_lean"


def test_right_stable():
    assert classify_zone(0.70) == "right_stable"


def test_boundary_left_lean():
    assert classify_zone(0.42) == "left_lean"


def test_boundary_threshold_low():
    assert classify_zone(0.48) == "threshold"


def test_zone_covers_full_range():
    """Every PSI in [0, 1] must classify to a zone."""
    for i in range(0, 101):
        psi = i / 100.0
        zone = classify_zone(psi)
        assert zone is not None
        assert isinstance(zone, str)
