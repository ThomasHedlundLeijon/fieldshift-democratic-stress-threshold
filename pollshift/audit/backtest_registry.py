"""Backtest registry — stores and retrieves historical backtest results."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

from config import BACKTEST_FILE


def load_backtest() -> Optional[dict]:
    if BACKTEST_FILE.exists():
        with open(BACKTEST_FILE) as f:
            return json.load(f)
    return None


def save_backtest(results: dict) -> None:
    with open(BACKTEST_FILE, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
