###############################################################################
# Hemp Calculation: Recovery/Erosion Asymmetry Constant
# DUBBEL MAGNITUDDEFINITION: Nettoförändring + Summa av absoluta delta
# FieldShift Research — Thomas Hedlund Leijon
###############################################################################

library(tidyverse)
library(zoo)

# ============================================================================
# STEG 1: LADDA DATA
# ============================================================================

vdem <- read_csv("V-Dem-CY-Full+Others-v16.csv")

df <- vdem %>%
  select(country_name, country_text_id, year, v2x_libdem) %>%
  arrange(country_text_id, year)

# ============================================================================
# STEG 2: BERÄKNA ÅRLIG FÖRÄNDRING OCH IDENTIFIERA EPISODER
# ============================================================================

df <- df %>%
  group_by(country_text_id) %>%
  mutate(
    delta = v2x_libdem - lag(v2x_libdem),
    direction = sign(delta)
  ) %>%
  ungroup() %>%
  drop_na(delta, direction)

# Fyll i noll-riktningar
df <- df %>%
  group_by(country_text_id) %>%
  mutate(
    direction_filled = ifelse(direction == 0, NA, direction),
    direction_filled = na.locf(direction_filled, na.rm = FALSE)
  ) %>%
  ungroup()

# Identifiera episoder
df <- df %>%
  group_by(country_text_id) %>%
  mutate(
    episode_change = ifelse(direction_filled != lag(direction_filled) | 
                            is.na(lag(direction_filled)), 1, 0),
    episode_id = cumsum(ifelse(is.na(episode_change), 0, episode_change))
  ) %>%
  ungroup()

# ============================================================================
# STEG 3: BERÄKNA EPISODEGENSKAPER MED BÅDA MAGNITUDDEFINITIONERNA
# ============================================================================

episodes <- df %>%
  group_by(country_text_id, episode_id) %>%
  summarise(
    country_name = first(country_name),
    start_year = min(year),
    end_year = max(year),
    duration = n(),
    direction = first(direction_filled),
    # Definition A: Summa av absoluta årliga förändringar (total turbulens)
    magnitude_abs_sum = sum(abs(delta), na.rm = TRUE),
    # Definition B: Nettoförändring (total kapacitetsförlust/vinst)
    magnitude_net = abs(last(v2x_libdem) - first(v2x_libdem)),
    start_value = first(v2x_libdem),
    end_value = last(v2x_libdem),
    total_change = end_value - start_value,
    .groups = 'drop'
  ) %>%
  filter(direction %in% c(-1, 1))

# ============================================================================
# STEG 4: FUNKTION FÖR ATT PARA IHOP OCH BERÄKNA Hemp
# ============================================================================

