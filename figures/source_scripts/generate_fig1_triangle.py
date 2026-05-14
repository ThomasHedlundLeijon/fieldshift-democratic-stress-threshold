"""
Figure 1: Triangular three-pillar geometric model of democratic stability.

Three panels:
a) Fully consolidated democracy (R = M = N = 1), maximum triangle area
b) Critical threshold S₂ = √3/4 (area reduced)
c) Post-bifurcation regime showing bistable structure

Style: Nature-quality, vector PDF, sans-serif, restrained color palette.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch
from matplotlib.lines import Line2D

# Nature-style settings
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
    'pdf.fonttype': 42,  # Editable text
    'ps.fonttype': 42,
})

# Color palette - restrained, color-blind safe
COLOR_R = '#1f77b4'    # blue: Rule of law
COLOR_M = '#2ca02c'    # green: horizontal accountability
COLOR_N = '#d62728'    # red: democratic norms
COLOR_FILL = '#f0f0f0' # light grey triangle fill
COLOR_OUTLINE = '#333333'
COLOR_ACCENT = '#8c0000'  # dark red for critical markings

def vec(R, M, N):
    """Return the three vector endpoints from origin given pillar strengths."""
    pR = np.array([R, 0])
    pM = np.array([-M/2, M*np.sqrt(3)/2])
    pN = np.array([-N/2, -N*np.sqrt(3)/2])
    return pR, pM, pN

def triangle_area(pR, pM, pN):
    """Calculate triangle area from three vertex points."""
    u = pM - pR
    v = pN - pR
    return 0.5 * abs(u[0]*v[1] - u[1]*v[0])

fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)

# ---------- Panel a: Fully consolidated democracy ----------
ax = axes[0]
R, M, N = 1.0, 1.0, 1.0
pR, pM, pN = vec(R, M, N)
area = triangle_area(pR, pM, pN)
S = 1 - area / (3*np.sqrt(3)/4)  # normalised stress

# Draw triangle
tri = Polygon([pR, pM, pN], facecolor=COLOR_FILL, edgecolor=COLOR_OUTLINE, lw=1.0, zorder=1)
ax.add_patch(tri)

# Draw vectors from origin
for p, c, lbl in [(pR, COLOR_R, 'R'), (pM, COLOR_M, 'M'), (pN, COLOR_N, 'N')]:
    ax.annotate('', xy=p, xytext=(0,0),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=1.6, mutation_scale=10),
                zorder=3)
    # Label at vector tip
    offset = p / np.linalg.norm(p) * 0.18
    ax.text(p[0]+offset[0], p[1]+offset[1], lbl, color=c, fontsize=11, fontweight='bold',
            ha='center', va='center')

# Origin
ax.plot(0, 0, 'ko', ms=3, zorder=4)
ax.text(0.04, -0.06, 'O', fontsize=8, ha='left', va='top', color='#555')

# Area annotation
ax.text(0, 0.05, f'A = {area:.3f}', fontsize=8, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85))

ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.4, 1.15)
ax.set_aspect('equal')
ax.set_title(r'$\mathbf{a}$  Consolidated democracy', loc='left', fontsize=9, pad=4)
ax.text(0, -1.25, r'$R=M=N=1,\ \ S = 0$',
        ha='center', va='center', fontsize=8, color='#444')
ax.axis('off')

# ---------- Panel b: Critical threshold S₂ = √3/4 ----------
ax = axes[1]
# Find pillar values that give S = √3/4 (i.e., A = (3√3/4)·(1-√3/4) = 3·(4-√3)/16 ≈ 0.4253)
# Simplest: scale all three pillars equally. A scales as (RM+RN+MN)/3 = R² for R=M=N
# Need A_norm = 1 - √3/4 ≈ 0.567, so R² = 0.567, R ≈ 0.753
S2 = np.sqrt(3)/4
A_norm_target = 1 - S2  # normalised stability at threshold
R_crit = np.sqrt(A_norm_target)
R, M, N = R_crit, R_crit, R_crit
pR, pM, pN = vec(R, M, N)
area = triangle_area(pR, pM, pN)
S_actual = 1 - area / (3*np.sqrt(3)/4)

# Original (faint) reference triangle at full capacity
pR0, pM0, pN0 = vec(1, 1, 1)
tri0 = Polygon([pR0, pM0, pN0], facecolor='none', edgecolor='#bbbbbb', lw=0.6, ls='--', zorder=1)
ax.add_patch(tri0)

# Current triangle (at S₂)
tri = Polygon([pR, pM, pN], facecolor=COLOR_FILL, edgecolor=COLOR_OUTLINE, lw=1.0, zorder=2)
ax.add_patch(tri)

# Vectors
for p, c, lbl in [(pR, COLOR_R, 'R'), (pM, COLOR_M, 'M'), (pN, COLOR_N, 'N')]:
    ax.annotate('', xy=p, xytext=(0,0),
                arrowprops=dict(arrowstyle='-|>', color=c, lw=1.6, mutation_scale=10),
                zorder=3)
    offset = p / np.linalg.norm(p) * 0.18
    ax.text(p[0]+offset[0], p[1]+offset[1], lbl, color=c, fontsize=11, fontweight='bold',
            ha='center', va='center')

ax.plot(0, 0, 'ko', ms=3, zorder=4)

# Annotation
ax.text(0, 0.05, f'A = {area:.3f}', fontsize=8, ha='center', va='center',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85))

ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.4, 1.15)
ax.set_aspect('equal')
ax.set_title(r'$\mathbf{b}$  Critical threshold $S_2 = \sqrt{3}/4$', loc='left', fontsize=9, pad=4)
ax.text(0, -1.25, fr'$S \approx {S_actual:.3f}$,  bifurcation point',
        ha='center', va='center', fontsize=8, color='#444')
ax.axis('off')

# ---------- Panel c: Post-bifurcation bistability ----------
ax = axes[2]
# Show bifurcation diagram: Φ vs S
S_vals = np.linspace(0, 0.85, 300)
Phi_c = 1 - S2

# Stable branch below S₂: Φ = Φ_c (single equilibrium)
# Above S₂: bistability - two stable branches Φ_c ± sqrt((S - S₂)/λ_eff)
# Use illustrative λ_eff
lam = 1.5

Phi_lower_branch = np.full_like(S_vals, np.nan)
Phi_upper_branch = np.full_like(S_vals, np.nan)
Phi_central_stable = np.full_like(S_vals, np.nan)
Phi_central_unstable = np.full_like(S_vals, np.nan)

for i, S in enumerate(S_vals):
    if S < S2:
        Phi_central_stable[i] = Phi_c
    else:
        Phi_central_unstable[i] = Phi_c
        delta = np.sqrt((S - S2) / lam)
        Phi_lower_branch[i] = Phi_c - delta
        Phi_upper_branch[i] = Phi_c + delta

ax.plot(S_vals, Phi_central_stable, color='#1a4d7a', lw=1.8)
ax.plot(S_vals, Phi_central_unstable, color='#888888', lw=1.0, ls='--')
ax.plot(S_vals, Phi_lower_branch, color='#1a4d7a', lw=1.8)
ax.plot(S_vals, Phi_upper_branch, color='#1a4d7a', lw=1.8)

# Mark S₂
ax.axvline(S2, color=COLOR_ACCENT, lw=0.9, ls=':', zorder=0)

# Mark bifurcation point with a small circle
ax.plot(S2, Phi_c, 'o', color=COLOR_ACCENT, ms=4.5, zorder=5)
ax.annotate(r'$S_2 = \sqrt{3}/4$', xy=(S2, Phi_c), xytext=(S2+0.05, 0.75),
            fontsize=8, color=COLOR_ACCENT,
            arrowprops=dict(arrowstyle='-', color=COLOR_ACCENT, lw=0.5))

# Labels for branches - placed inside plot
ax.text(0.68, Phi_c + np.sqrt((0.68-S2)/lam) + 0.04, 'Recovery',
        fontsize=7.5, color='#1a4d7a', ha='center', va='bottom', style='italic')
ax.text(0.68, Phi_c - np.sqrt((0.68-S2)/lam) - 0.04, 'Collapse',
        fontsize=7.5, color='#1a4d7a', ha='center', va='top', style='italic')

# Region shading
ax.axvspan(0, S2, alpha=0.04, color='#2ca02c', zorder=0)
ax.axvspan(S2, 0.78, alpha=0.05, color=COLOR_ACCENT, zorder=0)
ax.text(S2/2, 0.03, 'Stable', fontsize=7.5, color='#2a7a2a',
        ha='center', va='bottom', transform=ax.get_xaxis_transform(), style='italic')
ax.text((S2+0.78)/2, 0.03, 'Bistable', fontsize=7.5, color=COLOR_ACCENT,
        ha='center', va='bottom', transform=ax.get_xaxis_transform(), style='italic')

ax.set_xlim(0, 0.78)
ax.set_ylim(0, 1.0)
ax.set_xlabel(r'Democratic stress, $S$', fontsize=9)
ax.set_ylabel(r'Stability, $\Phi$', fontsize=9)
ax.set_title(r'$\mathbf{c}$  Pitchfork bifurcation', loc='left', fontsize=9, pad=4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save
plt.savefig('/home/claude/lindberg_final/figures/Figure1_geometric_model.pdf',
            bbox_inches='tight', pad_inches=0.05)
plt.savefig('/home/claude/lindberg_final/figures/Figure1_geometric_model.png',
            bbox_inches='tight', pad_inches=0.05, dpi=300)
print("Figure 1 saved successfully.")
print(f"S₂ = √3/4 = {S2:.6f}")
print(f"Area at threshold = {area:.4f}")
print(f"Actual S at threshold = {S_actual:.4f}")
