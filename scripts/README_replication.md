# Replication Package

This folder contains the empirical data and analysis scripts that produce
all numerical results reported in the manuscript Tables 1–3.

## Contents

### CSV files (derived results)

**`Hemp_summary_both_definitions.csv`** — produces manuscript Tables 2 and 3.

Six rows: three episode definitions × two magnitude operationalisations.

| Definition | N pairs | Hemp | 95% CI |
|---|---|---|---|
| Liberal (≥2 yr) (abs sum) | 1305 | 1.682 | [1.510, 1.881] |
| Liberal (≥2 yr) (net) | 1305 | 1.962 | [1.709, 2.258] |
| Standard (≥5 yr, ≥0.10) (abs sum) | 35 | 1.551 | [1.359, 1.778] |
| Standard (≥5 yr, ≥0.10) (net) | 35 | 1.576 | [1.366, 1.820] |
| Strict (≥8 yr, ≥0.20) (abs sum) | 10 | 1.727 | [1.462, 2.076] |
| Strict (≥8 yr, ≥0.20) (net) | 10 | 1.706 | [1.429, 2.060] |

Additional columns indicate whether each of five competing hypothesis
values (H = 1, √3/2, √3, 2√3, 3√3) falls within the 95% bootstrap
confidence interval. Only √3 ≈ 1.732 falls within all six CIs; the
four alternatives are excluded in every specification.

**`early_warning_results.csv`** — produces manuscript Table 1.

Test statistics for the critical slowing down analysis:

- Test 1 (above vs below S₂): variance β = −1.47 × 10⁻³ (p = 1.4 × 10⁻¹²⁷);
  AR(1) β = −5.07 × 10⁻² (p = 3.1 × 10⁻²¹). The naïve CSD prediction
  is falsified.
- Test 2 (pre-collapse vs stable, within S ≥ S₂): variance β = +1.26 × 10⁻³
  (p = 2.0 × 10⁻⁶⁶); AR(1) β = +8.14 × 10⁻² (p = 3.1 × 10⁻¹³). The
  refined CSD prediction is supported.
- Test 3 (trend before collapse): variance trend β = 6.71 × 10⁻⁵ (p = 0.086);
  AR(1) trend β = −4.97 × 10⁻³ (p = 0.828).
- Placebo (1000 permutations): variance p = 0.093; AR(1) p = 0.915.

### R scripts (analysis pipeline)

**`hemp_calculation_v3.R`** — computes the recovery–erosion asymmetry
constant ℋ across three episode definitions and two magnitude
operationalisations. Output: `Hemp_summary_both_definitions.csv`.

**`Demshift_analysis.R`** — runs the complete early-warning analysis:
critical slowing down tests (Test 1, Test 2, Test 3), placebo permutations,
and pre-collapse trend analysis. Output: `early_warning_results.csv`.

## Reproducing the analysis

### Prerequisites

- R version 4.0 or higher
- V-Dem Country-Year Full+Others Dataset v16 (filename:
  `V-Dem-CY-Full+Others-v16.csv`). Available after registration at
  https://v-dem.net/data/
- R packages: tidyverse, zoo, sandwich, lmtest, ggplot2, patchwork

### Steps

1. Place `V-Dem-CY-Full+Others-v16.csv` in the working directory.
2. Run `hemp_calculation_v3.R` to produce `Hemp_summary_both_definitions.csv`.
3. Run `Demshift_analysis.R` to produce `early_warning_results.csv`.

Each script is self-contained and reads V-Dem v16 directly.

### Verification

After running both scripts, the produced CSV files should match the
versions included in this folder to within numerical precision. Any
substantive deviation indicates either a different V-Dem version, missing
packages, or modified script parameters.

## Contact

For questions about replication or to report issues:

Thomas Hedlund Leijon  
FieldShift Research, Stockholm  
thomas.hedlundleijon@gmail.com
