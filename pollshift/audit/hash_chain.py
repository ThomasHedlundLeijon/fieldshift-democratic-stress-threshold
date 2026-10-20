"""
Hash chain implementation for GTT forecast evidence trail.

Each snapshot references previous_hash, forming a tamper-evident chain.
"""

from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Optional

from config import HASH_CHAIN_FILE


def _stable_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def compute_hash(payload: dict) -> str:
    """Deterministic SHA-256 of a dict (sorted keys)."""
    raw = _stable_json(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class HashChain:
    def __init__(self, chain_file: Path = HASH_CHAIN_FILE) -> None:
        self.chain_file = chain_file

    def _load_entries(self) -> list:
        if not self.chain_file.exists():
            return []
        entries = []
        with open(self.chain_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def get_last_hash(self) -> Optional[str]:
        entries = self._load_entries()
        if not entries:
            return None
        return entries[-1]["current_hash"]

    def append(self, snapshot_id: str, payload: dict) -> dict:
        """
        Append a new entry to the hash chain.

        Computes current_hash from payload + previous_hash.
        Returns the full chain entry.
        """
        previous_hash = self.get_last_hash()

        # Include previous_hash in the hashed content so chain is linked
        hashable = {
            "snapshot_id": snapshot_id,
            "previous_hash": previous_hash,
            "payload": payload,
        }
        current_hash = compute_hash(hashable)

        entry = {
            "snapshot_id": snapshot_id,
            "timestamp": payload.get("timestamp", ""),
            "previous_hash": previous_hash,
            "current_hash": current_hash,
        }

        with open(self.chain_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def verify_chain(self) -> dict:
        """
        Verify integrity of the full hash chain.

        Returns verification result dict.
        """
        entries = self._load_entries()
        if not entries:
            return {"valid": True, "entries": 0, "message": "Kedjan är tom."}

        errors = []
        for i, entry in enumerate(entries):
            # Re-derive expected previous hash
            expected_prev = entries[i - 1]["current_hash"] if i > 0 else None
            if entry["previous_hash"] != expected_prev:
                errors.append(f"Kedjebrott vid position {i}: {entry['snapshot_id']}")

        return {
            "valid": len(errors) == 0,
            "entries": len(entries),
            "errors": errors,
            "message": "Kedjan är giltig." if not errors else f"{len(errors)} kedjebrotts hittades.",
            "latest_hash": entries[-1]["current_hash"] if entries else None,
        }

    def get_recent(self, n: int = 10) -> list:
        return self._load_entries()[-n:]
