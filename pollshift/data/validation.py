"""Input validation for poll data."""

from __future__ import annotations
from typing import Dict, List, Tuple
from config import PARTIES, PARLIAMENTARY_THRESHOLD


def validate_shares(shares: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Validate a party shares dict.

    Returns (is_valid, list_of_issues).
    """
    issues = []

    for p in PARTIES:
        if p not in shares:
            issues.append(f"Parti saknas: {p}")
        elif not isinstance(shares[p], (int, float)):
            issues.append(f"Ogiltigt värde för {p}: {shares[p]}")
        elif shares[p] < 0:
            issues.append(f"Negativt värde för {p}: {shares[p]}")

    total = sum(shares.get(p, 0.0) for p in PARTIES)
    if abs(total - 100.0) > 2.0:
        issues.append(f"Summa är {total:.2f}%, förväntar 100% (±2%).")

    return len(issues) == 0, issues
