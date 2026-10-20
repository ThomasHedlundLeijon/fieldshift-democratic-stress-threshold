"""PollShift configuration — GTT v1.0, PollShift v15.0."""

from __future__ import annotations
import os

# ── Versioning ────────────────────────────────────────────────────────────────
APP_VERSION = "15.0.0"
GTT_VERSION = "1.0.0"
CALIBRATION_VERSION = "pending"

# ── Election target ───────────────────────────────────────────────────────────
ELECTION_DATE = "2026-09-13"  # next Swedish Riksdag election
ELECTION_ID = "SE-2026"
SEATS_TOTAL = 349

# ── Swedish parties ───────────────────────────────────────────────────────────
PARTIES = ["S", "V", "C", "MP", "M", "SD", "KD", "L"]
PARTY_NAMES = {
    "S":  "Socialdemokraterna",
    "V":  "Vänsterpartiet",
    "C":  "Centerpartiet",
    "MP": "Miljöpartiet",
    "M":  "Moderaterna",
    "SD": "Sverigedemokraterna",
    "KD": "Kristdemokraterna",
    "L":  "Liberalerna",
}
PARTY_COLORS = {
    "S":  "#E8112d",
    "V":  "#AF0000",
    "C":  "#009933",
    "MP": "#83CF39",
    "M":  "#1B49A4",
    "SD": "#DDDD00",
    "KD": "#0F4EA3",
    "L":  "#006AB3",
}

LEFT_BLOCK  = ["S", "V", "C", "MP"]
RIGHT_BLOCK = ["M", "SD", "KD", "L"]

PARLIAMENTARY_THRESHOLD = 4.0  # percent

# ── GTT calibration constants (defaults for demo mode) ────────────────────────
GTT_K_DEFAULT = 20.0      # normalization constant K; calibrated from historical data
GTT_EPSILON   = 0.5       # sensitivity denominator floor

# ── PSI zone thresholds (calibrated from 2002–2022 elections by default) ──────
PSI_ZONES = {
    "left_stable":    (0.00, 0.42),
    "left_lean":      (0.42, 0.48),
    "threshold":      (0.48, 0.52),
    "right_lean":     (0.52, 0.58),
    "right_stable":   (0.58, 1.00),
}

ZONE_LABELS = {
    "left_stable":  "Vänster stabil",
    "left_lean":    "Vänster lutar",
    "threshold":    "Tröskelzon",
    "right_lean":   "Höger lutar",
    "right_stable": "Höger stabil",
}

# ── App mode ──────────────────────────────────────────────────────────────────
APP_MODE = os.environ.get("POLLSHIFT_MODE", "demo")   # public | internal | demo

# ── Paths ─────────────────────────────────────────────────────────────────────
import pathlib
BASE_DIR          = pathlib.Path(__file__).parent
DATA_DIR          = BASE_DIR / "data_store"
FORECAST_ARCHIVE  = DATA_DIR / "forecast_archive.jsonl"
HASH_CHAIN_FILE   = DATA_DIR / "hash_chain.jsonl"
BACKTEST_FILE     = DATA_DIR / "backtest_results.json"
HISTORICAL_FILE   = BASE_DIR / "data" / "historical_elections.json"
POLLS_FILE        = BASE_DIR / "data" / "polls.json"

DATA_DIR.mkdir(exist_ok=True)
(BASE_DIR / "data").mkdir(exist_ok=True)

# ── Volatility window ─────────────────────────────────────────────────────────
VOLATILITY_WINDOW = 5   # snapshots

# ── Sensitivity labels ────────────────────────────────────────────────────────
SENSITIVITY_LABELS = [
    (1.0,  "Låg känslighet"),
    (3.0,  "Måttlig känslighet"),
    (8.0,  "Hög känslighet"),
    (float("inf"), "Kritisk tröskelkänslighet"),
]

VOLATILITY_LABELS = [
    (0.5, "Låg"),
    (1.5, "Medel"),
    (3.0, "Hög"),
    (float("inf"), "Kritisk"),
]
