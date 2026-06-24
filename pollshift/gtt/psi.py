"""GTT Pressure Sensitivity Index (PSI) computation."""

from __future__ import annotations
from typing import Optional


def compute_psi(block_margin: float, K: float) -> float:
    """
    PSI_t = clip(0.5 + B_t / K, 0, 1)

    K is calibrated from historical elections.
    Higher PSI → right structural advantage.
    PSI ≈ 0.5 → threshold zone.
    """
    if K == 0:
        raise ValueError("K must be non-zero.")
    raw = 0.5 + block_margin / K
    return max(0.0, min(1.0, raw))


def distance_to_threshold(psi: float) -> float:
    """Geometric distance from the electoral threshold (0.5)."""
    return abs(psi - 0.5)


def threshold_sensitivity(block_margin: float, epsilon: float) -> float:
    """
    Sensitivity = 1 / (epsilon + |B_t|)

    Higher value → election more fragile near threshold boundary.
    """
    return 1.0 / (epsilon + abs(block_margin))
