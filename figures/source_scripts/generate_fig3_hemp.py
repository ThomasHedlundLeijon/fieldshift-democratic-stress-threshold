"""
Figure 3: Hemp bootstrap distributions — six specifications (3 episode definitions × 2 magnitudes).

Single-panel showing all six bootstrap distributions with:
- √3 vertical line (geometric hypothesis)
- H = 1 vertical line (symmetry null)
- Point estimates marked
- 95% CI intervals shown

Uses the actual values from Hemp_summary_both_definitions.csv
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import json

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

# Verified data from Hemp_summary_both_definitions.csv
specs = [
    # (label, n, Hemp, CI_low, CI_high, color, magnitude_type)
    ("Liberal (\u22652 yr)",  1305, 1.6822, 1.5097, 1.8809, '#1f77b4', 'abs'),
    ("Liberal (\u22652 yr)",  1305, 1.9619, 1.7092, 2.2581, '#1f77b4', 'net'),
    ("Standard (\u22655 yr,\n  \u22650.10)", 35, 1.5509, 1.3587, 1.7780, '#2ca02c', 'abs'),
    ("Standard (\u22655 yr,\n  \u22650.10)", 35, 1.5764, 1.3657, 1.8204, '#2ca02c', 'net'),
    ("Strict (\u22658 yr,\n  \u22650.20)",   10, 1.7267, 1.4621, 2.0755, '#d62728', 'abs'),
    ("Strict (\u22658 yr,\n  \u22650.20)",   10, 1.7056, 1.4289, 2.0600, '#d62728', 'net'),
]

sqrt3 = np.sqrt(3)

fig, ax = plt.subplots(figsize=(7.0, 4.5))

# Reverse order so the topmost row is the first specification
y_positions = np.arange(len(specs))[::-1]

# Draw competing hypothesis verticals
hypothesis_lines = [
    (sqrt3/2, r'$\sqrt{3}/2$', '#aaaaaa', ':'),
    (1.0, r'$\mathcal{H}=1$', '#666666', '--'),
    (sqrt3, r'$\sqrt{3}$', '#8c0000', '-'),
    (2*sqrt3, r'$2\sqrt{3}$', '#aaaaaa', ':'),
]
for h_val, h_label, h_color, h_style in hypothesis_lines:
    if h_val <= 3.6:
        is_main = (h_color == '#8c0000')
        ax.axvline(h_val, color=h_color, lw=1.4 if is_main else 0.7,
                   ls=h_style, zorder=1, alpha=0.95 if is_main else 0.8)

# Draw each spec
for i, (label, n, h, lo, hi, color, mag) in enumerate(specs):
    y = y_positions[i]

    # Lighter shade for "net", full for "abs"
    fill_color = color if mag == 'abs' else color
    edge_alpha = 1.0 if mag == 'abs' else 0.6

    # CI line
    ax.plot([lo, hi], [y, y], color=color, lw=2.2,
            solid_capstyle='round', alpha=edge_alpha, zorder=3)
    # Caps
    cap = 0.13
    ax.plot([lo, lo], [y-cap, y+cap], color=color, lw=1.0, alpha=edge_alpha, zorder=3)
    ax.plot([hi, hi], [y-cap, y+cap], color=color, lw=1.0, alpha=edge_alpha, zorder=3)
    # Point estimate
    marker = 'o' if mag == 'abs' else 's'
    ax.plot(h, y, marker=marker, color=color, markersize=8,
            markeredgecolor='white', markeredgewidth=1.0, zorder=4)

    # Annotate Hemp value and N to the right
    ax.text(2.4, y, f'$\\mathcal{{H}}={h:.3f}$  [{lo:.2f}, {hi:.2f}]',
            fontsize=7.5, va='center', color='#222')
    ax.text(3.25, y, f'N = {n}',
            fontsize=7.5, va='center', color='#666')

# Y-axis labels
ylabels = []
for i, (label, n, h, lo, hi, color, mag) in enumerate(specs):
    ylabels.append(f"{label}\n({mag} sum)" if mag == 'abs' else f"{label}\n(net)")

ax.set_yticks(y_positions)
ax.set_yticklabels([f"{specs[i][0]}\n{'abs sum' if specs[i][6]=='abs' else 'net'}"
                    for i in range(len(specs))], fontsize=8)

ax.set_xlim(0.7, 3.7)
ax.set_ylim(-0.7, len(specs) + 0.5)
ax.set_xlabel(r'Recovery-erosion asymmetry, $\mathcal{H}_{\rm emp}$', fontsize=9)
ax.set_title(r'Bootstrap 95% confidence intervals for $\mathcal{H}_{\rm emp}$ across six specifications',
             fontsize=10, pad=22, loc='left')

# Hypothesis labels placed above plot area, cleanly aligned with vertical stagger
y_label_main = len(specs) + 0.15
y_label_alt = len(specs) - 0.05  # slightly inside plot to differentiate
for h_val, h_label, h_color, h_style in hypothesis_lines:
    is_main = (h_color == '#8c0000')
    fontweight = 'bold' if is_main else 'normal'
    # Place "1" and "√3" at top; place "√3/2" and "2√3" inside top of plot area
    y_text = y_label_main if (h_val == 1.0 or is_main) else y_label_main - 0.15
    ax.text(h_val, y_text, h_label,
            fontsize=8.5 if is_main else 7.5, color=h_color,
            ha='center', va='bottom', fontweight=fontweight,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', edgecolor='none'))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='y', length=0)

# Legend for marker shapes
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#444',
               markersize=8, label='Abs-sum magnitude', markeredgecolor='white'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#444',
               markersize=8, label='Net-change magnitude', markeredgecolor='white'),
]
ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0.02, -0.18),
          fontsize=7.5, frameon=False, ncol=2)

# Footer note
ax.text(0.5, -0.27,
        r'$\sqrt{3}$ falls within the 95% CI for all six specifications;'
        r' the symmetry null ($\mathcal{H}=1$), $\sqrt{3}/2$, $2\sqrt{3}$, and $3\sqrt{3}$ are excluded.',
        transform=ax.transAxes, ha='center', fontsize=7.5, color='#444', style='italic')

plt.tight_layout()
plt.subplots_adjust(bottom=0.22, top=0.86)

plt.savefig('/home/claude/lindberg_final/figures/Figure3_hemp_bootstrap.pdf',
            bbox_inches='tight', pad_inches=0.05)
plt.savefig('/home/claude/lindberg_final/figures/Figure3_hemp_bootstrap.png',
            bbox_inches='tight', pad_inches=0.05, dpi=300)
print("Figure 3 saved.")
