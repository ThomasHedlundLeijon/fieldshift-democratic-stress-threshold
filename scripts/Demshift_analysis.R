###############################################################################
# Early-Warning Analysis: Critical Slowing Down near S₂ = √3/4
# FieldShift Research — Thomas Hedlund Leijon
# 
# Detta skript kör den kompletta early-warning-analysen som specificerats
# i analysplanen (steg 0–6).
#
# Krav: V-Dem Country-Year Full+Others v16 (fil: V-Dem-CY-Full+Others-v16.csv)
#        Skriptet förutsätter att filen ligger i working directory.
###############################################################################

# ============================================================================
# STEG 0: PAKET, DATA, PREPROCESSERING
# ============================================================================

# Ladda nödvändiga paket
library(tidyverse)
library(sandwich)
library(lmtest)
library(ggplot2)
library(patchwork)

# Läs V-Dem v16
vdem <- read_csv("V-Dem-CY-Full+Others-v16.csv")

# Välj och döp om relevanta variabler
df <- vdem %>%
  select(
    country_name,
    country_text_id,
    year,
    v2x_libdem,       # Liberal Democracy Index
    v2x_polyarchy,    # Polyarchy (för robusthet)
    v2x_regime        # Regimes of the World (för extern validering)
  ) %>%
  arrange(country_text_id, year)

# ============================================================================
# STEG 0.1: BERÄKNA DEMOKRATISK STRESS OCH TIDIGA VARIABLER
# ============================================================================

# Definiera tröskeln
S2 <- sqrt(3) / 4  # ≈ 0.4330127

df <- df %>%
  group_by(country_text_id) %>%
  mutate(
    # Demokratisk stress
    S = 1 - v2x_libdem,
    
    # Binär indikator över tröskeln
    above_S2 = ifelse(S >= S2, 1, 0),
    
    # Årlig förändring i libdem
    delta_libdem = v2x_libdem - lag(v2x_libdem),
    
    # Kollapshändelse (primär definition: delta ≤ -0.05)
    collapse = ifelse(delta_libdem <= -0.05, 1, 0),
    
    # Framåtblickande kollapsutfall (1, 2, 3, 5 år)
    collapse_1y_forward = ifelse(lead(collapse, 1) == 1, 1, 0),
    collapse_2y_forward = ifelse(lead(collapse, 1) == 1 | lead(collapse, 2) == 1, 1, 0),
    collapse_3y_forward = ifelse(lead(collapse, 1) == 1 | lead(collapse, 2) == 1 | lead(collapse, 3) == 1, 1, 0),
    collapse_5y_forward = ifelse(lead(collapse, 1) == 1 | lead(collapse, 2) == 1 | lead(collapse, 3) == 1 | lead(collapse, 4) == 1 | lead(collapse, 5) == 1, 1, 0)
  ) %>%
  ungroup()

# Ta bort NA som uppstår från lag/lead
df <- df %>% drop_na(S, above_S2, delta_libdem, collapse)

# ============================================================================
# STEG 1: RULLANDE FÖNSTER — VARIANS OCH AUTOKORRELATION
# ============================================================================

#' Beräkna rullande varians och AR(1) för en tidsserie
#' 
#' @param x numerisk vektor (tidsserie)
#' @param w fönsterlängd
#' @return data.frame med kolumner: rolling_var, rolling_ar1

compute_rolling_csd <- function(x, w) {
  n <- length(x)
  rolling_var <- rep(NA, n)
  rolling_ar1 <- rep(NA, n)
  
  if (n < w) {
    return(data.frame(rolling_var = rolling_var, rolling_ar1 = rolling_ar1))
  }
  
  for (i in w:n) {
    window <- x[(i - w + 1):i]
    
    if (sum(!is.na(window)) < 4) next
    
    t_idx <- 1:w
    lm_fit <- tryCatch(
      lm(window ~ t_idx),
      error = function(e) NULL
    )
    
    if (is.null(lm_fit)) next
    
    resid_vals <- resid(lm_fit)
    
    if (length(resid_vals) < 4) next
    
    rolling_var[i] <- var(resid_vals)
    
    ar1_res <- tryCatch(
      cor(resid_vals[2:w], resid_vals[1:(w-1)]),
      error = function(e) NA
    )
    rolling_ar1[i] <- ar1_res
  }
  
  return(data.frame(rolling_var = rolling_var, rolling_ar1 = rolling_ar1))
}
 
