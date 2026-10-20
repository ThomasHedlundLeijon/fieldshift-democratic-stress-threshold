"""GTT Transition Risk Score."""

from __future__ import annotations
import math
from typing import Optional


def compute_transition_risk(
    psi: float,
    volatility_block: float,
    block_momentum: Optional[float],
    days_to_election: int,
    calibrated: bool = False,
) -> dict:
    """
    Combine structural indicators into a transition risk score [0, 1].

    Components:
    - distance_factor: closeness to threshold
    - volatility_factor: recent instability
    - momentum_factor: movement toward threshold
    - time_factor: discount for distant elections

    Returns dict with score and component breakdown.
    """
    distance = abs(psi - 0.5)

    # Proximity to threshold increases risk
    distance_factor = max(0.0, 1.0 - distance / 0.5)

    # Volatility amplifies uncertainty
    volatility_factor = min(1.0, volatility_block / 3.0)

    # Momentum toward threshold increases risk
    if block_momentum is not None:
        # momentum pushing psi toward 0.5 → risk up
        toward_threshold = (psi > 0.5 and block_momentum < 0) or \
                           (psi < 0.5 and block_momentum > 0)
        momentum_factor = min(1.0, abs(block_momentum) / 2.0) if toward_threshold else 0.0
    else:
        momentum_factor = 0.0

    # Time discount: elections far away have higher uncertainty
    time_factor = max(0.0, min(1.0, 1.0 - days_to_election / 365.0))

    # Weighted composite
    raw_score = (
        0.40 * distance_factor +
        0.25 * volatility_factor +
        0.20 * momentum_factor +
        0.15 * time_factor
    )
    score = max(0.0, min(1.0, raw_score))

    label = _risk_label(score)

    return {
        "score": round(score, 4),
        "label": label,
        "distance_factor": round(distance_factor, 4),
        "volatility_factor": round(volatility_factor, 4),
        "momentum_factor": round(momentum_factor, 4),
        "time_factor": round(time_factor, 4),
        "calibrated": calibrated,
        "note": "Probabilistisk uppskattning — ej deterministisk prognos.",
    }


def _risk_label(score: float) -> str:
    if score < 0.25:
        return "Låg övergångsrisk"
    elif score < 0.50:
        return "Måttlig övergångsrisk"
    elif score < 0.75:
        return "Hög övergångsrisk"
    return "Kritisk övergångsrisk"
