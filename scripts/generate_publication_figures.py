"""
Generate all publication-quality figures for the manuscript.
Targets: 300 DPI, serif fonts, minimal spines, journal-ready style.
"""
import sys, warnings, gc
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import polars as pl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path

BASE_DIR   = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects')
TABLES_DIR = BASE_DIR / 'outputs' / 'tables'
FIGS_DIR   = BASE_DIR / 'outputs' / 'figures'

# ── Style ──────────────────────────────────────────────────────────────────────
BLUE   = '#1565C0'
RED    = '#C62828'
ORANGE = '#E65100'
GRAY   = '#546E7A'
GREEN  = '#2E7D32'
LBLUE  = '#90CAF9'
LRED   = '#FFCDD2'

plt.rcParams.update({
    'figure.dpi': 150, 'savefig.dpi': 300,
    'font.family': 'DejaVu Serif',
    'font.size': 11,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.labelsize': 12, 'axes.titlesize': 12,
    'legend.fontsize': 10, 'legend.framealpha': 0.9,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
})

# ── Load key data ──────────────────────────────────────────────────────────────
print("Loading CSV data...")

annual_df   = pd.read_csv(TABLES_DIR / 'nb19_annual_ate.csv')
subgrp_df   = pd.read_csv(TABLES_DIR / 'nb21_cate_subgroups.csv')
shap_df     = pd.read_csv(TABLES_DIR / 'nb22_shap_importance.csv')
did_df      = pd.read_csv(TABLES_DIR / 'nb25_did_results.csv')
es_df       = pd.read_csv(TABLES_DIR / 'nb25_event_study.csv')
rdd_df      = pd.read_csv(TABLES_DIR / 'nb24_rdd_results.csv')
rob_df      = pd.read_csv(TABLES_DIR / 'nb26_estimator_comparison.csv')
plac_df     = pd.read_csv(TABLES_DIR / 'nb28_placebo_results.csv')
bal_df      = pd.read_csv(TABLES_DIR / 'covariate_balance.csv')
dml_df      = pd.read_csv(TABLES_DIR / 'nb19_dml_ate_results.csv')
cate_sum    = pd.read_csv(TABLES_DIR / 'nb21_cate_summary.csv')
bw_df       = pd.read_csv(TABLES_DIR / 'nb24_bandwidth_sensitivity.csv')
cont_df     = pd.read_csv(TABLES_DIR / 'nb24_covariate_continuity.csv')
plac_thr    = pd.read_csv(TABLES_DIR / 'nb24_placebo_thresholds.csv')

# Load a small sample for descriptive figures
print("Loading data sample (800K rows)...")
lf = pl.scan_parquet(str(BASE_DIR / 'data' / 'features_panel.parquet'))
rng = np.random.default_rng(0)

# For descriptive stats: sample 800K
df_s = lf.collect()
idx_s = rng.choice(len(df_s), size=800_000, replace=False)
df_small = df_s[idx_s].to_pandas()
print(f"Sample loaded: {len(df_small):,}")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Overview Panel — Key Descriptive Statistics
# ══════════════════════════════════════════════════════════════════════════════
print("\nFig 1: Overview panel...")

fig = plt.figure(figsize=(14, 10))
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

ax1 = fig.add_subplot(gs[0, 0])  # Approval rate by race over time
ax2 = fig.add_subplot(gs[0, 1])  # Raw gap vs DML-adjusted gap
ax3 = fig.add_subplot(gs[0, 2])  # Income distribution by race
ax4 = fig.add_subplot(gs[1, 0])  # DTI distribution by race
ax5 = fig.add_subplot(gs[1, 1])  # LTV distribution by race
ax6 = fig.add_subplot(gs[1, 2])  # Covariate balance summary

# 1a: Approval rate by year
years = [2020, 2021, 2022, 2023, 2024]
black_rates = []
white_rates = []
for yr in years:
    grp = df_small[df_small['year'] == yr]
    if len(grp) > 1000:
        black_rates.append(grp[grp['black'] == 1]['approved'].mean() * 100)
        white_rates.append(grp[grp['black'] == 0]['approved'].mean() * 100)

ax1.plot(years[:len(white_rates)], white_rates, 'o-', color=BLUE, lw=2.5, ms=7, label='White applicants')
ax1.plot(years[:len(black_rates)], black_rates, 's--', color=RED, lw=2.5, ms=7, label='Black applicants')
ax1.fill_between(years[:len(white_rates)],
                 [w - (w - b) for w, b in zip(white_rates, black_rates)],
                 white_rates, alpha=0.1, color=BLUE)
ax1.set_xlabel('Year')
ax1.set_ylabel('Approval Rate (%)')
ax1.set_title('(a) Approval Rates by Race,\n2020–2024')
ax1.legend(loc='lower right', fontsize=9)
ax1.set_xticks(years)
ax1.set_ylim(60, 90)

# 1b: Raw gap vs adjusted gap by year
es_years = es_df['year'].values
raw_gaps = es_df['gap'].values
adj_gaps = annual_df['ate_pp'].abs().values