# Funktion för att applicera rullande CSD på ett land

compute_country_csd <- function(country_data, w) {
  n_orig <- nrow(country_data)
  csd_res <- compute_rolling_csd(country_data$S, w)
  stopifnot(nrow(csd_res) == n_orig)
  country_data$rolling_var <- csd_res$rolling_var
  country_data$rolling_ar1 <- csd_res$rolling_ar1
  country_data$window_size <- w
  return(country_data)
}

# Primär fönsterlängd
W_PRIMARY <- 10

# Beräkna CSD-indikatorer för alla länder
df_csd <- df %>%
  group_by(country_text_id) %>%
  group_modify(~ compute_country_csd(.x, W_PRIMARY)) %>%
  ungroup()

# Ta bort NA från rullande beräkningar (första w-1 år per land)
df_csd <- df_csd %>% drop_na(rolling_var, rolling_ar1)

# ============================================================================
# STEG 2: TEST 1 — JÄMFÖRELSE ÖVER OCH UNDER S₂
# ============================================================================

# Sammanfattande statistik
summary_table_1 <- df_csd %>%
  group_by(above_S2) %>%
  summarise(
    mean_var = mean(rolling_var, na.rm = TRUE),
    sd_var = sd(rolling_var, na.rm = TRUE),
    mean_ar1 = mean(rolling_ar1, na.rm = TRUE),
    sd_ar1 = sd(rolling_ar1, na.rm = TRUE),
    n = n()
  )
print("Test 1 — Deskriptiv statistik:")
print(summary_table_1)

# 2a: Pooled approach med land-klustrade standardfel
model_var <- lm(rolling_var ~ above_S2, data = df_csd)
model_ar1 <- lm(rolling_ar1 ~ above_S2, data = df_csd)

# Klustra på land
vcov_cluster_var <- vcovCL(model_var, cluster = ~ country_text_id)
vcov_cluster_ar1 <- vcovCL(model_ar1, cluster = ~ country_text_id)

test1_var <- coeftest(model_var, vcov = vcov_cluster_var)
test1_ar1 <- coeftest(model_ar1, vcov = vcov_cluster_ar1)

print("Test 1 — Varians (above_S2 effekt, klustrade SE):")
print(test1_var)

print("Test 1 — AR(1) (above_S2 effekt, klustrade SE):")
print(test1_ar1)

# 2b: Within-country paired comparison
paired_countries <- df_csd %>%
  group_by(country_text_id) %>%
  filter(sum(above_S2 == 1) >= 5 & sum(above_S2 == 0) >= 5) %>%
  summarise(
    mean_var_above = mean(rolling_var[above_S2 == 1], na.rm = TRUE),
    mean_var_below = mean(rolling_var[above_S2 == 0], na.rm = TRUE),
    mean_ar1_above = mean(rolling_ar1[above_S2 == 1], na.rm = TRUE),
    mean_ar1_below = mean(rolling_ar1[above_S2 == 0], na.rm = TRUE),
    diff_var = mean_var_above - mean_var_below,
    diff_ar1 = mean_ar1_above - mean_ar1_below
  )

n_paired <- nrow(paired_countries)
paired_ttest_var <- t.test(paired_countries$diff_var, alternative = "greater")
paired_ttest_ar1 <- t.test(paired_countries$diff_ar1, alternative = "greater")

print(paste("Antal länder i paired analys:", n_paired))
print("Test 1 — Paired t-test, variansdifferens:")
print(paired_ttest_var)
print("Test 1 — Paired t-test, AR(1)-differens:")
print(paired_ttest_ar1)

# ============================================================================
# STEG 3: TEST 2 — PRE-KOLLAPS VS. STABIL HÖGSTRESS
# ============================================================================

# Skapa grupper
df_csd <- df_csd %>%
  mutate(
    # Pre-collapse: above S2 och kollaps inom 3 år
    pre_collapse = ifelse(above_S2 == 1 & collapse_3y_forward == 1, 1, 0),
    # Stabil högstress: above S2 men ingen kollaps inom 5 år
    stable_high_stress = ifelse(above_S2 == 1 & 
                                  collapse_1y_forward == 0 & 
                                  collapse_2y_forward == 0 & 
                                  collapse_3y_forward == 0 & 
                                  collapse_5y_forward == 0, 1, 0)
  )

