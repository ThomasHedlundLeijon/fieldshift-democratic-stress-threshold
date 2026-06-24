"""Data snapshot management for reproducibility."""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from typing import Dict, List
from pathlib import Path

from audit.hash_chain import compute_hash
from config import DATA_DIR


SNAPSHOT_FILE = DATA_DIR / "snapshots.jsonl"


def create_snapshot(party_shares: Dict[str, float], sources: List[str]) -> dict:
    snapshot_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"
    payload = {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "party_shares": party_shares,
        "sources": sources,
    }
    payload["snapshot_hash"] = compute_hash(payload)

    with open(SNAPSHOT_FILE, "a") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return payload


def load_snapshots() -> list:
    if not SNAPSHOT_FILE.exists():
        return []
    entries = []
    with open(SNAPSHOT_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries
