"""Tests for mandate calculation model."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.mandate_model import compute_mandates, block_mandates
from config import SEATS_TOTAL, PARTIES


DEMO_SHARES = {
    "S": 34.5, "V": 8.9, "C": 5.5, "MP": 4.3,
    "M": 18.9, "SD": 20.1, "KD": 4.0, "L": 3.4,
}


def test_total_mandates():
    mandates = compute_mandates(DEMO_SHARES)
    assert sum(mandates.values()) == SEATS_TOTAL


def test_below_threshold_gets_zero():
    shares = {**DEMO_SHARES, "L": 2.0}  # L below 4%
    mandates = compute_mandates(shares)
    assert mandates["L"] == 0


def test_all_parties_present():
    mandates = compute_mandates(DEMO_SHARES)
    assert set(mandates.keys()) == set(PARTIES)


def test_block_mandates_sum():
    mandates = compute_mandates(DEMO_SHARES)
    bm = block_mandates(mandates)
    assert bm["left"] + bm["right"] == SEATS_TOTAL


def test_mandates_deterministic():
    m1 = compute_mandates(DEMO_SHARES)
    m2 = compute_mandates(DEMO_SHARES)
    assert m1 == m2
