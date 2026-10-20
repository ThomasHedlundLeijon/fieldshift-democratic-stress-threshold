"""
Forecast locking module.

Every public forecast is assigned:
  - forecast_id
  - SHA-256 hash of all inputs + outputs
  - previous forecast hash (chain integrity)
  - status: draft → internal → locked → public → evaluated
"""

from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import (
    APP_VERSION, GTT_VERSION, CALIBRATION_VERSION,
    FORECAST_ARCHIVE, PSI_ZONES,
)
from audit.hash_chain import compute_hash, HashChain


VALID_STATUSES = ["draft", "internal", "locked", "public", "evaluated"]


class ForecastLock:
    def __init__(
        self,
        archive_file: Path = FORECAST_ARCHIVE,
        chain: Optional[HashChain] = None,
    ) -> None:
        self.archive_file = archive_file
        self.chain = chain or HashChain()

    def _load_archive(self) -> list:
        if not self.archive_file.exists():
            return []
        entries = []
        with open(self.archive_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def get_previous_hash(self) -> Optional[str]:
        entries = self._load_archive()
        if not entries:
            return None
        return entries[-1]["forecast_hash"]

    def lock(self, forecast: dict, status: str = "locked") -> dict:
        """
        Create a locked forecast record with SHA-256 hash.

        The hash covers all inputs and outputs — any modification
        changes the hash, making tampering detectable.
        """
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        forecast_id = str(uuid.uuid4())
        previous_hash = self.get_previous_hash()
        timestamp = datetime.utcnow().isoformat() + "Z"

        locked_payload = {
            "forecast_id": forecast_id,
            "model_version": APP_VERSION,
            "gtt_version": GTT_VERSION,
            "calibration_version": forecast.get("calibration_version", CALIBRATION_VERSION),
            "election_id": forecast.get("election_id", ""),
            "timestamp": timestamp,
            "party_shares": forecast.get("party_shares", {}),
            "left_pct": forecast.get("left_pct"),
            "right_pct": forecast.get("right_pct"),
            "block_margin": forecast.get("block_margin"),
            "psi": forecast.get("diagnostics", {}).get("psi"),
            "zone": forecast.get("diagnostics", {}).get("zone_key"),
            "zones_used": PSI_ZONES,
            "predicted_winner": forecast.get("predicted_winner"),
            "win_probability": forecast.get("win_probability"),
            "previous_forecast_hash": previous_hash,
        }

        forecast_hash = compute_hash(locked_payload)
        locked_payload["forecast_hash"] = forecast_hash
        locked_payload["status"] = status

        with open(self.archive_file, "a") as f:
            f.write(json.dumps(locked_payload, ensure_ascii=False) + "\n")

        # Also append to hash chain
        self.chain.append(snapshot_id=forecast_id, payload=locked_payload)

        return locked_payload

    def verify(self, forecast_id: str) -> dict:
        """Verify a locked forecast by re-computing its hash."""
        for entry in self._load_archive():
            if entry["forecast_id"] == forecast_id:
                stored_hash = entry.pop("forecast_hash", None)
                status = entry.pop("status", None)
                recomputed = compute_hash(entry)
                return {
                    "forecast_id": forecast_id,
                    "valid": recomputed == stored_hash,
                    "stored_hash": stored_hash,
                    "recomputed_hash": recomputed,
                    "status": status,
                }
        return {"forecast_id": forecast_id, "valid": False, "error": "Hittades ej."}

    def get_archive(self) -> list:
        return self._load_archive()

    def update_status(self, forecast_id: str, new_status: str) -> bool:
        """Update status field in archive (does not recompute hash)."""
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        entries = self._load_archive()
        updated = False
        for e in entries:
            if e["forecast_id"] == forecast_id:
                e["status"] = new_status
                updated = True
        if updated:
            with open(self.archive_file, "w") as f:
                for e in entries:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return updated