# Filtrera till relevanta grupper
df_test2 <- df_csd %>% filter(pre_collapse == 1 | stable_high_stress == 1)

# Sammanfattande statistik
summary_table_2 <- df_test2 %>%
  group_by(pre_collapse) %>%
  summarise(
    mean_var = mean(rolling_var, na.rm = TRUE),
    sd_var = sd(rolling_var, na.rm = TRUE),
    mean_ar1 = mean(rolling_ar1, na.rm = TRUE),
    sd_ar1 = sd(rolling_ar1, na.rm = TRUE),
    n = n()
  )
print("Test 2 — Deskriptiv statistik:")
print(summary_table_2)

# Test: pre-collapse vs stable high-stress
model_var_2 <- lm(rolling_var ~ pre_collapse, data = df_test2)
model_ar1_2 <- lm(rolling_ar1 ~ pre_collapse, data = df_test2)

vcov_var_2 <- vcovCL(model_var_2, cluster = ~ country_text_id)
vcov_ar1_2 <- vcovCL(model_ar1_2, cluster = ~ country_text_id)

test2_var <- coeftest(model_var_2, vcov = vcov_var_2)
test2_ar1 <- coeftest(model_ar1_2, vcov = vcov_ar1_2)

print("Test 2 — Varians (pre_collapse effekt, klustrade SE):")
print(test2_var)
print("Test 2 — AR(1) (pre_collapse effekt, klustrade SE):")
print(test2_ar1)

# Cohens d
cohens_d <- function(x, y) {
  n_x <- length(na.omit(x)); n_y <- length(na.omit(y))
  mean_x <- mean(x, na.rm = TRUE); mean_y <- mean(y, na.rm = TRUE)
  sd_x <- sd(x, na.rm = TRUE); sd_y <- sd(y, na.rm = TRUE)
  pooled_sd <- sqrt(((n_x - 1)*sd_x^2 + (n_y - 1)*sd_y^2) / (n_x + n_y - 2))
  (mean_x - mean_y) / pooled_sd
}

d_var <- cohens_d(df_test2$rolling_var[df_test2$pre_collapse == 1],
                  df_test2$rolling_var[df_test2$pre_collapse == 0])
d_ar1 <- cohens_d(df_test2$rolling_ar1[df_test2$pre_collapse == 1],
                  df_test2$rolling_ar1[df_test2$pre_collapse == 0])

print(paste("Test 2 — Cohen's d (varians):", round(d_var, 3)))
print(paste("Test 2 — Cohen's d (AR1):", round(d_ar1, 3)))

# ============================================================================
# STEG 4: TEST 3 — TEMPORAL TREND FÖRE KOLLAPS
# ============================================================================

# Identifiera kollapsår
collapse_events <- df_csd %>%
  filter(collapse == 1) %>%
  select(country_text_id, year) %>%
  distinct()

# För varje kollapshändelse, extrahera pre-kollapsdata
pre_collapse_trends <- data.frame()

for (i in 1:nrow(collapse_events)) {
  ctry <- collapse_events$country_text_id[i]
  event_year <- collapse_events$year[i]
  
  # Extrahera 5 år före kollaps
  pre_data <- df_csd %>%
    filter(country_text_id == ctry,
           year >= event_year - 5,
           year < event_year) %>%
    arrange(year) %>%
    mutate(time_to_collapse = year - event_year)
  
  if (nrow(pre_data) >= 4) {  # behövs minst 4 obs för trend
    # Linjär trend i varians
    lm_var <- lm(rolling_var ~ time_to_collapse, data = pre_data)
    beta_var <- coef(lm_var)["time_to_collapse"]
    p_var <- summary(lm_var)$coefficients["time_to_collapse", "Pr(>|t|)"]
    
    # Linjär trend i AR(1)
    lm_ar1 <- lm(rolling_ar1 ~ time_to_collapse, data = pre_data)
    beta_ar1 <- coef(lm_ar1)["time_to_collapse"]
    p_ar1 <- summary(lm_ar1)$coefficients["time_to_collapse", "Pr(>|t|)"]
    
    pre_collapse_trends <- rbind(pre_collapse_trends, data.frame(
      country = ctry,
      event_year = event_year,
      n_pre = nrow(pre_data),
      beta_var = beta_var,
      p_var = p_var,
      beta_ar1 = beta_ar1,
      p_ar1 = p_ar1
    ))
  }
}

