# FieldShift Dashboard v5 — Pre-submission version

This dashboard is a working operational prototype that accompanies the
manuscript. It demonstrates the practical application envisioned for the
geometric early-warning framework: an interactive, country-level
visualization of democratic stress, recovery-erosion asymmetry, and
red-flag indicator monitoring.

## What this is

A single-file HTML dashboard that loads in any modern browser
(no server required). Open `fieldshift_dashboard_v5.html` in Chrome,
Firefox, Safari, or Edge.

## What it shows

- Country-level democratic stress monitoring (CDRS data, 2010–2023)
- 28 red-flag indicators organized in 6 institutional subsystems
- Recovery-erosion asymmetry calculator (empirical range from V-Dem v16)
- World map visualization
- Country stories with historical analysis
- Election prediction lock workflow

## Scientific basis

The dashboard reflects the framework presented in the manuscript:

- **S₂ = √3/4 ≈ 0.433** — pre-registered critical threshold on the
  democratic stress scale (from triangle area)
- **S₁ = √3/8 ≈ 0.217** — pre-registered early-warning convention
- **ℋ_emp ≈ 1.55–1.96** — empirical recovery-erosion asymmetry observed
  in V-Dem v16 across six specifications
- **ℋ = √3 ≈ 1.732** — geometric conjecture (falls within all six 95% CIs)

All values in the dashboard are consistent with the manuscript tables
and the verified CSV outputs in the replication package.

## Note on data sources

The dashboard integrates two empirical data layers:

1. **V-Dem v16** (199 countries, 1790–2025): used for the asymmetry
   analysis and pre-registered threshold validation reported in the
   manuscript.

2. **CDRS composite** (163 countries, 2010–2023): the operational
   real-time monitoring score, aggregating Freedom House, V-Dem,
   World Bank WGI, and other sources.

These are complementary — V-Dem v16 is the *scientific validation
dataset*, CDRS is the *operational monitoring dataset*.

## Status

This is a pre-submission working prototype. Some features (e.g., the
recovery duration calculator) use the empirical asymmetry range
(1.55–1.96) as indicative calibration; they are presented as
"indicative only — not deterministic forecasts."

The dashboard is intended to give Professor Lindberg a sense of the
practical application envisioned for the framework, not as a
completed product.
