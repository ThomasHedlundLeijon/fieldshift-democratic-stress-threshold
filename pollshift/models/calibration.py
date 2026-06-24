"""
Calibration module — historical MAE, RMSE, bias calculation.

Loads from data/historical_elections.json and data/polls.json.
Only computes MAE when real historical data is present.
If data is missing: returns calibration_pending = True.
"""

from __future__ import annotations
import json
import math
from typing import Dict, List, Optional
from pathlib import Path

from config import PARTIES, LEFT_BLOCK, RIGHT_BLOCK, HISTORICAL_FILE, POLLS_FILE


DAYS_BUCKETS = [
    (0, 0,   "Valdagen"),
    (1, 7,   "1–7 dagar"),
    (8, 14,  "8–14 dagar"),
    (15, 30, "15–30 dagar"),
    (31, 60, "31–60 dagar"),
    (61, 90, "61–90 dagar"),
    (91, 9999, "91+ dagar"),
]


def _bucket_label(days: int) -> str:
    for lo, hi, label in DAYS_BUCKETS:
        if lo <= days <= hi:
            return label
    return "91+ dagar"


def _mae(actual: list, predicted: list) -> float:
    if not actual:
        return float("nan")
    return sum(abs(a - p) for a, p in zip(actual, predicted)) / len(actual)


def _rmse(actual: list, predicted: list) -> float:
    if not actual:
        return float("nan")
    return math.sqrt(sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual))


def _bias(actual: list, predicted: list) -> float:
    if not actual:
        return float("nan")
    return sum(p - a for a, p in zip(actual, predicted)) / len(actual)


class CalibrationEngine:
    def __init__(self) -> None:
        self.calibration_pending = True
        self.historical = []
        self.polls = []
        self._results: Optional[dict] = None
        self._load()

    def _load(self) -> None:
        if HISTORICAL_FILE.exists():
            with open(HISTORICAL_FILE) as f:
                self.historical = json.load(f)
        if POLLS_FILE.exists():
            with open(POLLS_FILE) as f:
                self.polls = json.load(f)

        if self.historical and self.polls:
            self.calibration_pending = False

    def run(self) -> dict:
        """Compute all calibration metrics. Returns dict with all results."""
        if self.calibration_pending:
            return {"calibration_pending": True, "message": "Kalibrering pågår — historisk data saknas."}

        if self._results is not None:
            return self._results

        errors_by_party: Dict[str, List[float]] = {p: [] for p in PARTIES}
        errors_left: List[float] = []
        errors_right: List[float] = []
        errors_by_bucket: Dict[str, List[float]] = {}
        win_predictions: List[tuple] = []   # (predicted_winner, actual_winner)

        for election in self.historical:
            election_id = election["id"]
            actual_shares = election["actual_shares"]
            actual_left = sum(actual_shares.get(p, 0) for p in LEFT_BLOCK)
            actual_right = sum(actual_shares.get(p, 0) for p in RIGHT_BLOCK)
            actual_winner = "right" if actual_right > actual_left else "left"

            for poll in self.polls:
                if poll.get("election_id") != election_id:
                    continue
                days = poll.get("days_before_election", 999)
                bucket = _bucket_label(days)
                pred = poll.get("predicted_shares", {})

                # Party errors
                for p in PARTIES:
                    if p in actual_shares and p in pred:
                        errors_by_party[p].append(abs(actual_shares[p] - pred[p]))

                # Block errors
                pred_left = sum(pred.get(p, 0) for p in LEFT_BLOCK)
                pred_right = sum(pred.get(p, 0) for p in RIGHT_BLOCK)
                errors_left.append(abs(actual_left - pred_left))
                errors_right.append(abs(actual_right - pred_right))

                # Bucket errors
                all_errs = [abs(actual_shares.get(p, 0) - pred.get(p, 0)) for p in PARTIES]
                errors_by_bucket.setdefault(bucket, []).extend(all_errs)

                # Win prediction accuracy
                pred_winner = "right" if pred_right > pred_left else "left"
                win_predictions.append((pred_winner, actual_winner))

        party_mae = {p: _mae([], errors_by_party[p]) for p in PARTIES}
        # Flatten all errors for overall MAE
        all_errors = [e for errs in errors_by_party.values() for e in errs]
        overall_actual = [0.0] * len(all_errors)
        overall_pred   = all_errors

        bucket_mae = {
            bucket: round(sum(errs) / len(errs), 4) if errs else float("nan")
            for bucket, errs in errors_by_bucket.items()
        }

        correct_wins = sum(1 for pw, aw in win_predictions if pw == aw)
        win_accuracy = correct_wins / len(win_predictions) if win_predictions else float("nan")

        self._results = {
            "calibration_pending": False,
            "overall_mae": round(sum(all_errors) / len(all_errors), 4) if all_errors else float("nan"),
            "block_mae": {
                "left": round(sum(errors_left) / len(errors_left), 4) if errors_left else float("nan"),
                "right": round(sum(errors_right) / len(errors_right), 4) if errors_right else float("nan"),
            },
            "party_mae": {p: round(_mae([], errors_by_party[p]) if not errors_by_party[p]
                                   else sum(errors_by_party[p]) / len(errors_by_party[p]), 4)
                          for p in PARTIES},
            "bucket_mae": bucket_mae,
            "win_accuracy": round(win_accuracy, 4) if not math.isnan(win_accuracy) else None,
            "n_elections": len(self.historical),
            "n_poll_snapshots": len(self.polls),
            "calibration_version": f"v{len(self.historical)}elections",
        }
        return self._results
