"""GTT State Vector — normalised party vote-share representation."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

from config import PARTIES, LEFT_BLOCK, RIGHT_BLOCK, PARLIAMENTARY_THRESHOLD


@dataclass
class StateVector:
    """Immutable snapshot of party vote shares at time t."""

    shares: Dict[str, float]          # party -> % (0–100)
    timestamp: str = ""
    source_ids: List[str] = field(default_factory=list)
    snapshot_id: str = ""

    def __post_init__(self) -> None:
        # Ensure all configured parties are present
        for p in PARTIES:
            self.shares.setdefault(p, 0.0)
        self.shares = {p: float(v) for p, v in self.shares.items()}

    # ── Normalisation ─────────────────────────────────────────────────────────

    @property
    def total(self) -> float:
        return sum(self.shares[p] for p in PARTIES)

    def normalized(self) -> "StateVector":
        """Return a copy normalized so configured parties sum to 100."""
        t = self.total
        if t == 0:
            raise ValueError("Cannot normalise a zero state vector.")
        scale = 100.0 / t
        return StateVector(
            shares={p: self.shares[p] * scale for p in PARTIES},
            timestamp=self.timestamp,
            source_ids=self.source_ids,
            snapshot_id=self.snapshot_id,
        )

    # ── Block aggregates ──────────────────────────────────────────────────────

    @property
    def left_total(self) -> float:
        return sum(self.shares[p] for p in LEFT_BLOCK)

    @property
    def right_total(self) -> float:
        return sum(self.shares[p] for p in RIGHT_BLOCK)

    @property
    def block_margin(self) -> float:
        """B_t = R_t – L_t. Positive → right advantage."""
        return self.right_total - self.left_total

    # ── Threshold filter ──────────────────────────────────────────────────────

    def above_threshold(self) -> List[str]:
        return [p for p in PARTIES if self.shares[p] >= PARLIAMENTARY_THRESHOLD]

    def below_threshold(self) -> List[str]:
        return [p for p in PARTIES if self.shares[p] < PARLIAMENTARY_THRESHOLD]

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "shares": self.shares,
            "timestamp": self.timestamp,
            "source_ids": self.source_ids,
            "snapshot_id": self.snapshot_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StateVector":
        return cls(
            shares=d["shares"],
            timestamp=d.get("timestamp", ""),
            source_ids=d.get("source_ids", []),
            snapshot_id=d.get("snapshot_id", ""),
        )

    # ── Delta ─────────────────────────────────────────────────────────────────

    def delta(self, previous: "StateVector") -> Dict[str, float]:
        """Return party-level changes M_t = P_t – P_{t-1}."""
        return {p: self.shares[p] - previous.shares.get(p, self.shares[p])
                for p in PARTIES}


def compute_momentum(vectors: List[StateVector]) -> Optional[Dict[str, float]]:
    """Return momentum (latest delta) if ≥2 snapshots available."""
    if len(vectors) < 2:
        return None
    return vectors[-1].delta(vectors[-2])


def compute_acceleration(vectors: List[StateVector]) -> Optional[Dict[str, float]]:
    """Return block acceleration (second derivative of block margin) if ≥3 snapshots."""
    if len(vectors) < 3:
        return None
    d1 = vectors[-1].block_margin - vectors[-2].block_margin
    d0 = vectors[-2].block_margin - vectors[-3].block_margin
    return {"block": d1 - d0}


def compute_volatility(vectors: List[StateVector], window: int = 5) -> Dict[str, float]:
    """Rolling std-dev of each party and block over last `window` snapshots."""
    recent = vectors[-window:]
    vol: Dict[str, float] = {}
    for p in PARTIES:
        series = [v.shares[p] for v in recent]
        vol[p] = float(np.std(series)) if len(series) > 1 else 0.0
    margins = [v.block_margin for v in recent]
    vol["block"] = float(np.std(margins)) if len(margins) > 1 else 0.0
    return vol
