"""Reusable Streamlit UI components for PollShift."""

from __future__ import annotations
import streamlit as st
from typing import Dict, Optional

from config import PARTY_NAMES, PARTY_COLORS, LEFT_BLOCK, RIGHT_BLOCK, APP_MODE, APP_VERSION, GTT_VERSION


def render_mode_banner() -> None:
    if APP_MODE == "demo":
        st.warning("⚠️ DEMO-LÄGE — Visar syntetisk exempeldata. Inga verkliga prognoser.")
    elif APP_MODE == "internal":
        st.info("🔬 INTERNT LÄGE — Experimentella diagnostik visas.")


def render_header() -> None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🗳️ PollShift")
        st.caption("Valprognoser med Geometric Threshold Theory · FieldShift Research Institute")
    with col2:
        st.caption(f"v{APP_VERSION} · GTT {GTT_VERSION}")
        st.caption("Scientific Election Intelligence")


def forecast_status_badge(status: str) -> str:
    colors = {
        "draft":     "🔵 Utkast",
        "internal":  "🟡 Intern",
        "locked":    "🔐 Låst",
        "public":    "🟢 Publik",
        "evaluated": "✅ Utvärderad",
    }
    return colors.get(status, status)


def render_main_forecast_card(forecast: dict) -> None:
    diag = forecast.get("diagnostics", {})
    winner = forecast.get("predicted_winner", "?")
    win_prob = forecast.get("win_probability")
    calibrated = forecast.get("win_probability_calibrated", False)

    winner_label = {
        "left":  "🔴 Vänsterblock",
        "right": "🔵 Högerblock",
        "tie":   "⚖️ Jämnt",
    }.get(winner, winner)

    with st.container():
        st.subheader("📊 Prognossammanfattning")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Prognostiserat vinnande block", winner_label)
        with col2:
            bm = diag.get("block_margin", 0)
            st.metric("Blockgap", f"{bm:+.2f} pp",
                      help="Höger minus Vänster i procentenheter")
        with col3:
            psi = diag.get("psi", 0.5)
            st.metric("PSI", f"{psi:.3f}",
                      help="Pressure Sensitivity Index. 0.5 = tröskelzon.")
        with col4:
            st.metric("GTT-zon", diag.get("zone_label", "—"))

        col5, col6, col7 = st.columns(3)
        with col5:
            dist = diag.get("distance_to_threshold", 0)
            st.metric("Avstånd till tröskel", f"{dist:.3f}")
        with col6:
            if win_prob is not None and calibrated:
                st.metric("Kalibrerad vinstsannolikhet",
                          f"{win_prob * 100:.1f}%",
                          help="Högerblockets sannolikhet att vinna")
            else:
                st.metric("Kalibrerad vinstsannolikhet", "Kalibrering pågår")
        with col7:
            status = forecast.get("forecast_status", "draft")
            st.metric("Prognosstatus", forecast_status_badge(status))


def render_party_table(
    shares: Dict[str, float],
    momentum: Optional[Dict[str, float]],
    uncertainty: Optional[Dict[str, tuple]],
    mandates: Optional[Dict[str, int]],
) -> None:
    import pandas as pd

    rows = []
    for p in [*LEFT_BLOCK, *RIGHT_BLOCK]:
        block = "Vänster" if p in LEFT_BLOCK else "Höger"
        m = momentum.get(p, 0.0) if momentum else 0.0
        mom_arrow = "▲" if m > 0.1 else ("▼" if m < -0.1 else "→")
        ui = uncertainty.get(p, (None, None)) if uncertainty else (None, None)
        ui_str = f"[{ui[0]:.1f}, {ui[1]:.1f}]" if ui[0] is not None else "—"
        seats = mandates.get(p, "—") if mandates else "—"
        rows.append({
            "Parti": PARTY_NAMES.get(p, p),
            "Prognos %": f"{shares.get(p, 0):.1f}%",
            "Förändring": f"{m:+.2f} pp" if momentum else "—",
            "Momentum": mom_arrow,
            "Osäkerhetsintervall": ui_str,
            "Mandat (prel.)": seats,
            "Block": block,
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_gtt_diagnostics(diag: dict, mode: str = "public") -> None:
    st.subheader("🔬 GTT-diagnostik")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("PSI", f"{diag.get('psi', 0):.4f}")
        st.metric("GTT-zon", diag.get("zone_label", "—"))
        st.metric("Avstånd till tröskel", f"{diag.get('distance_to_threshold', 0):.4f}")
        st.metric("Tröskelkänslighet", diag.get("sensitivity_label", "—"))
    with col2:
        st.metric("Strukturell volatilitet", diag.get("volatility_label", "—"))
        risk = diag.get("transition_risk", {})
        st.metric("Övergångsrisk", risk.get("label", "—"))
        bm = diag.get("block_momentum")
        if bm is not None:
            st.metric("Blockmomentum", f"{bm:+.3f} pp")
        else:
            st.metric("Blockmomentum", "Otillräcklig historik")
        calib = diag.get("calibrated", False)
        st.metric("Kalibreringsstatus",
                  "✅ Kalibrerad" if calib else "⏳ Kalibrering pågår")

    if mode == "internal":
        with st.expander("Teknisk diagnostik (internt läge)"):
            st.json({
                "K": diag.get("K"),
                "epsilon": diag.get("epsilon"),
                "volatility_by_party": diag.get("volatility"),
                "transition_risk_components": risk,
                "block_acceleration": diag.get("block_acceleration"),
                "days_to_election": diag.get("days_to_election"),
            })


def render_disclaimer() -> None:
    st.divider()
    st.caption(
        "PollShift är en probabilistisk valprognos baserad på Geometric Threshold Theory. "
        "Opinionsundersökningar kan vara felaktiga. Modellens osäkerhet är verklig. "
        "MAE redovisas från historiska backtests och är inte en garanti om framtida träffsäkerhet. "
        "FieldShift Research Institute · fieldshift.se"
    )
