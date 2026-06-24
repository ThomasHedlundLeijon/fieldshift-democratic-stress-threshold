"""GTT Diagnostics — aggregate all GTT signals for a snapshot."""

from __future__ import annotations
from typing import Dict, List, Optional
from datetime import date

from gtt.state_vector import StateVector, compute_momentum, compute_acceleration, compute_volatility
from gtt.psi import compute_psi, distance_to_threshold, threshold_sensitivity
from gtt.zones import classify_zone, zone_label, zone_color
from gtt.transition_risk import compute_transition_risk
from config import (
    GTT_K_DEFAULT, GTT_EPSILON, VOLATILITY_WINDOW,
    SENSITIVITY_LABELS, VOLATILITY_LABELS, ELECTION_DATE,
)


def sensitivity_label(sens: float) -> str:
    for threshold, label in SENSITIVITY_LABELS:
        if sens < threshold:
            return label
    return SENSITIVITY_LABELS[-1][1]


def volatility_label(vol: float) -> str:
    for threshold, label in VOLATILITY_LABELS:
        if vol < threshold:
            return label
    return VOLATILITY_LABELS[-1][1]


def run_diagnostics(
    vectors: List[StateVector],
    K: float = GTT_K_DEFAULT,
    epsilon: float = GTT_EPSILON,
    zones: Optional[dict] = None,
    calibrated: bool = False,
) -> dict:
    """
    Compute full GTT diagnostics from a list of state vectors (oldest first).

    Returns a comprehensive dict suitable for display and archival.
    """
    if not vectors:
        raise ValueError("At least one StateVector required.")

    current = vectors[-1]
    bm = current.block_margin
    psi = compute_psi(bm, K)
    dist = distance_to_threshold(psi)
    sens = threshold_sensitivity(bm, epsilon)
    zone_key = classify_zone(psi, zones)

    momentum = compute_momentum(vectors)
    acceleration = compute_acceleration(vectors)
    volatility = compute_volatility(vectors, VOLATILITY_WINDOW)

    block_momentum_val = None
    if momentum:
        from config import LEFT_BLOCK, RIGHT_BLOCK
        left_m = sum(momentum[p] for p in LEFT_BLOCK)
        right_m = sum(momentum[p] for p in RIGHT_BLOCK)
        block_momentum_val = right_m - left_m

    days_to_election = (date.fromisoformat(ELECTION_DATE) - date.today()).days
    days_to_election = max(0, days_to_election)

    risk = compute_transition_risk(
        psi=psi,
        volatility_block=volatility.get("block", 0.0),
        block_momentum=block_momentum_val,
        days_to_election=days_to_election,
        calibrated=calibrated,
    )

    return {
        # Core GTT
        "psi": round(psi, 4),
        "zone_key": zone_key,
        "zone_label": zone_label(zone_key),
        "zone_color": zone_color(zone_key),
        "block_margin": round(bm, 4),
        "left_total": round(current.left_total, 4),
        "right_total": round(current.right_total, 4),
        "distance_to_threshold": round(dist, 4),
        "threshold_sensitivity": round(sens, 4),
        "sensitivity_label": sensitivity_label(sens),
        # Momentum
        "party_momentum": {p: round(v, 4) for p, v in momentum.items()} if momentum else None,
        "block_momentum": round(block_momentum_val, 4) if block_momentum_val is not None else None,
        "block_acceleration": round(acceleration["block"], 4) if acceleration else None,
        # Volatility
        "volatility": {k: round(v, 4) for k, v in volatility.items()},
        "volatility_label": volatility_label(volatility.get("block", 0.0)),
        # Risk
        "transition_risk": risk,
        # Meta
        "K": K,
        "epsilon": epsilon,
        "calibrated": calibrated,
        "days_to_election": days_to_election,
        "party_shares": current.shares,
        "snapshot_id": current.snapshot_id,
        "timestamp": current.timestamp,
    }