calculate_Hemp <- function(episodes_df, min_duration, min_magnitude_abs_sum, min_magnitude_net) {
  
  # Filtrera enligt definition (använder abs_sum för filtrering, net för separat beräkning)
  ep_filt <- episodes_df %>%
    filter(duration >= min_duration, 
           magnitude_abs_sum >= min_magnitude_abs_sum,
           magnitude_net >= min_magnitude_net)
  
  # Para ihop erosion-recovery inom varje land
  pairs <- data.frame()
  
  for (ctry in unique(ep_filt$country_text_id)) {
    ctry_eps <- ep_filt %>% 
      filter(country_text_id == ctry) %>% 
      arrange(start_year)
    
    if (nrow(ctry_eps) < 2) next
    
    for (i in 1:(nrow(ctry_eps) - 1)) {
      if (ctry_eps$direction[i] == -1 && ctry_eps$direction[i + 1] == 1) {
        pairs <- rbind(pairs, data.frame(
          country = ctry,
          country_name = ctry_eps$country_name[i],
          erosion_start = ctry_eps$start_year[i],
          erosion_end = ctry_eps$end_year[i],
          erosion_duration = ctry_eps$duration[i],
          # Båda magnitudmåtten för erosion
          erosion_magnitude_abs_sum = ctry_eps$magnitude_abs_sum[i],
          erosion_magnitude_net = ctry_eps$magnitude_net[i],
          recovery_start = ctry_eps$start_year[i + 1],
          recovery_end = ctry_eps$end_year[i + 1],
          recovery_duration = ctry_eps$duration[i + 1],
          # Båda magnitudmåtten för recovery
          recovery_magnitude_abs_sum = ctry_eps$magnitude_abs_sum[i + 1],
          recovery_magnitude_net = ctry_eps$magnitude_net[i + 1]
        ))
      }
    }
  }
  
  if (nrow(pairs) == 0) return(NULL)
  
  # Beräkna Hemp för BÅDA definitionerna
  H_emp_abs_sum <- mean(pairs$recovery_magnitude_abs_sum) / mean(pairs$erosion_magnitude_abs_sum)
  H_emp_net <- mean(pairs$recovery_magnitude_net) / mean(pairs$erosion_magnitude_net)
  
  # Bootstrap CI för BÅDA definitionerna
  set.seed(42)
  B <- 10000
  boot_H_abs_sum <- numeric(B)
  boot_H_net <- numeric(B)
  
  for (b in 1:B) {
    idx <- sample(1:nrow(pairs), size = nrow(pairs), replace = TRUE)
    boot_sample <- pairs[idx, ]
    boot_H_abs_sum[b] <- mean(boot_sample$recovery_magnitude_abs_sum) / mean(boot_sample$erosion_magnitude_abs_sum)
    boot_H_net[b] <- mean(boot_sample$recovery_magnitude_net) / mean(boot_sample$erosion_magnitude_net)
  }
  
  # BCa CI för abs_sum
  alpha <- 0.05
  z0_abs <- qnorm(mean(boot_H_abs_sum < H_emp_abs_sum))
  n <- nrow(pairs)
  
  jack_H_abs <- numeric(n)
  for (i in 1:n) {
    jack_sample <- pairs[-i, ]
    jack_H_abs[i] <- mean(jack_sample$recovery_magnitude_abs_sum) / mean(jack_sample$erosion_magnitude_abs_sum)
  }
  a_abs <- sum((mean(jack_H_abs) - jack_H_abs)^3) / (6 * (sum((mean(jack_H_abs) - jack_H_abs)^2))^(3/2))
  
  z_alpha_lower <- qnorm(alpha / 2)
  z_alpha_upper <- qnorm(1 - alpha / 2)
  p_lower_abs <- pnorm(z0_abs + (z0_abs + z_alpha_lower) / (1 - a_abs * (z0_abs + z_alpha_lower)))
  p_upper_abs <- pnorm(z0_abs + (z0_abs + z_alpha_upper) / (1 - a_abs * (z0_abs + z_alpha_upper)))
  
  ci_abs_lower <- quantile(boot_H_abs_sum, p_lower_abs)
  ci_abs_upper <- quantile(boot_H_abs_sum, p_upper_abs)
  
  # BCa CI för net
  z0_net <- qnorm(mean(boot_H_net < H_emp_net))
  
  jack_H_net <- numeric(n)
  for (i in 1:n) {
    jack_sample <- pairs[-i, ]
    jack_H_net[i] <- mean(jack_sample$recovery_magnitude_net) / mean(jack_sample$erosion_magnitude_net)
  }
  a_net <- sum((mean(jack_H_net) - jack_H_net)^3) / (6 * (sum((mean(jack_H_net) - jack_H_net)^2))^(3/2))
  
  p_lower_net <- pnorm(z0_net + (z0_net + z_alpha_lower) / (1 - a_net * (z0_net + z_alpha_lower)))
  p_upper_net <- pnorm(z0_net + (z0_net + z_alpha_upper) / (1 - a_net * (z0_net + z_alpha_upper)))
  
  ci_net_lower <- quantile(boot_H_net, p_lower_net)
  ci_net_upper <- quantile(boot_H_net, p_upper_net)
  
  # Testa geometriska hypoteser för BÅDA
  geometric_values <- c(1, sqrt(3)/2, sqrt(3), 2*sqrt(3), 3*sqrt(3))
  geometric_names <- c("1 (symmetry)", "sqrt(3)/2", "sqrt(3)", "2*sqrt(3)", "3*sqrt(3)")
  
  hypothesis_tests_abs <- data.frame(
    Hypothesis = geometric_names,
    Value = geometric_values,
    Within_CI = geometric_values >= ci_abs_lower & geometric_values <= ci_abs_upper
  )
  
  hypothesis_tests_net <- data.frame(
    Hypothesis = geometric_names,
    Value = geometric_values,
    Within_CI = geometric_values >= ci_net_lower & geometric_values <= ci_net_upper
  )
  
  return(list(
    H_emp_abs_sum = H_emp_abs_sum,
    H_emp_net = H_emp_net,
    ci_abs_lower = ci_abs_lower,
    ci_abs_upper = ci_abs_upper,
    ci_net_lower = ci_net_lower,
    ci_net_upper = ci_net_upper,
    n_pairs = nrow(pairs),
    n_countries = length(unique(pairs$country)),
    mean_erosion_abs_sum = mean(pairs$erosion_magnitude_abs_sum),
    mean_recovery_abs_sum = mean(pairs$recovery_magnitude_abs_sum),
    mean_erosion_net = mean(pairs$erosion_magnitude_net),
    mean_recovery_net = mean(pairs$recovery_magnitude_net),
    hypothesis_tests_abs = hypothesis_tests_abs,
    hypothesis_tests_net = hypothesis_tests_net,
    boot_H_abs_sum = boot_H_abs_sum,
    boot_H_net = boot_H_net,
    pairs = pairs
  ))
}

