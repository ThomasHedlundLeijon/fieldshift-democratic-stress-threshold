"""
Poll data collection and aggregation.

In production: fetches from live sources.
In demo mode: loads from embedded demo data.
"""

from __future__ import annotations
import json
from typing import Dict, List, Optional
from pathlib import Path

from config import PARTIES, POLLS_FILE, APP_MODE


# ── Demo data (clearly labelled, used only in demo mode) ──────────────────────
DEMO_POLLS = [
    {
        "id": "demo-2024-06",
        "name": "Demo Novus Jun 2024",
        "date": "2024-06-15",
        "weight": 1.0,
        "shares": {"S": 33.2, "V": 8.1, "C": 5.4, "MP": 4.8,
                   "M": 19.1, "SD": 19.5, "KD": 4.2, "L": 3.9},
        "demo": True,
    },
    {
        "id": "demo-2024-09",
        "name": "Demo Sifo Sep 2024",
        "date": "2024-09-10",
        "weight": 1.0,
        "shares": {"S": 32.8, "V": 8.4, "C": 5.1, "MP": 4.5,
                   "M": 19.8, "SD": 20.2, "KD": 4.0, "L": 3.7},
        "demo": True,
    },
    {
        "id": "demo-2025-01",
        "name": "Demo Novus Jan 2025",
        "date": "2025-01-20",
        "weight": 1.0,
        "shares": {"S": 34.1, "V": 8.6, "C": 5.3, "MP": 4.2,
                   "M": 19.3, "SD": 19.8, "KD": 4.1, "L": 3.6},
        "demo": True,
    },
    {
        "id": "demo-2025-06",
        "name": "Demo Sifo Jun 2025",
        "date": "2025-06-05",
        "weight": 1.2,
        "shares": {"S": 34.5, "V": 8.9, "C": 5.5, "MP": 4.3,
                   "M": 18.9, "SD": 20.1, "KD": 4.0, "L": 3.4},
        "demo": True,
    },
    {
        "id": "demo-2026-03",
        "name": "Demo Novus Mar 2026",
        "date": "2026-03-15",
        "weight": 1.5,
        "shares": {"S": 34.8, "V": 9.1, "C": 5.7, "MP": 4.4,
                   "M": 18.7, "SD": 19.9, "KD": 4.1, "L": 3.3},
        "demo": True,
    },
]


def load_polls() -> List[dict]:
    """Load poll data. Demo mode uses embedded demo polls."""
    if APP_MODE == "demo":
        return DEMO_POLLS

    if POLLS_FILE.exists():
        with open(POLLS_FILE) as f:
            return json.load(f)
    return []


def aggregate_shares(polls: List[dict], method: str = "weighted_mean") -> Dict[str, float]:
    """
    Aggregate multiple polls into a single share estimate.

    method: "weighted_mean" (default) or "simple_mean"
    """
    if not polls:
        return {p: 0.0 for p in PARTIES}

    weights = [p.get("weight", 1.0) for p in polls]
    total_w = sum(weights)

    aggregated: Dict[str, float] = {}
    for party in PARTIES:
        if method == "simple_mean":
            aggregated[party] = sum(p["shares"].get(party, 0.0)
                                    for p in polls) / len(polls)
        else:
            aggregated[party] = sum(
                p["shares"].get(party, 0.0) * w
                for p, w in zip(polls, weights)
            ) / total_w

    return {p: round(v, 4) for p, v in aggregated.items()}


def get_sources_meta(polls: List[dict]) -> List[dict]:
    return [{"id": p["id"], "name": p.get("name", p["id"]),
             "date": p.get("date", ""), "weight": p.get("weight", 1.0)}
            for p in polls]