ax2.bar(np.array(years) - 0.2, raw_gaps[:5], width=0.38, color=ORANGE, alpha=0.8, label='Observed gap (pp)')
ax2.bar(np.array(years) + 0.2, adj_gaps[:5], width=0.38, color=BLUE, alpha=0.8, label='DML-adjusted penalty (|pp|)')
ax2.set_xlabel('Year')
ax2.set_ylabel('Racial Gap (percentage points)')
ax2.set_title('(b) Observed vs. Risk-Adjusted\nApproval Gap by Year')
ax2.legend(loc='upper right', fontsize=9)
ax2.set_xticks(years)

# 1c: Income distribution
inc_black = df_small[df_small['black'] == 1]['income'].dropna().clip(0, 300).values
inc_white = df_small[df_small['black'] == 0]['income'].dropna().clip(0, 300).values
ax3.hist(inc_white, bins=60, density=True, alpha=0.6, color=BLUE, label='White', range=(0, 300))
ax3.hist(inc_black, bins=60, density=True, alpha=0.6, color=RED, label='Black', range=(0, 300))
ax3.axvline(np.median(inc_white), color=BLUE, lw=1.5, linestyle='--', alpha=0.9, label=f'White median ${np.median(inc_white):.0f}K')
ax3.axvline(np.median(inc_black), color=RED, lw=1.5, linestyle='--', alpha=0.9, label=f'Black median ${np.median(inc_black):.0f}K')
ax3.set_xlabel('Applicant Income ($K)')
ax3.set_ylabel('Density')
ax3.set_title('(c) Income Distribution by Race')
ax3.legend(fontsize=8)

# 1d: DTI distribution
dti_black = df_small[df_small['black'] == 1]['dti_midpoint'].dropna().clip(0, 60).values
dti_white = df_small[df_small['black'] == 0]['dti_midpoint'].dropna().clip(0, 60).values
ax4.hist(dti_white, bins=50, density=True, alpha=0.6, color=BLUE, label='White', range=(0, 65))
ax4.hist(dti_black, bins=50, density=True, alpha=0.6, color=RED, label='Black', range=(0, 65))
ax4.axvline(43, color='gray', lw=2, linestyle=':', label='QM limit (43%)')
ax4.set_xlabel('Debt-to-Income Ratio (%)')
ax4.set_ylabel('Density')
ax4.set_title('(d) DTI Distribution by Race\n(gray: Qualified Mortgage limit)')
ax4.legend(fontsize=8)

# 1e: LTV distribution
ltv_black = df_small[df_small['black'] == 1]['ltv'].dropna().clip(40, 100).values
ltv_white = df_small[df_small['black'] == 0]['ltv'].dropna().clip(40, 100).values
ax5.hist(ltv_white, bins=60, density=True, alpha=0.6, color=BLUE, label='White', range=(40, 100))
ax5.hist(ltv_black, bins=60, density=True, alpha=0.6, color=RED, label='Black', range=(40, 100))
ax5.axvline(80, color='gray', lw=2, linestyle=':', label='LTV=80% (PMI cutoff)')
ax5.set_xlabel('Loan-to-Value Ratio (%)')
ax5.set_ylabel('Density')
ax5.set_title('(e) LTV Distribution by Race\n(gray: PMI cutoff)')
ax5.legend(fontsize=8)

# 1f: Covariate balance (standardised differences)
bal_vars = bal_df['variable'].tolist()
std_diffs = bal_df['std_diff'].tolist()
colors_bal = [RED if abs(d) > 0.1 else (ORANGE if abs(d) > 0.05 else GREEN) for d in std_diffs]
ax6.barh(range(len(bal_vars)), std_diffs, color=colors_bal, alpha=0.8)
ax6.axvline(-0.1, color='gray', lw=1, linestyle='--', alpha=0.7)
ax6.axvline(0.1, color='gray', lw=1, linestyle='--', alpha=0.7, label='±0.1 threshold')
ax6.axvline(0, color='black', lw=0.8)
ax6.set_yticks(range(len(bal_vars)))
ax6.set_yticklabels([v[:22] for v in bal_vars], fontsize=8)
ax6.set_xlabel('Standardised Difference (Black − White)')
ax6.set_title('(f) Pre-Treatment Covariate\nBalance')
ax6.legend(fontsize=8)

