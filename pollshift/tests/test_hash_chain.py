"""Tests for hash chain integrity."""

import sys, os, tempfile, pathlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from audit.hash_chain import HashChain, compute_hash


@pytest.fixture
def tmp_chain(tmp_path):
    return HashChain(chain_file=tmp_path / "chain.jsonl")


def test_compute_hash_deterministic():
    payload = {"a": 1, "b": "hello"}
    h1 = compute_hash(payload)
    h2 = compute_hash(payload)
    assert h1 == h2


def test_compute_hash_sensitive_to_change():
    h1 = compute_hash({"a": 1})
    h2 = compute_hash({"a": 2})
    assert h1 != h2


def test_empty_chain_verify(tmp_chain):
    result = tmp_chain.verify_chain()
    assert result["valid"] is True
    assert result["entries"] == 0


def test_chain_append_and_verify(tmp_chain):
    tmp_chain.append("snap1", {"timestamp": "2026-01-01", "psi": 0.52})
    tmp_chain.append("snap2", {"timestamp": "2026-01-02", "psi": 0.53})
    result = tmp_chain.verify_chain()
    assert result["valid"] is True
    assert result["entries"] == 2


def test_chain_previous_hash_links(tmp_chain):
    e1 = tmp_chain.append("snap1", {"timestamp": "2026-01-01"})
    e2 = tmp_chain.append("snap2", {"timestamp": "2026-01-02"})
    assert e2["previous_hash"] == e1["current_hash"]


def test_chain_previous_hash_ne_current(tmp_chain):
    """previous_hash must never equal current_hash."""
    e = tmp_chain.append("snap1", {"timestamp": "2026-01-01"})
    # For first entry previous is None, current is a hash
    assert e["previous_hash"] != e["current_hash"]