# ============================================================================
# STEG 5: KÖR ALLA TRE DEFINITIONER
# ============================================================================

definitions <- list(
  liberal = list(min_duration = 2, min_magnitude_abs_sum = 0.00, min_magnitude_net = 0.00, 
                 label = "Liberal (>=2 yr)"),
  standard = list(min_duration = 5, min_magnitude_abs_sum = 0.10, min_magnitude_net = 0.10, 
                  label = "Standard (>=5 yr, >=0.10)"),
  strict   = list(min_duration = 8, min_magnitude_abs_sum = 0.20, min_magnitude_net = 0.20, 
                  label = "Strict (>=8 yr, >=0.20)")
)

results_all <- list()

for (def_name in names(definitions)) {
  cat("\n========================================\n")
  cat("Definition:", definitions[[def_name]]$label, "\n")
  cat("========================================\n")
  
  res <- calculate_Hemp(
    episodes, 
    definitions[[def_name]]$min_duration, 
    definitions[[def_name]]$min_magnitude_abs_sum,
    definitions[[def_name]]$min_magnitude_net
  )
  
  if (is.null(res)) {
    cat("Inga episod-par funna för denna definition.\n")
    next
  }
  
  results_all[[def_name]] <- res
  
  cat("Antal episod-par:", res$n_pairs, "\n")
  cat("Antal länder:", res$n_countries, "\n\n")
  
  cat("--- Definition A: Summa av absoluta årliga förändringar ---\n")
  cat("Medel erosion (abs sum):", round(res$mean_erosion_abs_sum, 4), "\n")
  cat("Medel recovery (abs sum):", round(res$mean_recovery_abs_sum, 4), "\n")
  cat("Hemp (abs sum) =", round(res$H_emp_abs_sum, 4), "\n")
  cat("95% BCa CI: [", round(res$ci_abs_lower, 4), ", ", round(res$ci_abs_upper, 4), "]\n")
  
  cat("\nGeometriska hypoteser (abs sum):\n")
  for (i in 1:nrow(res$hypothesis_tests_abs)) {
    status <- ifelse(res$hypothesis_tests_abs$Within_CI[i], "INOM CI", "utanför CI")
    cat(sprintf("  H = %-20s (%.4f): %s\n", 
                res$hypothesis_tests_abs$Hypothesis[i], 
                res$hypothesis_tests_abs$Value[i], 
                status))
  }
  
  cat("\n--- Definition B: Nettoförändring ---\n")
  cat("Medel erosion (net):", round(res$mean_erosion_net, 4), "\n")
  cat("Medel recovery (net):", round(res$mean_recovery_net, 4), "\n")
  cat("Hemp (net) =", round(res$H_emp_net, 4), "\n")
  cat("95% BCa CI: [", round(res$ci_net_lower, 4), ", ", round(res$ci_net_upper, 4), "]\n")
  
  cat("\nGeometriska hypoteser (net):\n")
  for (i in 1:nrow(res$hypothesis_tests_net)) {
    status <- ifelse(res$hypothesis_tests_net$Within_CI[i], "INOM CI", "utanför CI")
    cat(sprintf("  H = %-20s (%.4f): %s\n", 
                res$hypothesis_tests_net$Hypothesis[i], 
                res$hypothesis_tests_net$Value[i], 
                status))
  }
  
  # Spara episod-par
  write_csv(res$pairs, paste0("episode_pairs_", def_name, "_v2.csv"))
}

# ============================================================================
# STEG 6: SAMMANFATTANDE TABELL
# ============================================================================

