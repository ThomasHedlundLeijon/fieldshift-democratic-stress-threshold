"""GTT Zone classification."""

from __future__ import annotations
from config import PSI_ZONES, ZONE_LABELS


def classify_zone(psi: float, zones: dict | None = None) -> str:
    """Return internal zone key for given PSI value."""
    z = zones or PSI_ZONES
    for zone_key, (lo, hi) in z.items():
        if lo <= psi < hi:
            return zone_key
    # Edge: psi exactly 1.0
    return "right_stable"


def zone_label(zone_key: str) -> str:
    return ZONE_LABELS.get(zone_key, zone_key)


def zone_color(zone_key: str) -> str:
    _colors = {
        "left_stable":  "#C62828",
        "left_lean":    "#EF9A9A",
        "threshold":    "#FFF176",
        "right_lean":   "#90CAF9",
        "right_stable": "#1565C0",
    }
    return _colors.get(zone_key, "#BDBDBD")
