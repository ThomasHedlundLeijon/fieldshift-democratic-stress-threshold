"""
Figure 4: Critical slowing down results (Test 1 falsification + Test 2 confirmation).

Four panels:
a) Variance: above vs below S₂ (Test 1 falsification - NEGATIVE)
b) AR(1): above vs below S₂ (Test 1 falsification - NEGATIVE)
c) Variance: pre-collapse vs stable high-stress (Test 2 confirmation - POSITIVE)
d) AR(1): pre-collapse vs stable high-stress (Test 2 confirmation - POSITIVE)

Uses exact values from early_warning_results.csv
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 9,
    'axes.linewidth': 0.6,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

# Verified values from R output (early_warning_results.csv)
# Test 1 means come from summary_table_1
T1_var_below = 0.00199   # S < S2 mean variance
T1_var_above = 0.000514  # S >= S2 mean variance
T1_var_below_sd = 0.00718
T1_var_above_sd = 0.00189
T1_ar1_below = 0.259
T1_ar1_above = 0.208
T1_ar1_below_sd = 0.263
T1_ar1_above_sd = 0.282

# Test 2 means from summary_table_2
T2_var_stable = 0.000440  # not pre-collapse
T2_var_precollapse = 0.00170
T2_var_stable_sd = 0.00175
T2_var_precollapse_sd = 0.00361
T2_ar1_stable = 0.201
T2_ar1_precollapse = 0.283
T2_ar1_stable_sd = 0.282
T2_ar1_precollapse_sd = 0.262

# Sample sizes
n_below = 3164
n_above = 20077
n_stable = 18207
n_precollapse = 660

# P-values
p_t1_var = 1.4e-127
p_t1_ar1 = 3.1e-21
p_t2_var = 2.0e-66
p_t2_ar1 = 3.1e-13

# Cohen's d (Test 2)
d_var = 0.685
d_ar1 = 0.289

fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.5), constrained_layout=True)

COLOR_LOW = '#5b9bd5'    # blue: below threshold / stable
COLOR_HIGH = '#c44a4a'   # red: above threshold / pre-collapse

def plot_comparison(ax, vals, sds, ns, labels, colors, ylabel, title, p_value, cohen_d=None,
                    yscale='linear', verdict_color='#8c0000'):
    """Bar plot with error bars for two-group comparison."""
    x = np.arange(2)
    bars = ax.bar(x, vals, color=colors, edgecolor='#333333', linewidth=0.6,
                  alpha=0.85, width=0.5)
    # Error bars (SE = SD/sqrt(n))
    se = [sd/np.sqrt(n) for sd, n in zip(sds, ns)]
    ax.errorbar(x, vals, yerr=se, fmt='none', ecolor='#333333', capsize=4, lw=0.8)

    # Sample sizes in bar (or above if bar too small)
    for i, (v, n) in enumerate(zip(vals, ns)):
        if yscale == 'log':
            # For log scale, check if bar is much smaller than max
            if v < max(vals) * 0.1:
                y_text = v * 2.5
                ax.text(i, y_text, f'n={n:,}', ha='center', va='bottom',
                        fontsize=7.5, color='#333', fontweight='bold')
            else:
                y_text = v * 0.55
                ax.text(i, y_text, f'n={n:,}', ha='center', va='center',
                        fontsize=7.5, color='white', fontweight='bold')
        else:
            if v < max(vals) * 0.15:
                y_text = v + max(vals) * 0.03
                ax.text(i, y_text, f'n={n:,}', ha='center', va='bottom',
                        fontsize=7.5, color='#333', fontweight='bold')
            else:
                y_text = v * 0.5 if v > 0 else 0.05 * max(vals)
                ax.text(i, y_text, f'n={n:,}', ha='center', va='center',
                        fontsize=7.5, color='white', fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, loc='left', fontsize=9.5, pad=4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if yscale == 'log':
        ax.set_yscale('log')

    # P-value annotation
    if p_value < 1e-10:
        p_str = f'p = {p_value:.0e}'.replace('e-', '\u00d710\u207b')
        # Format: convert exponent digits to superscript
        p_str = f'p \u2248 {p_value:.0e}'
        # Better: keep simple
        if p_value < 1e-50:
            p_str = f'$p < 10^{{-50}}$'
        else:
            exp = int(np.floor(np.log10(p_value)))
            mantissa = p_value / 10**exp
            p_str = f'$p \\approx {mantissa:.1f}\\times 10^{{{exp}}}$'
    else:
        p_str = f'p = {p_value:.3g}'

    # Verdict text (top center)
    max_val = max(vals)
    ymax = ax.get_ylim()[1]
    if yscale == 'log':
        y_p = ymax * 0.7
    else:
        y_p = ymax * 0.90

    note = p_str
    if cohen_d is not None:
        note += f"\nCohen's $d$ = {cohen_d:.3f}"
    ax.text(0.5, 0.95, note, transform=ax.transAxes,
            fontsize=8, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff4e6',
                      edgecolor=verdict_color, lw=0.6))

# Panel a: Test 1 variance
plot_comparison(
    axes[0,0],
    vals=[T1_var_below, T1_var_above],
    sds=[T1_var_below_sd, T1_var_above_sd],
    ns=[n_below, n_above],
    labels=[r'$S < S_2$', r'$S \geq S_2$'],
    colors=[COLOR_LOW, COLOR_HIGH],
    ylabel='Rolling variance',
    title=r'$\mathbf{a}$  Test 1: Variance, full population',
    p_value=p_t1_var,
    yscale='log',
)

# Panel b: Test 1 AR(1)
plot_comparison(
    axes[0,1],
    vals=[T1_ar1_below, T1_ar1_above],
    sds=[T1_ar1_below_sd, T1_ar1_above_sd],
    ns=[n_below, n_above],
    labels=[r'$S < S_2$', r'$S \geq S_2$'],
    colors=[COLOR_LOW, COLOR_HIGH],
    ylabel='Rolling AR(1)',
    title=r'$\mathbf{b}$  Test 1: Autocorrelation, full population',
    p_value=p_t1_ar1,
)

# Panel c: Test 2 variance
plot_comparison(
    axes[1,0],
    vals=[T2_var_stable, T2_var_precollapse],
    sds=[T2_var_stable_sd, T2_var_precollapse_sd],
    ns=[n_stable, n_precollapse],
    labels=['Stable high-stress', 'Pre-collapse'],
    colors=[COLOR_LOW, COLOR_HIGH],
    ylabel='Rolling variance',
    title=r'$\mathbf{c}$  Test 2: Variance within $S \geq S_2$',
    p_value=p_t2_var,
    cohen_d=d_var,
    yscale='log',
)

# Panel d: Test 2 AR(1)
plot_comparison(
    axes[1,1],
    vals=[T2_ar1_stable, T2_ar1_precollapse],
    sds=[T2_ar1_stable_sd, T2_ar1_precollapse_sd],
    ns=[n_stable, n_precollapse],
    labels=['Stable high-stress', 'Pre-collapse'],
    colors=[COLOR_LOW, COLOR_HIGH],
    ylabel='Rolling AR(1)',
    title=r'$\mathbf{d}$  Test 2: Autocorrelation within $S \geq S_2$',
    p_value=p_t2_ar1,
    cohen_d=d_ar1,
)

# Overall caption interpretation
fig.suptitle('Critical slowing down: naive prediction falsified, refined prediction confirmed',
             fontsize=10.5, fontweight='bold', y=1.02)

plt.savefig('/home/claude/lindberg_final/figures/Figure4_csd.pdf',
            bbox_inches='tight', pad_inches=0.05)
plt.savefig('/home/claude/lindberg_final/figures/Figure4_csd.png',
            bbox_inches='tight', pad_inches=0.05, dpi=300)
print("Figure 4 saved.")
