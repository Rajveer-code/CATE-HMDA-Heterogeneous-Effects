"""
Run OLS regressions on HMDA data to get actual values for NB27 sensitivity analysis.
Outputs:
  - beta_uncontrolled: bivariate OLS coef of Black on approved
  - r2_uncontrolled:   R² from bivariate regression
  - r2_controlled:     R² from full 33-feature OLS
  - t_stat_aus:        t-statistic for aus_automated in full OLS
  - Partial R² for key confounders
"""
import sys, warnings
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import polars as pl
import json
from pathlib import Path
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

BASE_DIR  = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects')
DATA_DIR  = BASE_DIR / 'data'

print("Loading sample (N=500,000) for OLS regressions...")
lf = pl.scan_parquet(str(DATA_DIR / 'features_panel.parquet'))

rng = np.random.default_rng(42)
df_full = lf.collect()
idx = rng.choice(len(df_full), size=500_000, replace=False)
df = df_full[idx].to_pandas()
print(f"Sample: {len(df):,} rows | Black share: {df['black'].mean():.3f}")

with open(DATA_DIR / 'feature_sets.json') as f:
    fs = json.load(f)
X_FULL = [c for c in fs['X_FULL'] if c in df.columns]
print(f"Features available: {len(X_FULL)}")

Y = df['approved'].values.astype(float)
D = df['black'].values.astype(float)

# ── 1. Bivariate OLS: Y ~ 1 + D ──────────────────────────────────────────────
print("\n" + "="*60)
print("1. BIVARIATE OLS: approved ~ black")
print("="*60)

X_uni = add_constant(D)
res_uni = OLS(Y, X_uni).fit(cov_type='HC3')
beta_uncontrolled = float(res_uni.params[1])
r2_uncontrolled   = float(res_uni.rsquared)
t_uni             = float(res_uni.tvalues[1])
se_uni            = float(res_uni.bse[1])

print(f"  beta (Black)  : {beta_uncontrolled:.6f}")
print(f"  SE            : {se_uni:.6f}")
print(f"  t-statistic   : {t_uni:.3f}")
print(f"  R²            : {r2_uncontrolled:.6f}")

# ── 2. Full OLS: Y ~ 1 + D + X ───────────────────────────────────────────────
print("\n" + "="*60)
print("2. FULL OLS: approved ~ black + X_FULL (33 features)")
print("="*60)

X_full = add_constant(pd.concat([pd.Series(D, name='black'), df[X_FULL]], axis=1))
res_full = OLS(Y, X_full).fit(cov_type='HC3')
beta_controlled   = float(res_full.params['black'])
r2_controlled     = float(res_full.rsquared)
t_controlled      = float(res_full.tvalues['black'])
se_controlled     = float(res_full.bse['black'])

print(f"  beta (Black)  : {beta_controlled:.6f}")
print(f"  SE            : {se_controlled:.6f}")
print(f"  t-statistic   : {t_controlled:.3f}")
print(f"  R²            : {r2_controlled:.6f}")
print(f"  N             : {len(Y):,}")

# ── 3. t-stat for AUS in full model ──────────────────────────────────────────
print("\n" + "="*60)
print("3. AUS coefficient in full model")
print("="*60)

aus_feature = 'aus_automated'
if aus_feature in res_full.params.index:
    t_stat_aus    = float(res_full.tvalues[aus_feature])
    beta_aus      = float(res_full.params[aus_feature])
    se_aus        = float(res_full.bse[aus_feature])
    print(f"  beta (AUS_auto): {beta_aus:.6f}")
    print(f"  SE             : {se_aus:.6f}")
    print(f"  t-statistic    : {t_stat_aus:.3f}")
else:
    t_stat_aus = 15.0
    print(f"  aus_automated not in model — using placeholder {t_stat_aus}")

# ── 4. Partial R² for key confounders ────────────────────────────────────────
print("\n" + "="*60)
print("4. PARTIAL R² FOR KEY CONFOUNDERS")
print("="*60)

# Partial R² for variable j = t_j^2 / (t_j^2 + df_resid)
df_resid = res_full.df_resid
partial_r2 = {}
benchmarks = ['dti_midpoint', 'ltv', 'log_income', 'purpose_purchase', 'lender_large',
               'aus_automated', 'income', 'log_loan_amount']
for col in benchmarks:
    if col in res_full.tvalues.index:
        t_val = float(res_full.tvalues[col])
        pr2   = t_val**2 / (t_val**2 + df_resid)
        partial_r2[col] = pr2
        print(f"  {col:<20}: t={t_val:+8.3f}  partial-R²={pr2:.8f}")
    else:
        print(f"  {col:<20}: NOT IN MODEL")

# ── 5. Oster delta ───────────────────────────────────────────────────────────
print("\n" + "="*60)
print("5. OSTER (2019) DELTA BOUNDS")
print("="*60)

# delta = beta_c * (R2_c - R2_u) / ((beta_u - beta_c) * (R2_max - R2_c))
# Where R2_max is typically set to 1.3 * R2_c (Oster's recommendation) or author's choice
R2_max_values = [1.3 * r2_controlled, 2.0 * r2_controlled, r2_controlled + 0.1, r2_controlled + 0.2]
for r2_max in R2_max_values:
    if r2_max > r2_controlled and beta_uncontrolled != beta_controlled:
        delta = (beta_controlled * (r2_controlled - r2_uncontrolled)) / \
                ((beta_uncontrolled - beta_controlled) * (r2_max - r2_controlled))
    else:
        delta = float('inf')
    print(f"  R²_max = {r2_max:.4f}  =>  delta = {delta:.4f}")

# ── 6. Save results ───────────────────────────────────────────────────────────
results = {
    'beta_uncontrolled': beta_uncontrolled,
    'r2_uncontrolled':   r2_uncontrolled,
    't_stat_uncontrolled': t_uni,
    'se_uncontrolled':   se_uni,
    'beta_controlled':   beta_controlled,
    'r2_controlled':     r2_controlled,
    't_stat_controlled': t_controlled,
    'se_controlled':     se_controlled,
    't_stat_aus':        t_stat_aus,
    'partial_r2':        partial_r2,
    'n_obs':             int(len(Y)),
    'df_resid':          int(df_resid),
}

import json as j
out_path = BASE_DIR / 'outputs' / 'tables' / 'ols_sensitivity_inputs.json'
with open(out_path, 'w') as f:
    j.dump(results, f, indent=2)
print(f"\nSaved: {out_path}")
print("\n" + "="*60)
print("OLS COMPLETE — copy these to NB27:")
print(f"  beta_uncontrolled = {beta_uncontrolled:.6f}")
print(f"  r2_uncontrolled   = {r2_uncontrolled:.6f}")
print(f"  beta_controlled   = {beta_controlled:.6f}")
print(f"  r2_controlled     = {r2_controlled:.6f}")
print(f"  t_stat_aus        = {t_stat_aus:.3f}")
print("="*60)
