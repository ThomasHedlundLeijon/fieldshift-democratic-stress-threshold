"""Deterministic scenario engine — no random generation."""

from __future__ import annotations
from typing import Dict, List
from copy import deepcopy

from gtt.state_vector import StateVector
from gtt.diagnostics import run_diagnostics
from models.mandate_model import compute_mandates, block_mandates
from config import PARTIES, GTT_K_DEFAULT, GTT_EPSILON


def apply_scenario(
    base_shares: Dict[str, float],
    adjustments: Dict[str, float],
) -> Dict[str, float]:
    """
    Apply deterministic adjustments to base shares.

    adjustments: party -> delta (e.g. {"M": +1.0, "S": -1.0})
    Result is renormalized to sum to 100.
    """
    adjusted = {p: base_shares.get(p, 0.0) + adjustments.get(p, 0.0)
                for p in PARTIES}
    # Clip to [0, 100]
    adjusted = {p: max(0.0, min(100.0, v)) for p, v in adjusted.items()}
    total = sum(adjusted.values())
    if total > 0:
        adjusted = {p: v * 100.0 / total for p, v in adjusted.items()}
    return adjusted


def run_scenario(
    base_shares: Dict[str, float],
    adjustments: Dict[str, float],
    K: float = GTT_K_DEFAULT,
    epsilon: float = GTT_EPSILON,
    zones: dict | None = None,
) -> dict:
    """Run a single scenario and return full diagnostics + mandates."""
    scenario_shares = apply_scenario(base_shares, adjustments)
    sv = StateVector(shares=scenario_shares, timestamp="scenario", snapshot_id="scenario")
    diag = run_diagnostics([sv], K=K, epsilon=epsilon, zones=zones)
    mandates = compute_mandates(scenario_shares)
    blocks = block_mandates(mandates)
    return {
        "scenario_shares": scenario_shares,
        "diagnostics": diag,
        "mandates": mandates,
        "block_mandates": blocks,
    }


PRESET_SCENARIOS = {
    "Ingen justering": {},
    "S +1%, M -1%": {"S": 1.0, "M": -1.0},
    "S -1%, M +1%": {"S": -1.0, "M": 1.0},
    "SD +2%, L -2%": {"SD": 2.0, "L": -2.0},
    "MP under 4% (MP→0)": {"MP": -10.0},
    "Vänsterblock +2%": {"S": 0.5, "V": 0.5, "C": 0.5, "MP": 0.5},
    "Högerblock +2%": {"M": 0.5, "SD": 0.5, "KD": 0.5, "L": 0.5},
}
