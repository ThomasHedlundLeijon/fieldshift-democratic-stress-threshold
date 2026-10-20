"""Data quality assessment module."""

from __future__ import annotations
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from config import PARTIES, PARLIAMENTARY_THRESHOLD


def assess_quality(
    sources: List[dict],
    shares: Dict[str, float],
    as_of: Optional[str] = None,
) -> dict:
    """
    Assess data quality from poll sources and computed shares.

    sources: list of dicts with keys: id, name, date, weight
    shares: computed weighted shares
    """
    today = date.fromisoformat(as_of) if as_of else date.today()

    # Recency scoring
    recency_scores = []
    stale_sources = []
    for s in sources:
        src_date = date.fromisoformat(s["date"]) if "date" in s else None
        if src_date:
            age_days = (today - src_date).days
            recency = max(0.0, 1.0 - age_days / 30.0)
            recency_scores.append(recency)
            if age_days > 14:
                stale_sources.append(s.get("name", s.get("id", "?")))

    avg_recency = round(sum(recency_scores) / len(recency_scores), 3) if recency_scores else 0.0

    # Sum validation
    total = sum(shares.get(p, 0.0) for p in PARTIES)
    sum_ok = abs(total - 100.0) < 1.0

    # Missing party check
    missing = [p for p in PARTIES if shares.get(p, 0.0) == 0.0]

    # Below-threshold party check
    near_threshold = [
        p for p in PARTIES
        if 0 < shares.get(p, 0.0) < PARLIAMENTARY_THRESHOLD + 0.5
    ]

    # Overall reliability score
    n_sources = len(sources)
    source_score = min(1.0, n_sources / 4.0)
    reliability = round((source_score + avg_recency) / 2.0, 3)

    return {
        "n_sources": n_sources,
        "last_update": max((s.get("date", "") for s in sources), default=""),
        "stale_sources": stale_sources,
        "stale_warning": len(stale_sources) > 0,
        "missing_parties": missing,
        "share_sum": round(total, 3),
        "sum_valid": sum_ok,
        "near_threshold_parties": near_threshold,
        "recency_score": avg_recency,
        "reliability_score": reliability,
    }
