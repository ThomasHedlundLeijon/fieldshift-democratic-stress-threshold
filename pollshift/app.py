"""
PollShift v15.0 — Vetenskapligt spårbar valprognos baserad på Geometric Threshold Theory.

FieldShift Research Institute · Scientific Election Intelligence
"""

from __future__ import annotations
import sys
import os

# Add pollshift directory to path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from datetime import datetime, date

from config import (
    PARTIES, PARTY_NAMES, LEFT_BLOCK, RIGHT_BLOCK,
    APP_MODE, APP_VERSION, GTT_VERSION, ELECTION_DATE,
    GTT_K_DEFAULT, GTT_EPSILON,
)
from data.collector import load_polls, aggregate_shares, get_sources_meta
from data.validation import validate_shares
from data.quality import assess_quality
from data.historical_loader import load_historical
from gtt.state_vector import StateVector
from models.forecast_engine import GTTForecastEngine
from models.calibration import CalibrationEngine
from models.scenario_engine import run_scenario, PRESET_SCENARIOS
from models.mandate_model import MANDATE_DISCLAIMER
from audit.forecast_lock import ForecastLock
from audit.hash_chain import HashChain
from audit.snapshot import create_snapshot, load_snapshots
from ui.components import (
    render_mode_banner, render_header,
    render_main_forecast_card, render_party_table,
    render_gtt_diagnostics, render_disclaimer,
    forecast_status_badge,
)
from ui.charts import (
    party_bar_chart, block_gauge, timeline_chart,
    party_trend_chart, block_pie, calibration_curve,
)
from ui.transparency import render_method_page

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PollShift · Valprognos",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state["history"] = []   # list of diagnostic dicts

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=PollShift", use_column_width=True)
    st.markdown("**FieldShift Research Institute**")
    st.caption("Vetenskapligt spårbar valprognos baserad på Geometric Threshold Theory.")
    st.divider()

    pages = [
        "📊 Prognos",
        "🔬 GTT-diagnostik",
        "📈 Scenario-explorer",
        "📚 Backtest",
        "🗃️ Prognosarkiv",
        "🔗 Hashkedja",
        "📖 Metod & Begränsningar",
    ]
    page = st.radio("Navigation", pages, label_visibility="collapsed")

    st.divider()
    mode_label = {"demo": "Demo", "internal": "Intern", "public": "Publik"}.get(APP_MODE, APP_MODE)
    st.caption(f"Läge: **{mode_label}** · v{APP_VERSION} · GTT {GTT_VERSION}")
    days_left = (date.fromisoformat(ELECTION_DATE) - date.today()).days
    st.caption(f"Dagar till valet: **{days_left}** ({ELECTION_DATE})")

# ── Header ────────────────────────────────────────────────────────────────────
render_mode_banner()
render_header()

# ── Load data ─────────────────────────────────────────────────────────────────
polls = load_polls()
shares = aggregate_shares(polls)
sources = get_sources_meta(polls)
is_valid, validation_issues = validate_shares(shares)
quality = assess_quality(sources, shares)
historical = load_historical()

# ── Calibration ───────────────────────────────────────────────────────────────
cal_engine = CalibrationEngine()
cal_results = cal_engine.run()
calibrated = not cal_results.get("calibration_pending", True)

# ── Build StateVector history ─────────────────────────────────────────────────
def _build_vectors_from_polls(polls_list):
    """Build chronologically sorted StateVectors from poll list."""
    sorted_polls = sorted(polls_list, key=lambda p: p.get("date", ""))
    vectors = []
    for p in sorted_polls:
        sv = StateVector(
            shares=p["shares"],
            timestamp=p.get("date", ""),
            source_ids=[p["id"]],
            snapshot_id=p["id"],
        )
        vectors.append(sv)
    return vectors

vectors = _build_vectors_from_polls(polls)
if not vectors:
    # Fallback: single vector from aggregated shares
    vectors = [StateVector(shares=shares, timestamp=datetime.utcnow().isoformat())]

