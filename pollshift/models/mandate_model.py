"""
Simplified proportional mandate model for Swedish Riksdag (349 seats).

TODO: Replace with full modified Sainte-Laguë + constituency adjustment.

NOTICE: Mandatberäkningen är preliminär och förenklad tills full
        svensk mandatmodell är implementerad.
"""

from __future__ import annotations
from typing import Dict, List
from config import PARTIES, PARLIAMENTARY_THRESHOLD, SEATS_TOTAL, LEFT_BLOCK, RIGHT_BLOCK


def compute_mandates(shares: Dict[str, float]) -> Dict[str, int]:
    """
    Simplified proportional allocation.

    Only parties above the parliamentary threshold receive seats.
    Remaining seats (due to rounding) go to largest remainder party.
    """
    eligible = {p: v for p, v in shares.items()
                if p in PARTIES and v >= PARLIAMENTARY_THRESHOLD}

    total_eligible = sum(eligible.values())
    if total_eligible == 0:
        return {p: 0 for p in PARTIES}

    # Initial allocation (floor)
    raw = {p: (v / total_eligible) * SEATS_TOTAL for p, v in eligible.items()}
    floors = {p: int(v) for p, v in raw.items()}
    remainders = {p: raw[p] - floors[p] for p in eligible}

    allocated = sum(floors.values())
    remaining = SEATS_TOTAL - allocated

    # Largest remainder
    sorted_rem = sorted(remainders, key=lambda p: remainders[p], reverse=True)
    for p in sorted_rem[:remaining]:
        floors[p] += 1

    # Zero for below-threshold parties
    result = {p: 0 for p in PARTIES}
    result.update(floors)
    return result


def block_mandates(mandate_dict: Dict[str, int]) -> Dict[str, int]:
    return {
        "left":  sum(mandate_dict[p] for p in LEFT_BLOCK),
        "right": sum(mandate_dict[p] for p in RIGHT_BLOCK),
    }


MANDATE_DISCLAIMER = (
    "Mandatberäkningen är preliminär och förenklad tills full "
    "svensk mandatmodell är implementerad."
)