fig.suptitle('Figure 1: Descriptive Overview — Race, Creditworthiness, and Mortgage Outcomes\n(HMDA 2020–2024, N=42.3M applications)', fontsize=13, fontweight='bold', y=1.01)
plt.savefig(FIGS_DIR / 'fig1_descriptive_overview.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig1_descriptive_overview.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: DML Results Panel
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 2: DML results panel...")

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

ax = axes[0]
dml_y = annual_df['ate_pp'].values
ci_lo = annual_df['ci_lower'].values
ci_hi = annual_df['ci_upper'].values
colors_yr = [BLUE] * 5
bars = ax.bar(years, dml_y, color=colors_yr, alpha=0.85, width=0.55, zorder=3)
yerr_lo = dml_y - ci_lo   # positive values (lower error bar)
yerr_hi = ci_hi - dml_y   # positive values (upper error bar)
ax.errorbar(years, dml_y, yerr=[yerr_lo, yerr_hi],
            fmt='none', color='black', capsize=6, capthick=2, linewidth=2, zorder=4)
ax.axhline(0, color='black', lw=0.8)
ax.axhline(-9.38, color=GRAY, lw=1.5, linestyle='--', alpha=0.8, label='Pooled 2020–2024: −9.38 pp')
ax.set_xticks(years)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('DML Racial Penalty (pp)', fontsize=12)
ax.set_title('(a) Annual DML Estimates\n(controlling for 33 creditworthiness features)', fontsize=12)
ax.legend(fontsize=9)
for b, v in zip(bars, dml_y):
    ax.text(b.get_x() + b.get_width()/2, v - 0.4, f'{v:.2f}',
            ha='center', va='top', fontsize=9, color='white', fontweight='bold')
ax.set_ylim(-12, 0)

ax2 = axes[1]
# Feature set comparison
features = ['DML (33 features,\nfull specification)', 'DML (4 features,\nbaseline spec)']
ates = [-9.385, -13.172]
colors_fs = [BLUE, ORANGE]
bars2 = ax2.bar(features, ates, color=colors_fs, alpha=0.85, width=0.45)
ax2.axhline(0, color='black', lw=0.8)
raw = -14.95
ax2.axhline(raw, color=RED, lw=2, linestyle='--', label=f'Unconditional gap: {raw:.2f} pp')
ax2.set_ylabel('Racial Penalty (pp)', fontsize=12)
ax2.set_title('(b) Feature Set Sensitivity\n(more controls = smaller but still large penalty)', fontsize=12)
ax2.legend(fontsize=9)
for b, v in zip(bars2, ates):
    ax2.text(b.get_x() + b.get_width()/2, v + 0.2, f'{v:.2f} pp',
             ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.set_ylim(-16, 1)

pct_exp = f"{100 - 62.8:.1f}%"
pct_unexp = f"{62.8:.1f}%"
ax2.text(0.5, -0.15, f'Observed gap: −14.95 pp | DML-explained: {pct_exp} | Unexplained: {pct_unexp}',
         ha='center', va='top', transform=ax2.transAxes, fontsize=9, color='gray',
         style='italic')

fig.suptitle('Figure 2: Double Machine Learning Estimates of the Racial Approval Penalty\n(HMDA 2020–2024)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig2_dml_results.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig2_dml_results.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3: CATE Distribution
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 3: CATE distribution...")

cate_est = pd.read_parquet(str(BASE_DIR / 'data' / 'cate_estimates.parquet'))
print(f"  CATE estimates loaded: {len(cate_est):,}")
cate_col = [c for c in cate_est.columns if 'cate' in c.lower() or 'effect' in c.lower()]
print(f"  CATE columns: {cate_col}")

if cate_col:
    cate_vals = cate_est[cate_col[0]].values * 100
else:
    cate_vals = cate_est.iloc[:, -1].values * 100

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

ax = axes[0]
ax.hist(cate_vals, bins=100, density=True, color=BLUE, alpha=0.75, range=(-50, 20),
        label=f'CATE distribution (N={len(cate_vals)/1e6:.1f}M)')
ax.axvline(np.mean(cate_vals), color=RED, lw=2.5, linestyle='-', label=f'Mean: {np.mean(cate_vals):.2f} pp')
ax.axvline(np.median(cate_vals), color=ORANGE, lw=2.5, linestyle='--', label=f'Median: {np.median(cate_vals):.2f} pp')
ax.axvline(0, color='black', lw=1, linestyle=':', label='Zero (no penalty)')
pct_neg = (cate_vals < 0).mean() * 100
ax.text(0.02, 0.97, f'{pct_neg:.1f}% of applicants penalised\n(CATE < 0)',
        transform=ax.transAxes, va='top', fontsize=10, color=RED,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
ax.set_xlabel('Individual CATE (percentage points)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.set_title('(a) Distribution of Conditional Average\nTreatment Effects (CATEs)', fontsize=12)
ax.legend(loc='upper left', fontsize=9)
ax.set_xlim(-50, 20)

ax2 = axes[1]
# CATE percentile distribution
pctiles = np.percentile(cate_vals, np.linspace(0, 100, 101))
ax2.plot(np.linspace(0, 100, 101), pctiles, color=BLUE, lw=2.5)
ax2.fill_between(np.linspace(0, 100, 101), pctiles, 0, where=pctiles < 0,
                 color=RED, alpha=0.3, label='Penalised (CATE < 0)')
ax2.fill_between(np.linspace(0, 100, 101), pctiles, 0, where=pctiles >= 0,
                 color=GREEN, alpha=0.3, label='Not penalised (CATE ≥ 0)')
ax2.axhline(0, color='black', lw=1, linestyle='--')
p10, p25, p75, p90 = np.percentile(cate_vals, [10, 25, 75, 90])
for pct, val in [(10, p10), (25, p25), (75, p75), (90, p90)]:
    ax2.annotate(f'P{pct}: {val:.1f} pp', (pct, val),
                 xytext=(pct + 5, val - 2), fontsize=8,
                 arrowprops=dict(arrowstyle='->', color='gray'))
ax2.set_xlabel('Percentile', fontsize=12)
ax2.set_ylabel('CATE (percentage points)', fontsize=12)
ax2.set_title('(b) CATE Percentile Distribution\n(heterogeneity: SD = 8.47 pp)', fontsize=12)
ax2.legend(fontsize=9)

fig.suptitle('Figure 3: Heterogeneous Treatment Effects — Who Faces the Largest Penalty?\n(CausalForestDML on 1.5M observations)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig3_cate_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig3_cate_distribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Subgroup CATE Heterogeneity
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 4: Subgroup heterogeneity...")

# Filter to key subgroups for main figure
key_groups = ['Automated AUS', 'Manual/exempt AUS',
              'LTV <= 80%', 'LTV > 80%',
              'Purchase loans', 'Refinance loans',
              'Low DTI (<43%)', 'High DTI (>=43%)',
              'Income Q1', 'Income Q5',
              'Large lenders', 'Small lenders']

sub = subgrp_df[subgrp_df['subgroup'].isin(key_groups)].copy()
sub = sub.set_index('subgroup').reindex(key_groups).reset_index()

fig, ax = plt.subplots(figsize=(10, 8))

colors_sg = [RED if v < -12 else (ORANGE if v < -9 else BLUE) for v in sub['mean_cate'].values]
bars = ax.barh(range(len(sub)), sub['mean_cate'].values, color=colors_sg, alpha=0.85, height=0.65)
ax.errorbar(sub['mean_cate'].values, range(len(sub)),
            xerr=1.96 * sub['se'].values,
            fmt='none', color='black', capsize=5, linewidth=1.5)
ax.axvline(-9.08, color=GRAY, lw=2, linestyle='--', alpha=0.8, label='Pooled mean: −9.08 pp')
ax.axvline(0, color='black', lw=0.8)
ax.set_yticks(range(len(sub)))
ax.set_yticklabels(sub['subgroup'].values, fontsize=10)
ax.set_xlabel('Mean CATE (percentage points)', fontsize=12)
ax.set_title('Figure 4: Heterogeneity in Racial Penalty Across Applicant Subgroups\n(bars = 95% CI; N per group shown right)', fontsize=12)
ax.legend(fontsize=10)

for i, (v, n, pct) in enumerate(zip(sub['mean_cate'].values, sub['n'].values, sub['pct_penalised'].values)):
    ax.text(1, i, f' N={n/1000:.0f}K | {pct:.0f}% penalised', va='center', fontsize=8, color='gray')

# Add separator lines between groups
separators = [2, 4, 6, 8, 10]
for s in separators:
    ax.axhline(s - 0.5, color='lightgray', lw=1, linestyle='-')

ax.set_xlim(-20, 5)
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig4_subgroup_heterogeneity.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig4_subgroup_heterogeneity.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5: SHAP Attribution Panel
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 5: SHAP panel...")

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

ax = axes[0]
shap_plot = shap_df.sort_values('mean_abs_shap', ascending=True).tail(10)
bars = ax.barh(range(len(shap_plot)), shap_plot['mean_abs_shap'].values,
               color=[RED if 'aus' in n.lower() else BLUE for n in shap_plot['display_name'].values],
               alpha=0.85, height=0.65)
ax.set_yticks(range(len(shap_plot)))
ax.set_yticklabels(shap_plot['display_name'].values, fontsize=10)
ax.set_xlabel('Mean |SHAP| value (average impact on CATE)', fontsize=11)
ax.set_title('(a) SHAP Feature Importance\n(predictive contribution to CATE variation)', fontsize=12)
# Red patch for AUS
from matplotlib.patches import Patch
legend_handles = [Patch(color=RED, alpha=0.85, label='AUS type (top predictor)'),
                  Patch(color=BLUE, alpha=0.85, label='Other features')]
ax.legend(handles=legend_handles, fontsize=9)
for b, v in zip(bars, shap_plot['mean_abs_shap'].values):
    ax.text(v + 0.02, b.get_y() + b.get_height()/2, f'{v:.3f}',
            va='center', fontsize=9)

ax2 = axes[1]
# AUS contrast
aus_contrast = -14.793 - (-6.168)
groups = ['Automated AUS\n(−6.17 pp)', 'Manual/Exempt AUS\n(−14.79 pp)']
vals = [-6.168, -14.793]
cols = [BLUE, RED]
bars2 = ax2.bar(groups, vals, color=cols, alpha=0.85, width=0.5)
ax2.axhline(-9.08, color=GRAY, lw=2, linestyle='--', label='Pooled mean: −9.08 pp')
ax2.set_ylabel('Mean CATE (pp)', fontsize=12)
ax2.set_title(f'(b) Automated vs. Manual AUS Channel\n(contrast = {aus_contrast:.2f} pp)', fontsize=12)
ax2.legend(fontsize=10)
ax2.text(1, -14.793 - 0.6, f'Δ = {aus_contrast:.2f} pp\n(discretion channel)', ha='center',
         fontsize=10, color=RED, fontweight='bold')
ax2.set_ylim(-18, -1)
ax2.axhline(0, color='black', lw=0.8)

fig.suptitle('Figure 5: SHAP Attribution — Automated Underwriting System Type is the\nStrongest Predictor of CATE Variation (consistent with institutional discretion channel)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig5_shap_attribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig5_shap_attribution.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6: RDD Main + Diagnostics
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 6: RDD panel...")

fig, axes = plt.subplots(2, 2, figsize=(13, 10))
fig.suptitle('Figure 6: Regression Discontinuity Design at LTV=80% (PMI Threshold)',
             fontsize=13, fontweight='bold', y=1.01)

# 6a: RDD main (use rdd_df)
ax = axes[0, 0]
rdd_sub = rdd_df.set_index('group')
groups_rdd = ['Full sample', 'Purchase loans', 'Refinance loans']
discs = [rdd_sub.loc[g, 'discontinuity'] for g in groups_rdd if g in rdd_sub.index]
ses_rdd = [rdd_sub.loc[g, 'se'] for g in groups_rdd if g in rdd_sub.index]
groups_avail = [g for g in groups_rdd if g in rdd_sub.index]
colors_rdd = [BLUE, GREEN, ORANGE]
bars_rdd = ax.bar(groups_avail, discs, color=colors_rdd[:len(groups_avail)], alpha=0.85, width=0.5)
ax.errorbar(range(len(discs)), discs, yerr=1.96 * np.array(ses_rdd),
            fmt='none', color='black', capsize=6, capthick=2)
ax.axhline(0, color='black', lw=0.8)
ax.set_ylabel('Racial Gap Discontinuity (pp)', fontsize=11)
ax.set_title('(a) RDD Estimates by Loan Type\n(all samples, BW=5%)', fontsize=11)
for b, v in zip(bars_rdd, discs):
    ax.text(b.get_x() + b.get_width()/2, v + 0.05, f'{v:.2f} pp', ha='center', fontsize=10, fontweight='bold')

# 6b: Bandwidth sensitivity
ax2 = axes[0, 1]
ax2.errorbar(bw_df['bandwidth'], bw_df['discontinuity'],
             yerr=1.96 * bw_df['se'],
             fmt='o-', color=BLUE, lw=2, ms=7, capsize=5, capthick=2,
             label='RDD estimate ± 1.96 SE')
ax2.axhline(0, color='gray', lw=1, linestyle='--')
ax2.axhline(1.812, color=GRAY, lw=1.5, linestyle=':', alpha=0.7, label='Main estimate (BW=5): 1.81 pp')
ax2.set_xlabel('Bandwidth (LTV pp)', fontsize=11)
ax2.set_ylabel('Discontinuity (pp)', fontsize=11)
ax2.set_title('(b) Bandwidth Sensitivity\n(estimate stable at narrow BW)', fontsize=11)
ax2.legend(fontsize=9)

# 6c: Placebo thresholds
ax3 = axes[1, 0]
plac_colors = [RED if p else BLUE for p in plac_thr['is_real']]
plac_sizes = [150 if p else 80 for p in plac_thr['is_real']]
ax3.scatter(plac_thr['cutoff'], plac_thr['discontinuity'], c=plac_colors, s=plac_sizes, zorder=5)
ax3.errorbar(plac_thr['cutoff'], plac_thr['discontinuity'],
             yerr=1.96 * plac_thr['se'],
             fmt='none', color='gray', capsize=4, alpha=0.6)
ax3.axhline(0, color='black', lw=0.8)
ax3.axvline(80, color=RED, lw=1.5, linestyle='--', label='True cutoff (LTV=80%)', alpha=0.7)
real_disc = plac_thr[plac_thr['is_real']]['discontinuity'].values[0]
ax3.annotate(f'True: {real_disc:.2f} pp', (80, real_disc),
             xytext=(82, real_disc + 0.5), fontsize=9, color=RED,
             arrowprops=dict(arrowstyle='->', color=RED))
ax3.set_xlabel('LTV Cutoff (%)', fontsize=11)
ax3.set_ylabel('Discontinuity (pp)', fontsize=11)
ax3.set_title('(c) Placebo Cutoffs\n(spike at true cutoff)', fontsize=11)
ax3.legend(fontsize=9)

# 6d: Covariate continuity
ax4 = axes[1, 1]
cont_colors = [GREEN if p else ORANGE for p in cont_df['continuous']]
ax4.barh(cont_df['covariate'].values, cont_df['diff'].values, color=cont_colors, alpha=0.85)
ax4.axvline(0, color='black', lw=0.8)
for i, (v, p) in enumerate(zip(cont_df['diff'].values, cont_df['p_value'].values)):
    flag = '✓' if p > 0.05 else '✗'
    ax4.text(v + 0.01 if v >= 0 else v - 0.01, i,
             f' {flag} p={p:.3f}', va='center', fontsize=9,
             ha='left' if v >= 0 else 'right')
ax4.set_xlabel('Diff. in covariate mean (above − below LTV=80%)', fontsize=11)
ax4.set_title('(d) Covariate Continuity Test\n(✓ = continuous at cutoff; ✗ = jumps)', fontsize=11)

plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig6_rdd_diagnostics.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig6_rdd_diagnostics.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 7: Event Study + DiD
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 7: Event study / DiD...")

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# 7a: Event study
ax = axes[0]
es_years = es_df['year'].values
es_gaps  = es_df['gap'].values
es_ses   = es_df['se'].values

ax.fill_between(es_years, es_gaps - 1.96 * es_ses, es_gaps + 1.96 * es_ses,
                alpha=0.15, color=BLUE)
ax.plot(es_years, es_gaps, 'o-', color=BLUE, lw=2.5, ms=9, zorder=5, label='Racial approval gap')
ax.axvspan(2021.5, 2024.5, alpha=0.07, color=RED, label='Post-tightening period (2022–)')
ax.axhline(es_gaps[0], color=GRAY, lw=1.5, linestyle='--', alpha=0.7, label='2020 baseline gap')

for y, g, se in zip(es_years, es_gaps, es_ses):
    ax.annotate(f'{g:.1f} pp', (y, g + 0.5), ha='center', fontsize=9.5, color=BLUE, fontweight='bold')

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Racial Approval Gap (pp)\n(White − Black)', fontsize=12)
ax.set_title('(a) Evolution of the Racial Approval Gap\n(2020–2024)', fontsize=12)
ax.set_xticks(es_years)
ax.set_ylim(11, 18)
ax.legend(fontsize=9, loc='lower right')

# 7b: DiD by subgroup
ax2 = axes[1]
did_sub = did_df[did_df['group'].isin([
    'Full sample', 'Q4 (most penalised)', 'Q1 (least penalised)',
    'Automated AUS', 'Manual/exempt', 'Income Q1 <$60K', 'Income Q5 >$180K'
])].copy()

did_vals  = did_sub['did'].values
did_ses   = did_sub['se'].values
did_names = did_sub['group'].values
did_colors = [BLUE if g == 'Full sample' else (RED if d > 1.5 else (GREEN if d < 0 else ORANGE))
              for g, d in zip(did_names, did_vals)]

bars7 = ax2.barh(range(len(did_names)), did_vals, color=did_colors, alpha=0.85, height=0.6)
ax2.errorbar(did_vals, range(len(did_names)),
             xerr=1.96 * did_ses,
             fmt='none', color='black', capsize=5, linewidth=1.5)
ax2.axvline(0, color='black', lw=0.8)
ax2.axvline(0.987, color=GRAY, lw=1.5, linestyle='--', alpha=0.7, label='Full sample DiD: +0.99 pp')
ax2.set_yticks(range(len(did_names)))
ax2.set_yticklabels(did_names, fontsize=10)
ax2.set_xlabel('DiD Estimate (pp)', fontsize=12)
ax2.set_title('(b) Post-2022 DiD Estimates by Subgroup\n(gap widened most for low-income, penalised groups)', fontsize=12)
ax2.legend(fontsize=9)
for b, v, p in zip(bars7, did_vals, did_sub['p_value'].values):
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else ''))
    ax2.text(v + 0.05 if v >= 0 else v - 0.05, b.get_y() + b.get_height()/2,
             f' {v:+.2f}{sig}', va='center', fontsize=9,
             ha='left' if v >= 0 else 'right')

fig.suptitle('Figure 7: Difference-in-Differences — Post-2022 Rate Tightening Exacerbated the Racial Penalty\nfor the Most Vulnerable Applicants', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig7_event_study_did.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig7_event_study_did.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 8: Robustness and Placebo Panel
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 8: Robustness panel...")

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

ax = axes[0]
estimators = rob_df['estimator'].values
ates = rob_df['ate_pp'].values
stds = rob_df['std_pp'].values
colors_rob = [BLUE, RED, GRAY]

bars8 = ax.barh(range(len(estimators)), ates, color=colors_rob, alpha=0.85)
ax.axvline(0, color='black', lw=0.8)
ax.axvline(-9.08, color=GRAY, lw=1.5, linestyle='--', alpha=0.7, label='Main estimate: −9.08 pp')
ax.set_yticks(range(len(estimators)))
ax.set_yticklabels(estimators, fontsize=10)
ax.set_xlabel('Mean ATE (pp)', fontsize=12)
ax.set_title('(a) ATE Across Estimators\n(all methods converge near −9 pp)', fontsize=12)
ax.legend(fontsize=9)
for b, v in zip(bars8, ates):
    ax.text(v - 0.2, b.get_y() + b.get_height()/2, f'{v:.2f} pp',
            va='center', ha='right', fontsize=9.5, color='white', fontweight='bold')

ax2 = axes[1]
plac_real = plac_df[plac_df['type'] == 'real'].iloc[0]
plac_shuf = plac_df[plac_df['type'] == 'race_shuffle']
plac_labels = ['Real CATEs\n(race→approval)'] + [f'Shuffle #{r["permutation"]}' for _, r in plac_shuf.iterrows()]
plac_stds   = [plac_real['std_pp']] + plac_shuf['std_pp'].tolist()
plac_colors = [RED] + [LBLUE] * len(plac_shuf)

bars9 = ax2.bar(range(len(plac_labels)), plac_stds, color=plac_colors, alpha=0.85)
ax2.set_xticks(range(len(plac_labels)))
ax2.set_xticklabels(plac_labels, fontsize=9)
ax2.set_ylabel('SD of CATE Distribution (pp)', fontsize=12)
ax2.set_title('(b) Placebo Test — Race Shuffle\n(real SD ≫ shuffled SD → genuine signal)', fontsize=12)
avg_shuf = plac_shuf['std_pp'].mean()
signal_ratio = plac_real['std_pp'] / avg_shuf
ax2.text(0.5, 0.95, f'Signal ratio: {signal_ratio:.0f}× (real / shuffled)',
         transform=ax2.transAxes, ha='center', va='top', fontsize=10, color=RED, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9))

fig.suptitle('Figure 8: Robustness — Findings Replicate Across Estimators and Pass Placebo Tests',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig8_robustness_placebo.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig8_robustness_placebo.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 9: Income × AUS Interaction Heatmap
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 9: Income × AUS heatmap...")

income_q = pd.qcut(df_small['income'].clip(10, 400), q=5, labels=['Q1\n<$60K','Q2\n$60-90K','Q3\n$90-125K','Q4\n$125-180K','Q5\n>$180K'])
df_small['income_q'] = income_q

aus_groups = [('Automated\nAUS', df_small['aus_automated'] == 1),
              ('Manual/\nExempt AUS', df_small['aus_automated'] == 0)]

income_labels = ['Q1\n<$60K','Q2\n$60-90K','Q3\n$90-125K','Q4\n$125-180K','Q5\n>$180K']
heatmap_data = np.zeros((2, 5))
sample_sizes = np.zeros((2, 5))

for i, (aus_label, aus_mask) in enumerate(aus_groups):
    for j, inc_label in enumerate(income_labels):
        inc_mask = df_small['income_q'] == inc_label
        sub = df_small[aus_mask & inc_mask]
        if len(sub) > 500:
            gap = (sub[sub['black'] == 0]['approved'].mean() -
                   sub[sub['black'] == 1]['approved'].mean()) * 100
            heatmap_data[i, j] = gap
            sample_sizes[i, j] = len(sub)

fig, ax = plt.subplots(figsize=(10, 4))
cmap = LinearSegmentedColormap.from_list('rwb', ['#1565C0', '#EEEEEE', '#C62828'])
im = ax.imshow(heatmap_data, cmap='RdYlBu_r', vmin=5, vmax=25, aspect='auto')
ax.set_xticks(range(5))
ax.set_xticklabels(income_labels, fontsize=10)
ax.set_yticks(range(2))
ax.set_yticklabels([g[0] for g in aus_groups], fontsize=10)
ax.set_xlabel('Applicant Income Quintile', fontsize=12)
ax.set_title('Figure 9: Racial Approval Gap by Income Quintile and Underwriting System\n(darker = larger gap; manual AUS gaps are systematically larger across all income levels)', fontsize=12)
for i in range(2):
    for j in range(5):
        ax.text(j, i, f'{heatmap_data[i,j]:.1f} pp\n(N={sample_sizes[i,j]/1000:.0f}K)',
                ha='center', va='center', fontsize=9,
                color='white' if heatmap_data[i,j] > 15 else 'black')
plt.colorbar(im, ax=ax, label='Racial Approval Gap (pp)', shrink=0.8)
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig9_income_aus_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig9_income_aus_heatmap.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 10: Sensitivity Analysis (Oster bounds, placeholder values)
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 10: Sensitivity analysis...")

# Using placeholder values (marked clearly)
r2_max_values = np.linspace(0.23, 0.50, 50)  # R²_max from current 0.22 to 2× 0.22
beta_c = -0.0939   # DML estimate (proxy for OLS controlled)
beta_unc = -0.1317  # uncontrolled (from DML base spec)
r2_c = 0.2155       # approximate from outcome model AUC²
r2_unc = 0.04       # bivariate R² (placeholder)

deltas = []
for r2_max in r2_max_values:
    if r2_max > r2_c and beta_unc != beta_c:
        delta = (beta_c * (r2_c - r2_unc)) / ((beta_unc - beta_c) * (r2_max - r2_c))
    else:
        delta = np.nan
    deltas.append(delta)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.plot(r2_max_values, deltas, color=BLUE, lw=2.5)
ax.axhline(1.0, color=RED, lw=2, linestyle='--', label='δ=1 (unobservables = observables)')
ax.axhline(0, color='black', lw=0.8)
ax.fill_between(r2_max_values, deltas, 1.0,
                where=[d < 1.0 if not np.isnan(d) else False for d in deltas],
                alpha=0.2, color=GREEN, label='δ>1 region (unobservables must dominate)')
ax.fill_between(r2_max_values, deltas, 1.0,
                where=[d > 1.0 if not np.isnan(d) else False for d in deltas],
                alpha=0.15, color=RED, label='δ<1 region (concern)')
ax.set_xlabel('Assumed R²_max (maximum R²)', fontsize=12)
ax.set_ylabel("Oster (2019) δ", fontsize=12)
ax.set_title('(a) Oster (2019) Sensitivity Bounds\n(δ > 1 → unobservables must dominate to nullify)', fontsize=12)
ax.legend(fontsize=9)
ax.set_ylim(-1, 8)
ax.text(0.97, 0.05, '[Note: β_uncontrolled, R²_uncontrolled\nare approximate — update from NB19 OLS]',
        transform=ax.transAxes, ha='right', fontsize=8, color='gray', style='italic')

ax2 = axes[1]
# Robustness value visualization
t_stats = [15.0, 12.0, 20.0, 8.5, 10.2]  # PLACEHOLDER
covar_names = ['AUS type', 'DTI ratio', 'AUS × year', 'LTV', 'Income']
partial_r2s = [(t**2) / (t**2 + 1_000_000) for t in t_stats]  # rough

ax2.barh(covar_names, partial_r2s, color=BLUE, alpha=0.8)
ax2.axvline(partial_r2s[0] * 0.5, color=RED, lw=2, linestyle='--',
             label='RV₀ threshold\n(min partial R² to nullify)')
ax2.set_xlabel('Partial R² (contribution to R²)', fontsize=12)
ax2.set_title('(b) Cinelli & Hazlett (2020)\nBenchmarking Confounders\n[PLACEHOLDER — run NB27 to update]', fontsize=12)
ax2.legend(fontsize=9)
ax2.text(0.97, 0.05, '[These are placeholder values —\nrun NB27 with actual OLS to update]',
         transform=ax2.transAxes, ha='right', fontsize=8, color='gray', style='italic',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

fig.suptitle('Figure 10: Sensitivity Analysis — Robustness to Omitted Variable Bias\n(Oster 2019 and Cinelli & Hazlett 2020 bounds)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig10_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig10_sensitivity_analysis.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 11: Geographic / Demographic Disparity Patterns
# ══════════════════════════════════════════════════════════════════════════════
print("Fig 11: Loan type and temporal patterns...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 11a: Purchase vs refi gap
ax = axes[0]
loan_groups = ['Purchase\nloans', 'Refinance\nloans']
loan_cates  = [-6.066, -9.702]
loan_colors = [BLUE, RED]
bars11 = ax.bar(loan_groups, loan_cates, color=loan_colors, alpha=0.85, width=0.5)
ax.axhline(-9.08, color=GRAY, lw=2, linestyle='--', label='Pooled mean')
ax.axhline(0, color='black', lw=0.8)
ax.set_ylabel('Mean CATE (pp)', fontsize=11)
ax.set_title('(a) CATE by Loan Purpose\n(Refinance > Purchase penalty)', fontsize=11)
ax.legend(fontsize=9)
for b, v in zip(bars11, loan_cates):
    ax.text(b.get_x() + b.get_width()/2, v + 0.2, f'{v:.2f} pp', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax.set_ylim(-13, 0.5)

# 11b: Small vs large lender
ax2 = axes[1]
lend_groups = ['Small\nlenders', 'Large\nlenders']
lend_cates  = [-10.554, -9.130]
bars12 = ax2.bar(lend_groups, lend_cates, color=[ORANGE, BLUE], alpha=0.85, width=0.5)
ax2.axhline(-9.08, color=GRAY, lw=2, linestyle='--', label='Pooled mean')
ax2.axhline(0, color='black', lw=0.8)
ax2.set_ylabel('Mean CATE (pp)', fontsize=11)
ax2.set_title('(b) CATE by Lender Size\n(small lenders show larger penalty)', fontsize=11)
ax2.legend(fontsize=9)
for b, v in zip(bars12, lend_cates):
    ax2.text(b.get_x() + b.get_width()/2, v + 0.2, f'{v:.2f} pp', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.set_ylim(-13, 0.5)

# 11c: Annual CATE trend
ax3 = axes[2]
yr_groups = ['Pre-2022', 'Post-2022']
yr_cates   = [-8.812, -9.408]
yr_pcts    = [89.8, 91.8]
bars13 = ax3.bar(yr_groups, yr_cates, color=[GREEN, RED], alpha=0.85, width=0.5)
ax3.axhline(-9.08, color=GRAY, lw=2, linestyle='--', label='Pooled mean')
ax3.axhline(0, color='black', lw=0.8)
ax3.set_ylabel('Mean CATE (pp)', fontsize=11)
ax3.set_title('(c) CATE Pre/Post Credit Tightening\n(penalty worsened post-2022)', fontsize=11)
ax3.legend(fontsize=9)
for b, v, pct in zip(bars13, yr_cates, yr_pcts):
    ax3.text(b.get_x() + b.get_width()/2, v + 0.2, f'{v:.2f} pp\n({pct:.1f}% penalised)',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax3.set_ylim(-12, 0.5)

fig.suptitle('Figure 11: Heterogeneity in the Racial Penalty by Loan Characteristics and Temporal Period',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(FIGS_DIR / 'fig11_loan_lender_temporal.png', dpi=300, bbox_inches='tight')
plt.close()
print("  Saved: fig11_loan_lender_temporal.png")

# ══════════════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ALL PUBLICATION FIGURES GENERATED")
print("=" * 60)
pub_figs = sorted(FIGS_DIR.glob('fig*.png'))
for f in pub_figs:
    size_kb = f.stat().st_size // 1024
    print(f"  {f.name}  ({size_kb} KB)")
print(f"\nTotal publication figures: {len(pub_figs)}")
