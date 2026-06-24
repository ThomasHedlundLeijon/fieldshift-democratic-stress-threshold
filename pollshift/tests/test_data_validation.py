"""Tests for data validation module."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.validation import validate_shares


VALID_SHARES = {
    "S": 34.5, "V": 8.9, "C": 5.5, "MP": 4.3,
    "M": 18.9, "SD": 20.1, "KD": 4.0, "L": 3.4,
}


def test_valid_shares_passes():
    ok, issues = validate_shares(VALID_SHARES)
    assert ok
    assert not issues


def test_missing_party_fails():
    bad = {k: v for k, v in VALID_SHARES.items() if k != "S"}
    ok, issues = validate_shares(bad)
    assert not ok
    assert any("S" in i for i in issues)


def test_negative_value_fails():
    bad = {**VALID_SHARES, "S": -1.0}
    ok, issues = validate_shares(bad)
    assert not ok


def test_bad_sum_fails():
    # Sum way off
    bad = {p: 1.0 for p in VALID_SHARES}
    ok, issues = validate_shares(bad)
    assert not ok
    assert any("Summa" in i for i in issues)