# Test: är medellutningen > 0?
n_trend_events <- nrow(pre_collapse_trends)
ttest_beta_var <- t.test(pre_collapse_trends$beta_var, alternative = "greater")
ttest_beta_ar1 <- t.test(pre_collapse_trends$beta_ar1, alternative = "greater")

print(paste("Antal kollapshändelser i trendanalys:", n_trend_events))
print("Test 3 — One-sample t-test, beta_var > 0:")
print(ttest_beta_var)
print("Test 3 — One-sample t-test, beta_ar1 > 0:")
print(ttest_beta_ar1)

print(paste("Medellutning varians:", round(mean(pre_collapse_trends$beta_var), 6)))
print(paste("Medellutning AR(1):", round(mean(pre_collapse_trends$beta_ar1), 6)))

# Andel positiva lutningar
prop_pos_var <- mean(pre_collapse_trends$beta_var > 0)
prop_pos_ar1 <- mean(pre_collapse_trends$beta_ar1 > 0)
print(paste("Andel positiva lutningar (varians):", round(prop_pos_var, 3)))
print(paste("Andel positiva lutningar (AR1):", round(prop_pos_ar1, 3)))

# ============================================================================
# STEG 5: PLACEBO-TEST
# ============================================================================

N_PERM <- 1000
set.seed(42)  # reproducerbarhet

# Hjälpfunktion: randomisera kollapstider inom land
permute_collapse_years <- function(data) {
  data %>%
    group_by(country_text_id) %>%
    mutate(
      collapse_perm = sample(collapse)  # slumpa om kollapsindikatorn
    ) %>%
    ungroup()
}

# Lagra placebofördelningar
placebo_beta_var <- numeric(N_PERM)
placebo_beta_ar1 <- numeric(N_PERM)

for (p in 1:N_PERM) {
  # Slumpa om kollapser
  df_perm <- permute_collapse_years(df_csd)
  
  # Identifiera permuterade kollapshändelser
  collapse_perm_events <- df_perm %>%
    filter(collapse_perm == 1) %>%
    select(country_text_id, year) %>%
    distinct()
  
  # Beräkna trender för permuterade data
  perm_trends <- data.frame()
  
  for (i in 1:nrow(collapse_perm_events)) {
    ctry <- collapse_perm_events$country_text_id[i]
    event_year <- collapse_perm_events$year[i]
    
    pre_data <- df_perm %>%
      filter(country_text_id == ctry,
             year >= event_year - 5,
             year < event_year) %>%
      arrange(year) %>%
      mutate(time_to_collapse = year - event_year)
    
    if (nrow(pre_data) >= 4) {
      lm_var <- lm(rolling_var ~ time_to_collapse, data = pre_data)
      lm_ar1 <- lm(rolling_ar1 ~ time_to_collapse, data = pre_data)
      
      perm_trends <- rbind(perm_trends, data.frame(
        beta_var = coef(lm_var)["time_to_collapse"],
        beta_ar1 = coef(lm_ar1)["time_to_collapse"]
      ))
    }
  }
  
  placebo_beta_var[p] <- mean(perm_trends$beta_var)
  placebo_beta_ar1[p] <- mean(perm_trends$beta_ar1)
  
  if (p %% 100 == 0) cat("Permutation", p, "av", N_PERM, "\n")
}

# Beräkna empiriska p-värden
obs_mean_beta_var <- mean(pre_collapse_trends$beta_var)
obs_mean_beta_ar1 <- mean(pre_collapse_trends$beta_ar1)

p_placebo_var <- mean(placebo_beta_var >= obs_mean_beta_var)
p_placebo_ar1 <- mean(placebo_beta_ar1 >= obs_mean_beta_ar1)

print(paste("Placebo-test — p-värde (varians):", round(p_placebo_var, 4)))
print(paste("Placebo-test — p-värde (AR1):", round(p_placebo_ar1, 4)))
print(paste("Observerad medellutning (varians):", round(obs_mean_beta_var, 6)))
print(paste("99:e percentilen av placebo (varians):", round(quantile(placebo_beta_var, 0.99), 6)))

