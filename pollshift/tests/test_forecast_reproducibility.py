"""Tests for forecast reproducibility — same input → same output."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gtt.state_vector import StateVector
from models.forecast_engine import GTTForecastEngine


DEMO_SHARES = {
    "S": 34.5, "V": 8.9, "C": 5.5, "MP": 4.3,
    "M": 18.9, "SD": 20.1, "KD": 4.0, "L": 3.4,
}


def _make_forecast():
    sv = StateVector(shares=DEMO_SHARES, timestamp="2026-01-01T00:00:00Z")
    engine = GTTForecastEngine()
    return engine.forecast([sv])


def test_psi_reproducible():
    f1 = _make_forecast()
    f2 = _make_forecast()
    assert f1["diagnostics"]["psi"] == f2["diagnostics"]["psi"]


def test_block_margin_reproducible():
    f1 = _make_forecast()
    f2 = _make_forecast()
    assert f1["block_margin"] == f2["block_margin"]


def test_mandates_reproducible():
    f1 = _make_forecast()
    f2 = _make_forecast()
    assert f1["party_mandates"] == f2["party_mandates"]


def test_winner_reproducible():
    f1 = _make_forecast()
    f2 = _make_forecast()
    assert f1["predicted_winner"] == f2["predicted_winner"]


def test_no_random_in_forecast():
    """Forecasts must not vary across runs (no np.random calls)."""
    results = [_make_forecast()["diagnostics"]["psi"] for _ in range(5)]
    assert len(set(results)) == 1
