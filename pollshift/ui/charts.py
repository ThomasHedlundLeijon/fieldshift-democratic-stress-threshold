"""Plotly chart builders for PollShift."""

from __future__ import annotations
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config import PARTIES, PARTY_NAMES, PARTY_COLORS, LEFT_BLOCK, RIGHT_BLOCK


def party_bar_chart(shares: Dict[str, float], title: str = "Partiernas stöd (%)") -> go.Figure:
    parties = [p for p in PARTIES]
    values = [shares.get(p, 0.0) for p in parties]
    colors = [PARTY_COLORS.get(p, "#999") for p in parties]
    labels = [PARTY_NAMES.get(p, p) for p in parties]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
    ))
    fig.add_hline(y=4.0, line_dash="dash", line_color="red",
                  annotation_text="4% spärr", annotation_position="top right")
    fig.update_layout(
        title=title,
        yaxis=dict(title="%", range=[0, max(values) * 1.2]),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=350,
        margin=dict(t=50, b=10),
    )
    return fig


def block_gauge(psi: float) -> go.Figure:
    """Gauge chart showing PSI with zone coloring."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(psi * 100, 1),
        delta={"reference": 50},
        title={"text": "PSI — Structural Pressure Index"},
        gauge={
            "axis": {"range": [0, 100], "tickvals": [0, 42, 48, 52, 58, 100]},
            "bar": {"color": "black", "thickness": 0.15},
            "steps": [
                {"range": [0, 42],  "color": "#C62828"},
                {"range": [42, 48], "color": "#EF9A9A"},
                {"range": [48, 52], "color": "#FFF176"},
                {"range": [52, 58], "color": "#90CAF9"},
                {"range": [58, 100],"color": "#1565C0"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 3},
                "thickness": 0.8,
                "value": 50,
            },
        },
        number={"suffix": "", "font": {"size": 28}},
    ))
    fig.update_layout(height=280, margin=dict(t=60, b=10))
    return fig


def timeline_chart(history: List[dict], metric: str = "block_margin") -> go.Figure:
    """Plot a metric over time from a list of diagnostic snapshots."""
    if not history:
        fig = go.Figure()
        fig.update_layout(title="Ingen historik tillgänglig")
        return fig

    dates = [h.get("timestamp", "")[:10] for h in history]

    if metric == "block_margin":
        values = [h.get("block_margin", 0) for h in history]
        title = "Blockgap (Höger − Vänster)"
        yaxis = "Procentenheter"
    elif metric == "psi":
        values = [h.get("psi", 0.5) for h in history]
        title = "PSI över tid"
        yaxis = "PSI"
    else:
        values = [h.get(metric, 0) for h in history]
        title = metric
        yaxis = metric

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=values, mode="lines+markers",
        line=dict(color="#1B49A4", width=2),
        marker=dict(size=6),
    ))

    if metric == "psi":
        fig.add_hline(y=0.5, line_dash="dash", line_color="gray",
                      annotation_text="Tröskel (0.5)")
    elif metric == "block_margin":
        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                      annotation_text="Jämvikt")

    fig.update_layout(
        title=title,
        yaxis=dict(title=yaxis),
        xaxis=dict(title="Datum"),
        height=300,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=10),
    )
    return fig


def party_trend_chart(history: List[dict], parties: Optional[List[str]] = None) -> go.Figure:
    """Multi-line chart of party shares over time."""
    if not history:
        fig = go.Figure()
        fig.update_layout(title="Ingen historik")
        return fig

    target = parties or PARTIES
    dates = [h.get("timestamp", "")[:10] for h in history]

    fig = go.Figure()
    for p in target:
        values = [h.get("party_shares", {}).get(p, 0) for h in history]
        fig.add_trace(go.Scatter(
            x=dates, y=values,
            name=PARTY_NAMES.get(p, p),
            mode="lines+markers",
            line=dict(color=PARTY_COLORS.get(p, "#999"), width=2),
        ))

    fig.add_hline(y=4.0, line_dash="dot", line_color="red",
                  annotation_text="4% spärr")
    fig.update_layout(
        title="Partiernas stöd över tid",
        yaxis=dict(title="%", range=[0, 45]),
        height=350,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=10),
    )
    return fig


def block_pie(left_pct: float, right_pct: float) -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=["Vänsterblock", "Högerblock"],
        values=[left_pct, right_pct],
        marker_colors=["#C62828", "#1565C0"],
        hole=0.5,
        textinfo="label+percent",
    ))
    fig.update_layout(
        height=280,
        margin=dict(t=30, b=10),
        showlegend=False,
    )
    return fig


def calibration_curve(bucket_mae: dict) -> go.Figure:
    """MAE by days-before-election bucket."""
    labels = list(bucket_mae.keys())
    values = [v if v == v else 0 for v in bucket_mae.values()]  # NaN → 0
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color="#1B49A4",
        text=[f"{v:.3f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="MAE per tidsfönster",
        yaxis=dict(title="MAE (procentenheter)"),
        height=300,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=10),
    )
    return fig