# ============================================================================
# STEG 6: SAMMANSTÄLLNING OCH VISUALISERING
# ============================================================================

# --- Hjälpfunktion för att extrahera resultat ---
extract_lm_result <- function(model_obj, coef_name) {
  s <- summary(model_obj)
  if (coef_name %in% rownames(s$coefficients)) {
    return(c(
      estimate = s$coefficients[coef_name, "Estimate"],
      se = s$coefficients[coef_name, "Std. Error"],
      p = s$coefficients[coef_name, "Pr(>|t|)"]
    ))
  } else {
    return(c(estimate = NA, se = NA, p = NA))
  }
}

# --- Extrahera resultat från Test 1 ---
t1_var <- extract_lm_result(model_var, "above_S2")
t1_ar1 <- extract_lm_result(model_ar1, "above_S2")

# --- Extrahera resultat från Test 2 ---
t2_var <- extract_lm_result(model_var_2, "pre_collapse")
t2_ar1 <- extract_lm_result(model_ar1_2, "pre_collapse")

# --- Tabell: Huvudresultat ---
results_table <- data.frame(
  Test = c("Test 1: above vs below S2", "Test 1: above vs below S2",
           "Test 2: pre-collapse vs stable", "Test 2: pre-collapse vs stable",
           "Test 3: trend before collapse", "Test 3: trend before collapse",
           "Placebo", "Placebo"),
  Indicator = c("Varians", "AR(1)", "Varians", "AR(1)", 
                "Varians trend", "AR(1) trend", "Varians", "AR(1)"),
  Estimate = c(
    t1_var["estimate"], t1_ar1["estimate"],
    t2_var["estimate"], t2_ar1["estimate"],
    mean(pre_collapse_trends$beta_var),
    mean(pre_collapse_trends$beta_ar1),
    NA, NA
  ),
  p_value = c(
    t1_var["p"], t1_ar1["p"],
    t2_var["p"], t2_ar1["p"],
    ttest_beta_var$p.value,
    ttest_beta_ar1$p.value,
    p_placebo_var,
    p_placebo_ar1
  )
)

print("=== SAMMANFATTANDE RESULTATTABELL ===")
print(results_table)

# --- Figur: Varians över och under S2 ---
p_var <- ggplot(df_csd, aes(x = factor(above_S2, labels = c("S < S2", "S >= S2")), 
                            y = rolling_var)) +
  geom_violin(aes(fill = factor(above_S2)), alpha = 0.6, draw_quantiles = 0.5) +
  geom_boxplot(width = 0.15, alpha = 0.3) +
  scale_y_log10() +
  scale_fill_manual(values = c("steelblue", "firebrick"), guide = "none") +
  labs(x = "", y = "Rolling variance (log scale)", 
       title = "Variance above vs below S2") +
  theme_minimal()

# --- Figur: AR(1) över och under S2 ---
p_ar1 <- ggplot(df_csd, aes(x = factor(above_S2, labels = c("S < S2", "S >= S2")), 
                            y = rolling_ar1)) +
  geom_violin(aes(fill = factor(above_S2)), alpha = 0.6, draw_quantiles = 0.5) +
  geom_boxplot(width = 0.15, alpha = 0.3) +
  scale_fill_manual(values = c("steelblue", "firebrick"), guide = "none") +
  labs(x = "", y = "Rolling AR(1)", 
       title = "Autocorrelation above vs below S2") +
  theme_minimal()

# --- Figur: Placebo-fördelning ---
placebo_df <- data.frame(
  beta_var = placebo_beta_var,
  beta_ar1 = placebo_beta_ar1
)

fig_placebo_var <- ggplot(placebo_df, aes(x = beta_var)) +
  geom_histogram(bins = 50, fill = "grey70", color = "grey30") +
  geom_vline(xintercept = obs_mean_beta_var, color = "firebrick", linewidth = 1) +
  labs(x = "Mean beta (variance trend)", y = "Frequency",
       title = "Placebo distribution — Variance",
       subtitle = paste("p =", round(p_placebo_var, 4))) +
  theme_minimal()