# ── Forecast engine ───────────────────────────────────────────────────────────
engine = GTTForecastEngine(
    K=GTT_K_DEFAULT,
    epsilon=GTT_EPSILON,
    calibrated=calibrated,
    calibration_results=cal_results,
)
forecast = engine.forecast(vectors)
diag = forecast["diagnostics"]

# Store snapshot in history (session)
if not st.session_state["history"] or \
        st.session_state["history"][-1].get("timestamp") != diag.get("timestamp"):
    st.session_state["history"].append(diag)

# ── Shared objects ────────────────────────────────────────────────────────────
lock = ForecastLock()
chain = HashChain()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📊 Prognos":
    # ── Data quality warning ──────────────────────────────────────────────────
    if not is_valid:
        st.error("⚠️ Datavalideringsfel: " + "; ".join(validation_issues))
    if quality.get("stale_warning"):
        st.warning(f"⚠️ Inaktuella källor: {', '.join(quality['stale_sources'])}")
    if APP_MODE == "demo":
        st.info("📌 Visad data är syntetiska demosiffror — inte verkliga opinionsundersökningar.")

    # ── Main forecast card ────────────────────────────────────────────────────
    render_main_forecast_card(forecast)

    st.divider()
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(block_gauge(diag["psi"]), use_container_width=True)
    with col_right:
        st.plotly_chart(
            block_pie(diag["left_total"], diag["right_total"]),
            use_container_width=True,
        )

    # ── Party bar chart ───────────────────────────────────────────────────────
    st.plotly_chart(party_bar_chart(diag["party_shares"]), use_container_width=True)

    # ── Party forecast table ──────────────────────────────────────────────────
    st.subheader("📋 Partiprognos")
    render_party_table(
        shares=diag["party_shares"],
        momentum=diag.get("party_momentum"),
        uncertainty=forecast.get("party_uncertainty"),
        mandates=forecast.get("party_mandates"),
    )
    st.caption(f"⚠️ {MANDATE_DISCLAIMER}")

    # ── Block summary ─────────────────────────────────────────────────────────
    st.subheader("🏛️ Blocköversikt")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Vänsterblock", f"{diag['left_total']:.1f}%")
        st.metric("Vänster mandat", forecast.get("left_mandates", "—"))
    with col2:
        st.metric("Högerblock", f"{diag['right_total']:.1f}%")
        st.metric("Höger mandat", forecast.get("right_mandates", "—"))
    with col3:
        bm = diag["block_margin"]
        st.metric("Blockgap", f"{bm:+.2f} pp")
    with col4:
        wp = forecast.get("win_probability")
        if wp is not None and calibrated:
            st.metric("Kalibrerad vinstsannolikhet (H)", f"{wp*100:.1f}%")
        else:
            st.metric("Kalibrerad vinstsannolikhet", "Kalibrering pågår")

    # ── Timeline ──────────────────────────────────────────────────────────────
    if len(vectors) > 1:
        st.subheader("📈 Trender")
        hist_diags = []
        for sv in vectors:
            from gtt.diagnostics import run_diagnostics
            d = run_diagnostics([sv], K=GTT_K_DEFAULT, epsilon=GTT_EPSILON)
            d["timestamp"] = sv.timestamp
            d["party_shares"] = sv.shares
            hist_diags.append(d)

        tab1, tab2, tab3 = st.tabs(["Partitrend", "Blockgap", "PSI"])
        with tab1:
            st.plotly_chart(party_trend_chart(hist_diags), use_container_width=True)
        with tab2:
            st.plotly_chart(timeline_chart(hist_diags, "block_margin"), use_container_width=True)
        with tab3:
            st.plotly_chart(timeline_chart(hist_diags, "psi"), use_container_width=True)

    # ── Data quality card ─────────────────────────────────────────────────────
    with st.expander("🔍 Datakvalitet"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Antal källor", quality["n_sources"])
            st.metric("Senaste uppdatering", quality["last_update"] or "—")
        with col2:
            st.metric("Aktualitetspoäng", f"{quality['recency_score']:.2f}")
            st.metric("Tillförlitlighetspoäng", f"{quality['reliability_score']:.2f}")
        with col3:
            st.metric("Summavalidering", "✅ OK" if quality["sum_valid"] else "❌ Fel")
            near = quality.get("near_threshold_parties", [])
            st.metric("Partier nära spärren",
                      ", ".join(PARTY_NAMES.get(p, p) for p in near) if near else "Inga")

    # ── Lock forecast (internal/public) ───────────────────────────────────────
    if APP_MODE in ("internal", "public"):
        with st.expander("🔐 Lås prognos"):
            status_choice = st.selectbox("Prognosstatus",
                                         ["draft", "internal", "locked", "public"])
            if st.button("Lås och arkivera prognos"):
                locked = lock.lock(forecast, status=status_choice)
                st.success(f"Prognos låst. ID: `{locked['forecast_id']}`")
                st.code(f"Hash: {locked['forecast_hash']}", language="text")

    render_disclaimer()


elif page == "🔬 GTT-diagnostik":
    render_gtt_diagnostics(diag, mode=APP_MODE)
    render_disclaimer()


elif page == "📈 Scenario-explorer":
    st.header("📈 Scenario-explorer")
    st.caption("Utforska hur förändringar i partiernas stöd påverkar PSI, blockresultat och mandat.")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        preset = st.selectbox("Välj förinställt scenario", list(PRESET_SCENARIOS.keys()))
        base_adjustments = PRESET_SCENARIOS[preset]

        st.subheader("Manuella justeringar")
        adjustments: dict = {}
        for p in PARTIES:
            delta = st.slider(
                PARTY_NAMES.get(p, p),
                min_value=-10.0, max_value=10.0,
                value=float(base_adjustments.get(p, 0.0)),
                step=0.5, key=f"scenario_{p}",
            )
            if delta != 0:
                adjustments[p] = delta

    result = run_scenario(
        base_shares=shares,
        adjustments=adjustments or base_adjustments,
        K=GTT_K_DEFAULT, epsilon=GTT_EPSILON,
    )

    with col_right:
        s_diag = result["diagnostics"]
        s_shares = result["scenario_shares"]
        bm_s = result["block_mandates"]

        st.subheader("Scenarioresultat")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("PSI (scenario)", f"{s_diag['psi']:.4f}",
                      delta=f"{s_diag['psi'] - diag['psi']:+.4f}")
            st.metric("GTT-zon", s_diag["zone_label"])
        with col2:
            bm = s_diag["block_margin"]
            st.metric("Blockgap", f"{bm:+.2f} pp",
                      delta=f"{bm - diag['block_margin']:+.2f}")
        with col3:
            winner = result["diagnostics"]["transition_risk"]["label"]
            st.metric("Prognostiserat block",
                      "🔵 Höger" if bm > 0 else "🔴 Vänster")

        st.plotly_chart(party_bar_chart(s_shares, "Partiernas stöd (scenario)"),
                        use_container_width=True)

        cols = st.columns(4)
        for i, p in enumerate(LEFT_BLOCK + RIGHT_BLOCK):
            with cols[i % 4]:
                delta = s_shares.get(p, 0) - shares.get(p, 0)
                st.metric(PARTY_NAMES.get(p, p),
                          f"{s_shares.get(p, 0):.1f}%",
                          f"{delta:+.1f} pp")

        st.caption(f"⚠️ {MANDATE_DISCLAIMER}")
        st.metric("Höger mandat (prel.)", bm_s["right"])
        st.metric("Vänster mandat (prel.)", bm_s["left"])


elif page == "📚 Backtest":
    st.header("📚 Backtest & Historisk kalibrering")

    if cal_results.get("calibration_pending"):
        st.warning("⏳ Kalibrering pågår — historisk data saknas.")
        st.info("Lägg till historiska valresultat och opinionsundersökningar i "
                "`data/historical_elections.json` och `data/polls.json` för att aktivera backtest.")
    else:
        st.success(f"✅ Kalibrering beräknad från {cal_results.get('n_elections')} val "
                   f"och {cal_results.get('n_poll_snapshots')} opinionsundersökningar.")

        col1, col2, col3 = st.columns(3)
        with col1:
            mae = cal_results.get("overall_mae")
            st.metric("Övergripande MAE",
                      f"{mae:.4f} pp" if mae == mae else "—")
        with col2:
            win_acc = cal_results.get("win_accuracy")
            st.metric("Vinnarprognosens träffsäkerhet",
                      f"{win_acc*100:.1f}%" if win_acc is not None else "—")
        with col3:
            st.metric("Kalibreringsstatus", cal_results.get("calibration_version", "—"))

        if cal_results.get("bucket_mae"):
            st.plotly_chart(calibration_curve(cal_results["bucket_mae"]),
                            use_container_width=True)

        with st.expander("MAE per parti"):
            import pandas as pd
            df = pd.DataFrame([
                {"Parti": PARTY_NAMES.get(p, p), "MAE (pp)": v}
                for p, v in cal_results.get("party_mae", {}).items()
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

        with st.expander("MAE per block"):
            block_mae = cal_results.get("block_mae", {})
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Vänsterblock MAE", f"{block_mae.get('left', float('nan')):.4f} pp")
            with col2:
                st.metric("Högerblock MAE", f"{block_mae.get('right', float('nan')):.4f} pp")

    # Historical elections reference table
    st.subheader("Historiska valresultat (referensdata)")
    import pandas as pd
    hist_rows = []
    for e in historical:
        s = e.get("actual_shares", {})
        left = sum(s.get(p, 0) for p in LEFT_BLOCK)
        right = sum(s.get(p, 0) for p in RIGHT_BLOCK)
        hist_rows.append({
            "Val": e["id"], "Datum": e.get("date", ""),
            "Vänster %": f"{left:.1f}", "Höger %": f"{right:.1f}",
            "Blockgap": f"{right-left:+.1f}",
            "Vinnare": "Höger" if e.get("winner") == "right" else "Vänster",
        })
    if hist_rows:
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)


elif page == "🗃️ Prognosarkiv":
    st.header("🗃️ Prognosarkiv")
    archive = lock.get_archive()

    if not archive:
        st.info("Inga låsta prognoser ännu. Lås en prognos från Prognossidan.")
    else:
        import pandas as pd
        rows = []
        for e in archive:
            rows.append({
                "Prognos-ID": e.get("forecast_id", "")[:8] + "…",
                "Datum": e.get("timestamp", "")[:10],
                "Vinnare": e.get("predicted_winner", "—"),
                "PSI": e.get("psi", "—"),
                "Hash (kort)": (e.get("forecast_hash") or "")[:12] + "…",
                "Status": forecast_status_badge(e.get("status", "draft")),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        selected_id = st.text_input("Verifiera prognos-ID (klistra in fullständigt ID):")
        if selected_id:
            result = lock.verify(selected_id)
            if result.get("valid"):
                st.success(f"✅ Prognosen är giltig. Hash: `{result['stored_hash'][:20]}…`")
            else:
                st.error(f"❌ Verifiering misslyckades: {result.get('error', 'Hash mismatch')}")


elif page == "🔗 Hashkedja":
    st.header("🔗 Kryptografisk hashkedja")
    st.caption("Tamper-evident audit trail för alla prognoser.")

    verify = chain.verify_chain()
    if verify["valid"]:
        st.success(f"✅ Kedjan är giltig. {verify['entries']} poster verifierade.")
    else:
        st.error(f"❌ Kedjeavvikelse detekterad: {verify['message']}")
        for err in verify.get("errors", []):
            st.warning(err)

    recent = chain.get_recent(10)
    if recent:
        st.subheader("Senaste poster")
        import pandas as pd
        rows = []
        for e in recent:
            rows.append({
                "Snapshot-ID": str(e.get("snapshot_id", ""))[:12] + "…",
                "Tidpunkt": str(e.get("timestamp", ""))[:19],
                "Aktuell hash": str(e.get("current_hash") or "")[:20] + "…",
                "Föregående hash": str(e.get("previous_hash") or "genesis")[:20] + "…",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        latest = recent[-1]
        with st.expander("Senaste post (full)"):
            st.json(latest)
    else:
        st.info("Kedjan är tom — inga poster ännu.")


elif page == "📖 Metod & Begränsningar":
    render_method_page()

render_disclaimer()
