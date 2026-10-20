"""Uncertainty intervals for party-level forecasts."""

from __future__ import annotations
from typing import Dict, Optional
from config import PARTIES


def compute_uncertainty(
    shares: Dict[str, float],
    volatility: Dict[str, float],
    days_to_election: int,
    coverage: float = 0.90,
) -> Dict[str, tuple]:
    """
    Return (low, high) 90% uncertainty interval per party.

    Interval widens with volatility and time remaining.
    Based on normal approximation: ±z * sigma_adjusted.

    z ≈ 1.645 for 90% coverage.
    """
    z = 1.645
    time_scale = min(2.0, 1.0 + days_to_election / 180.0)
    intervals: Dict[str, tuple] = {}
    for p in PARTIES:
        sigma = volatility.get(p, 1.0) * time_scale
        lo = max(0.0, shares.get(p, 0.0) - z * sigma)
        hi = min(100.0, shares.get(p, 0.0) + z * sigma)
        intervals[p] = (round(lo, 2), round(hi, 2))
    return intervals
