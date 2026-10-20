"""Transparency and method pages for PollShift."""

from __future__ import annotations
import streamlit as st

from config import APP_VERSION, GTT_VERSION, APP_MODE


def render_method_page() -> None:
    st.header("📖 Metod & Begränsningar")

    st.markdown("""
    ### Geometric Threshold Theory (GTT)

    PollShift använder Geometric Threshold Theory som kärnmodell för valprognos.
    GTT modellerar valsystemet som ett strukturellt tröskelssystem där:

    - **Politisk tillståndsvektorn P_t** representerar partiernas opinionsstöd vid tidpunkt t
    - **Blockmarginalen B_t = R_t − L_t** mäter högerblockets strukturella fördel
    - **PSI (Pressure Sensitivity Index)** normaliserar blockmarginalen till [0, 1]
    - **Tröskelzoner** klassificerar systemets strukturella läge

    GTT förutsäger inte enskilda partiresultat mekanistiskt.
    Teorin identifierar strukturella trender och tröskelkänslighet.

    ---

    ### Kalibrering

    MAE och övriga noggrannhetsmått beräknas **uteslutande** från historiska backtests.
    Inga noggrannhetspåståenden görs utan empirisk beräkning.

    Om historisk data saknas visas: **"Kalibrering pågår"**.

    ---

    ### Begränsningar

    - Opinionsundersökningar innehåller systematiska och slumpmässiga fel
    - Modellen fångar inte strukturella förändringar som sker utan varsel
    - Mandatberäkningen är förenklad (se not i partitabellen)
    - Historisk träffsäkerhet är inte en garanti för framtida prestanda
    - PSI-kalibreringskonstanten K estimeras från begränsad historisk data

    ---

    ### Reproducerbarhet

    Varje prognos låses med ett SHA-256-hashvärde.
    Samma indata ger alltid samma utdata.
    Kryptografisk hashkedja möjliggör granskning av prognoshistorik.

    ---

    ### Modellversion
    """)

    st.code(f"PollShift v{APP_VERSION} · GTT {GTT_VERSION} · Läge: {APP_MODE}", language="text")
