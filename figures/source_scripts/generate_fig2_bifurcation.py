"""
Figure 2: The pitchfork bifurcation structure of the geometric threshold.

Two panels:
a) Bifurcation diagram (cleaner version of Fig 1c, with explicit Φ_c axis)
b) Potential landscapes U(Φ; S) at three stress levels: S=0.2, S=S₂, S=0.7
"""
import numpy as np
import matplotlib.pyplot as plt

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

COLOR_ACCENT = '#8c0000'
COLOR_STABLE = '#1a4d7a'
COLOR_UNSTABLE = '#888888'

S2 = np.sqrt(3)/4
Phi_c = 1 - S2
alpha = 1.0
lam = 1.5

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), constrained_layout=True)

# ---------- Panel a: Bifurcation diagram ----------
ax = axes[0]
S_vals = np.linspace(0, 0.78, 500)

Phi_stable_low = np.full_like(S_vals, np.nan)
Phi_upper = np.full_like(S_vals, np.nan)
Phi_lower = np.full_like(S_vals, np.nan)
Phi_unstable = np.full_like(S_vals, np.nan)

for i, S in enumerate(S_vals):
    if S <= S2:
        Phi_stable_low[i] = Phi_c
    else:
        Phi_unstable[i] = Phi_c
        delta = np.sqrt((S - S2) / lam)
        Phi_upper[i] = Phi_c + delta
        Phi_lower[i] = Phi_c - delta

ax.plot(S_vals, Phi_stable_low, color=COLOR_STABLE, lw=2.0)
ax.plot(S_vals, Phi_upper, color=COLOR_STABLE, lw=2.0)
ax.plot(S_vals, Phi_lower, color=COLOR_STABLE, lw=2.0)
ax.plot(S_vals, Phi_unstable, color=COLOR_UNSTABLE, lw=1.0, ls='--')

# Mark S₂
ax.axvline(S2, color=COLOR_ACCENT, lw=0.9, ls=':', zorder=0)
ax.plot(S2, Phi_c, 'o', color=COLOR_ACCENT, ms=5, zorder=5)
ax.annotate(r'$S_2 = \sqrt{3}/4$' + '\n' + r'(bifurcation)',
            xy=(S2, Phi_c), xytext=(S2-0.13, 0.20),
            fontsize=8, color=COLOR_ACCENT, ha='center',
            arrowprops=dict(arrowstyle='->', color=COLOR_ACCENT, lw=0.6))

# Branch labels
ax.text(0.72, Phi_c + np.sqrt((0.72-S2)/lam) + 0.04, 'Recovery branch',
        fontsize=8, color=COLOR_STABLE, ha='right', va='bottom', style='italic')
ax.text(0.72, Phi_c - np.sqrt((0.72-S2)/lam) - 0.04, 'Collapse branch',
        fontsize=8, color=COLOR_STABLE, ha='right', va='top', style='italic')
ax.text(0.55, Phi_c+0.015, 'Unstable',
        fontsize=7.5, color=COLOR_UNSTABLE, ha='center', va='bottom', style='italic')

# Shading
ax.axvspan(0, S2, alpha=0.04, color='#2ca02c', zorder=0)
ax.axvspan(S2, 0.78, alpha=0.05, color=COLOR_ACCENT, zorder=0)

ax.set_xlim(0, 0.78)
ax.set_ylim(0, 1.0)
ax.set_xlabel(r'Democratic stress, $S$', fontsize=9)
ax.set_ylabel(r'Equilibrium stability, $\Phi^*$', fontsize=9)
ax.set_title(r'$\mathbf{a}$  Bifurcation diagram', loc='left', fontsize=9, pad=4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Mark Phi_c on y-axis
ax.axhline(Phi_c, color='#cccccc', lw=0.5, ls=':', zorder=0)
ax.text(0.005, Phi_c+0.012, r'$\Phi_c$', fontsize=8, color='#666',
        ha='left', va='bottom')

# ---------- Panel b: Potential landscapes ----------
ax = axes[1]

def potential(Phi, S, alpha=1.0, lam=1.5):
    k = alpha * (S2 - S)
    return 0.5*k*(Phi-Phi_c)**2 + 0.25*lam*(Phi-Phi_c)**4

Phi_range = np.linspace(0.0, 1.0, 300)

stress_levels = [
    (0.20, '#2a7a2a', r'$S = 0.20$ (stable)', '-'),
    (S2,   COLOR_ACCENT, r'$S = S_2$ (critical)', '-'),
    (0.65, '#c44a4a', r'$S = 0.65$ (bistable)', '-'),
]

for S, color, label, ls in stress_levels:
    U = potential(Phi_range, S)
    # Normalize to a comparable scale
    U_plot = U - U.min()
    ax.plot(Phi_range, U_plot, color=color, lw=1.8, ls=ls, label=label)

# Mark Phi_c
ax.axvline(Phi_c, color='#cccccc', lw=0.5, ls=':', zorder=0)
ax.text(Phi_c, ax.get_ylim()[1]*0.85 if hasattr(ax, '_ylim') else 0.04,
        r'$\Phi_c$', fontsize=8, color='#666', ha='center', va='bottom')

ax.set_xlim(0.0, 1.0)
ax.set_xlabel(r'Stability, $\Phi$', fontsize=9)
ax.set_ylabel(r'Potential, $U(\Phi; S)$', fontsize=9)
ax.set_title(r'$\mathbf{b}$  Potential landscapes', loc='left', fontsize=9, pad=4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.legend(loc='upper right', fontsize=7.5, frameon=False)

# Save
import os
os.makedirs('/home/claude/lindberg_final/figures', exist_ok=True)
plt.savefig('/home/claude/lindberg_final/figures/Figure2_bifurcation.pdf',
            bbox_inches='tight', pad_inches=0.05)
plt.savefig('/home/claude/lindberg_final/figures/Figure2_bifurcation.png',
            bbox_inches='tight', pad_inches=0.05, dpi=300)
print("Figure 2 saved.")
