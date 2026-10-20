"""
GTT Forecast Engine — top-level forecasting entry point.

Combines state vector, GTT diagnostics, mandate model,
uncertainty, and win-probability into a single forecast object.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from datetime import datetime

from gtt.state_vector import StateVector
from gtt.diagnostics import run_diagnostics
from models.mandate_model import compute_mandates, block_mandates
from models.uncertainty import compute_uncertainty
from config import (
    APP_VERSION, GTT_VERSION, CALIBRATION_VERSION,
    GTT_K_DEFAULT, GTT_EPSILON, ELECTION_ID, ELECTION_DATE,
)


class GTTForecastEngine:
    def __init__(
        self,
        K: float = GTT_K_DEFAULT,
        epsilon: float = GTT_EPSILON,
        zones: Optional[dict] = None,
        calibrated: bool = False,
        calibration_results: Optional[dict] = None,
    ) -> None:
        self.K = K
        self.epsilon = epsilon
        self.zones = zones
        self.calibrated = calibrated
        self.calibration_results = calibration_results or {}

    def forecast(self, vectors: List[StateVector]) -> dict:
        """
        Run GTT forecast from list of StateVectors (oldest → newest).

        Returns comprehensive forecast dict.
        """
        if not vectors:
            raise ValueError("Minst en StateVector krävs.")

        current = vectors[-1]
        diag = run_diagnostics(vectors, K=self.K, epsilon=self.epsilon,
                               zones=self.zones, calibrated=self.calibrated)

        mandates = compute_mandates(current.shares)
        b_mandates = block_mandates(mandates)

        uncertainty = compute_uncertainty(
            shares=current.shares,
            volatility=diag["volatility"],
            days_to_election=diag["days_to_election"],
        )

        winner = self._determine_winner(diag)
        win_prob = self._win_probability(diag)

        forecast = {
            # Identity
            "model_version": APP_VERSION,
            "gtt_version": GTT_VERSION,
            "calibration_version": CALIBRATION_VERSION if not self.calibrated
                                   else self.calibration_results.get("calibration_version", "?"),
            "election_id": ELECTION_ID,
            "election_date": ELECTION_DATE,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            # GTT core
            "diagnostics": diag,
            # Parties
            "party_shares": current.shares,
            "party_mandates": mandates,
            "party_uncertainty": uncertainty,
            # Blocks
            "left_pct": diag["left_total"],
            "right_pct": diag["right_total"],
            "block_margin": diag["block_margin"],
            "left_mandates": b_mandates["left"],
            "right_mandates": b_mandates["right"],
            # Winner
            "predicted_winner": winner,
            "win_probability": win_prob,
            "win_probability_calibrated": self.calibrated,
            # Status
            "forecast_status": "draft",
            "calibrated": self.calibrated,
        }
        return forecast

    def _determine_winner(self, diag: dict) -> str:
        if diag["block_margin"] > 0:
            return "right"
        elif diag["block_margin"] < 0:
            return "left"
        return "tie"

    def _win_probability(self, diag: dict) -> Optional[float]:
        """
        Return calibrated probability of right-block winning.

        Only if calibration data exists; otherwise None.
        """
        if not self.calibrated:
            return None
        # Simple logistic placeholder — must be replaced by fitted model
        # when calibration data is available
        psi = diag["psi"]
        # logistic: p = 1 / (1 + exp(-k*(psi-0.5)))
        import math
        k = 20.0
        return round(1.0 / (1.0 + math.exp(-k * (psi - 0.5))), 4)
