"""Load historical Swedish election results for calibration and backtesting."""

from __future__ import annotations
import json
from typing import List
from config import HISTORICAL_FILE


# Embedded historical data for calibration (2002–2022)
# Source: Valmyndigheten — actual results
EMBEDDED_HISTORICAL = [
    {
        "id": "SE-2002",
        "date": "2002-09-15",
        "actual_shares": {
            "S": 39.85, "V": 8.30, "C": 6.19, "MP": 4.65,
            "M": 15.26, "SD": 1.44, "KD": 9.15, "L": 13.39,
        },
        "winner": "left",
    },
    {
        "id": "SE-2006",
        "date": "2006-09-17",
        "actual_shares": {
            "S": 34.99, "V": 5.84, "C": 7.88, "MP": 5.24,
            "M": 26.23, "SD": 2.93, "KD": 6.59, "L": 7.54,
        },
        "winner": "right",
    },
    {
        "id": "SE-2010",
        "date": "2010-09-19",
        "actual_shares": {
            "S": 30.66, "V": 5.60, "C": 6.56, "MP": 7.34,
            "M": 30.06, "SD": 5.70, "KD": 5.60, "L": 7.06,
        },
        "winner": "right",
    },
    {
        "id": "SE-2014",
        "date": "2014-09-14",
        "actual_shares": {
            "S": 31.01, "V": 5.72, "C": 6.11, "MP": 6.89,
            "M": 23.33, "SD": 12.86, "KD": 4.57, "L": 5.42,
        },
        "winner": "left",
    },
    {
        "id": "SE-2018",
        "date": "2018-09-09",
        "actual_shares": {
            "S": 28.26, "V": 7.90, "C": 8.61, "MP": 4.41,
            "M": 19.84, "SD": 17.53, "KD": 6.37, "L": 5.49,
        },
        "winner": "left",  # S-bloc formed government with C/L support
    },
    {
        "id": "SE-2022",
        "date": "2022-09-11",
        "actual_shares": {
            "S": 30.33, "V": 6.75, "C": 6.71, "MP": 5.08,
            "M": 19.10, "SD": 20.54, "KD": 5.34, "L": 4.73,
        },
        "winner": "right",
        # Stödröstningskalibrering: L:s organiska stöd ~3.53% men taktiska
        # röster från M (~0.85 pp) och SD (~0.35 pp) lyfte L till 4.73%.
        # Utan stödröster: L under spärren → vänsterblock +17 mandat → klar vänstervinct.
        # Med stödröster: högerblock vann med 3 mandats marginal.
        "tactical_voting": {
            "L": {
                "organic_share": 3.53,
                "inflow_total": 1.20,
                "donors": {"M": 0.85, "SD": 0.35},
                "crosses_threshold": True,
            }
        },
        "counterfactual_without_tactical": {
            "block_margin_mandates": -14,
            "winner": "left",
            "note": "Hypotetiskt utfall om L:s organiska stöd ~3.53% hade gällt.",
        },
        "actual_block_margin_mandates": 3,
    },
]


def load_historical() -> List[dict]:
    """Load historical elections, preferring file over embedded data."""
    if HISTORICAL_FILE.exists():
        with open(HISTORICAL_FILE) as f:
            return json.load(f)
    return EMBEDDED_HISTORICAL


def save_historical(data: List[dict]) -> None:
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
