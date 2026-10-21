"""Tests for tactical voting (stödröstning) model."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gtt.tactical_voting import (
    threshold_risk_score,
    estimate_tactical_inflow,
    adjust_shares_for_tactical_voting,
    run_tactical_adjustment,
    SE2022_TACTICAL_CALIBRATION,
    PARLIAMENTARY_THRESHOLD,
)


# SE-2022 demo shares (L at 3.5% = below threshold)
SE2022_ORGANIC = {
    "S": 30.33, "V": 6.75, "C": 6.71, "MP": 5.08,
    "M": 19.95, "SD": 20.89, "KD": 5.34, "L": 3.53,
}

# Safe shares — all parties well above threshold
SAFE_SHARES = {
    "S": 32.0, "V": 8.0, "C": 7.0, "MP": 5.5,
    "M": 20.0, "SD": 18.0, "KD": 5.5, "L": 5.0,
}


def test_threshold_risk_below_threshold():
    """Party below 4% should have high risk score."""
    risk = threshold_risk_score(3.5)
    assert risk > 0.5, f"Expected high risk for 3.5%, got {risk}"


def test_threshold_risk_safe():
    """Party well above threshold should have zero risk."""
    assert threshold_risk_score(7.0) == 0.0
    assert threshold_risk_score(20.0) == 0.0


def test_threshold_risk_at_threshold():
    """Party exactly at 4% should have low but nonzero risk."""
    risk = threshold_risk_score(PARLIAMENTARY_THRESHOLD)
    assert 0.0 <= risk < 0.3


def test_tactical_inflow_when_below_threshold():
    """L at 3.5% should receive positive tactical inflow."""
    inflows = estimate_tactical_inflow(SE2022_ORGANIC, donor_willingness=0.04)
    assert inflows["L"] > 0, f"Expected inflow for L, got {inflows['L']}"


def test_no_tactical_inflow_when_safe():
    """No party should receive tactical inflow when all are safe."""
    inflows = estimate_tactical_inflow(SAFE_SHARES, donor_willingness=0.04)
    assert all(v < 0.01 for v in inflows.values()), \
        f"Unexpected inflow in safe scenario: {inflows}"


def test_adjusted_shares_lift_l_above_threshold():
    """After adjustment, L should cross 4% threshold in SE-2022 scenario."""
    result = run_tactical_adjustment(SE2022_ORGANIC, donor_willingness=0.04, calibrated=False)
    adj = result["adjusted_shares"]
    assert adj["L"] >= PARLIAMENTARY_THRESHOLD, \
        f"L at {adj['L']:.3f}% — expected >= {PARLIAMENTARY_THRESHOLD}%"


def test_adjusted_shares_sum_preserved():
    """Total adjusted shares should remain close to original total."""
    result = run_tactical_adjustment(SE2022_ORGANIC)
    original_total = sum(SE2022_ORGANIC.values())
    adjusted_total = sum(result["adjusted_shares"].values())
    assert abs(original_total - adjusted_total) < 0.5, \
        f"Share total drifted: {original_total:.2f} → {adjusted_total:.2f}"


def test_donor_shares_decrease():
    """Donor party (M) should lose share when transferring to L."""
    result = run_tactical_adjustment(SE2022_ORGANIC, donor_willingness=0.04)
    adj = result["adjusted_shares"]
    assert adj["M"] < SE2022_ORGANIC["M"], \
        "M should lose share as a donor party"


def test_se2022_calibration_reference():
    """SE-2022 calibration object has correct values."""
    cal = SE2022_TACTICAL_CALIBRATION
    assert cal["organic_L"] < PARLIAMENTARY_THRESHOLD
    assert cal["final_L"] > PARLIAMENTARY_THRESHOLD
    assert cal["final_L"] - cal["organic_L"] == cal["tactical_inflow_total"]
    assert cal["actual_block_margin_mandates"] == 3
    assert cal["mandate_swing_due_to_tactical"] == 17


def test_result_structure():
    """run_tactical_adjustment returns all required keys."""
    result = run_tactical_adjustment(SE2022_ORGANIC)
    for key in ("adjusted_shares", "inflows", "threshold_risks", "at_risk_parties"):
        assert key in result, f"Missing key: {key}"