cat("\n\n========================================\n")
cat("SAMMANFATTANDE RESULTAT - BÅDA MAGNITUDDEFINITIONER\n")
cat("========================================\n\n")

summary_table <- data.frame()

for (def_name in names(results_all)) {
  res <- results_all[[def_name]]
  
  # Abs sum rad
  summary_table <- rbind(summary_table, data.frame(
    Definition = paste(definitions[[def_name]]$label, "(abs sum)"),
    N_pairs = res$n_pairs,
    N_countries = res$n_countries,
    Mean_erosion = round(res$mean_erosion_abs_sum, 4),
    Mean_recovery = round(res$mean_recovery_abs_sum, 4),
    Hemp = round(res$H_emp_abs_sum, 4),
    CI_lower = round(res$ci_abs_lower, 4),
    CI_upper = round(res$ci_abs_upper, 4),
    H1_in_CI = res$hypothesis_tests_abs$Within_CI[1],
    Hsqrt3_2_in_CI = res$hypothesis_tests_abs$Within_CI[2],
    Hsqrt3_in_CI = res$hypothesis_tests_abs$Within_CI[3],
    H2sqrt3_in_CI = res$hypothesis_tests_abs$Within_CI[4],
    H3sqrt3_in_CI = res$hypothesis_tests_abs$Within_CI[5]
  ))
  
  # Net rad
  summary_table <- rbind(summary_table, data.frame(
    Definition = paste(definitions[[def_name]]$label, "(net)"),
    N_pairs = res$n_pairs,
    N_countries = res$n_countries,
    Mean_erosion = round(res$mean_erosion_net, 4),
    Mean_recovery = round(res$mean_recovery_net, 4),
    Hemp = round(res$H_emp_net, 4),
    CI_lower = round(res$ci_net_lower, 4),
    CI_upper = round(res$ci_net_upper, 4),
    H1_in_CI = res$hypothesis_tests_net$Within_CI[1],
    Hsqrt3_2_in_CI = res$hypothesis_tests_net$Within_CI[2],
    Hsqrt3_in_CI = res$hypothesis_tests_net$Within_CI[3],
    H2sqrt3_in_CI = res$hypothesis_tests_net$Within_CI[4],
    H3sqrt3_in_CI = res$hypothesis_tests_net$Within_CI[5]
  ))
}

print(summary_table)
write_csv(summary_table, "Hemp_summary_both_definitions.csv")

# ============================================================================
# STEG 7: VISUALISERING
# ============================================================================

boot_combined <- data.frame()
for (def_name in names(results_all)) {
  res <- results_all[[def_name]]
  boot_combined <- rbind(boot_combined, data.frame(
    H = res$boot_H_abs_sum,
    Definition = paste(definitions[[def_name]]$label, "(abs sum)"),
    MagnitudeType = "Sum of absolute deltas"
  ))
  boot_combined <- rbind(boot_combined, data.frame(
    H = res$boot_H_net,
    Definition = paste(definitions[[def_name]]$label, "(net)"),
    MagnitudeType = "Net change"
  ))
}

p_bootstrap <- ggplot(boot_combined, aes(x = H, fill = MagnitudeType)) +
  geom_density(alpha = 0.4) +
  facet_wrap(~ Definition, scales = "free_y", ncol = 1) +
  geom_vline(xintercept = sqrt(3), linetype = "dashed", color = "firebrick", linewidth = 1) +
  geom_vline(xintercept = 1, linetype = "dotted", color = "grey50") +
  labs(x = expression(mathcal(H)), y = "Density",
       title = "Bootstrap distributions — Both magnitude definitions",
       subtitle = "Red dashed: geometric hypothesis (sqrt(3)). Dotted: symmetry null (H=1).") +
  theme_minimal() +
  theme(legend.position = "bottom")

ggsave("fig_Hemp_bootstrap_both_defs.pdf", p_bootstrap, width = 12, height = 10)

# ============================================================================
# STEG 8: SPARA ALLT
# ============================================================================

saveRDS(results_all, "Hemp_results_both_definitions.rds")

cat("\n=== ANALYS KLAR ===\n")
cat("Resultat sparade:\n")
cat("  - Hemp_results_both_definitions.rds\n")
cat("  - Hemp_summary_both_definitions.csv\n")
cat("  - episode_pairs_*_v2.csv\n")
cat("  - fig_Hemp_bootstrap_both_defs.pdf\n")