fig_placebo_ar1 <- ggplot(placebo_df, aes(x = beta_ar1)) +
  geom_histogram(bins = 50, fill = "grey70", color = "grey30") +
  geom_vline(xintercept = obs_mean_beta_ar1, color = "firebrick", linewidth = 1) +
  labs(x = "Mean beta (AR1 trend)", y = "Frequency",
       title = "Placebo distribution — AR(1)",
       subtitle = paste("p =", round(p_placebo_ar1, 4))) +
  theme_minimal()

# --- Spara figurer ---
ggsave("fig_csd_variance.pdf", p_var, width = 6, height = 5)
ggsave("fig_csd_ar1.pdf", p_ar1, width = 6, height = 5)
ggsave("fig_placebo_var.pdf", fig_placebo_var, width = 6, height = 5)
ggsave("fig_placebo_ar1.pdf", fig_placebo_ar1, width = 6, height = 5)

# --- Spara resultat ---
write_csv(results_table, "early_warning_results.csv")
write_csv(pre_collapse_trends, "pre_collapse_trends.csv")
write_csv(placebo_df, "placebo_distribution.csv")

# --- Placebo resultat ---
print("=== PLACEBO RESULTAT ===")
print(paste("Observerad medellutning (varians):", round(obs_mean_beta_var, 6)))
print(paste("Observerad medellutning (AR1):", round(obs_mean_beta_ar1, 6)))
print(paste("Placebo p-värde (varians):", round(p_placebo_var, 4)))
print(paste("Placebo p-värde (AR1):", round(p_placebo_ar1, 4)))
print(paste("99:e percentilen av placebo (varians):", round(quantile(placebo_beta_var, 0.99), 6)))
print(paste("99:e percentilen av placebo (AR1):", round(quantile(placebo_beta_ar1, 0.99), 6)))

# ============================================================================
# EXTRA: ROBUSTHET MED ALTERNATIVA FÖNSTERLÄNGDER
# ============================================================================

window_lengths <- c(5, 8, 12, 15)
robustness_results <- data.frame()

for (w_alt in window_lengths) {
  cat("\n=== Robusthet: w =", w_alt, "===\n")
  
  df_csd_alt <- df %>%
    group_by(country_text_id) %>%
    group_modify(~ compute_country_csd(.x, w_alt)) %>%
    ungroup() %>%
    drop_na(rolling_var, rolling_ar1)
  
  m_var <- lm(rolling_var ~ above_S2, data = df_csd_alt)
  m_ar1 <- lm(rolling_ar1 ~ above_S2, data = df_csd_alt)
  
  vcov_alt_var <- vcovCL(m_var, cluster = ~ country_text_id)
  vcov_alt_ar1 <- vcovCL(m_ar1, cluster = ~ country_text_id)
  
  t_var <- coeftest(m_var, vcov = vcov_alt_var)
  t_ar1 <- coeftest(m_ar1, vcov = vcov_alt_ar1)
  
  robustness_results <- rbind(robustness_results, data.frame(
    window = w_alt,
    coef_var = t_var["above_S2", "Estimate"],
    se_var = t_var["above_S2", "Std. Error"],
    p_var = t_var["above_S2", "Pr(>|t|)"],
    coef_ar1 = t_ar1["above_S2", "Estimate"],
    se_ar1 = t_ar1["above_S2", "Std. Error"],
    p_ar1 = t_ar1["above_S2", "Pr(>|t|)"]
  ))
}

robustness_results <- rbind(
  data.frame(
    window = W_PRIMARY,
    coef_var = t1_var["estimate"],
    se_var = t1_var["se"],
    p_var = t1_var["p"],
    coef_ar1 = t1_ar1["estimate"],
    se_ar1 = t1_ar1["se"],
    p_ar1 = t1_ar1["p"]
  ),
  robustness_results
) %>% arrange(window)

print("=== ROBUSTHET: ALTERNATIVA FÖNSTERLÄNGDER ===")
print(robustness_results)
write_csv(robustness_results, "window_robustness.csv")

cat("\n=== ANALYS KLAR ===\n")
cat("Resultat sparade:\n")
cat("  - early_warning_results.csv\n")
cat("  - pre_collapse_trends.csv\n")
cat("  - placebo_distribution.csv\n")
cat("  - window_robustness.csv\n")
cat("  - fig_csd_variance.pdf, fig_csd_ar1.pdf\n")
cat("  - fig_placebo_var.pdf, fig_placebo_ar1.pdf\n")