"""GTT calibrated threshold management."""

from __future__ import annotations
from typing import Optional
from config import PSI_ZONES, GTT_K_DEFAULT, GTT_EPSILON


def default_zones() -> dict:
    return dict(PSI_ZONES)


def recalibrate_zones(historical_elections: list) -> Optional[dict]:
    """
    Derive zone thresholds empirically from historical elections.

    Each election entry must have:
      - psi_at_election: float
      - winner: "left" | "right"

    Returns recalibrated zone dict or None if insufficient data.
    """
    if len(historical_elections) < 3:
        return None

    psi_values = sorted(e["psi_at_election"] for e in historical_elections
                        if "psi_at_election" in e)
    if not psi_values:
        return None

    mid = 0.5
    spread = max(abs(p - mid) for p in psi_values) or 0.1
    lean_boundary = round(mid - spread * 0.4, 3)
    stable_boundary = round(mid - spread * 0.8, 3)

    return {
        "left_stable":  (0.00, stable_boundary),
        "left_lean":    (stable_boundary, lean_boundary),
        "threshold":    (lean_boundary, 1 - lean_boundary),
        "right_lean":   (1 - lean_boundary, 1 - stable_boundary),
        "right_stable": (1 - stable_boundary, 1.00),
    }


def estimate_K(historical_elections: list) -> float:
    """
    Estimate K from historical elections.

    Each election entry must have:
      - block_margin: float (R − L in percentage points)
      - psi_empirical: float (empirical win probability proxy)

    Uses: PSI = 0.5 + B / K  →  K = B / (PSI − 0.5)
    Returns mean K across elections where |PSI − 0.5| > 0.01.
    """
    Ks = []
    for e in historical_elections:
        bm = e.get("block_margin")
        psi_e = e.get("psi_empirical")
        if bm is None or psi_e is None:
            continue
        denom = psi_e - 0.5
        if abs(denom) > 0.01:
            Ks.append(bm / denom)
    if not Ks:
        return GTT_K_DEFAULT
    return float(sum(Ks) / len(Ks))
