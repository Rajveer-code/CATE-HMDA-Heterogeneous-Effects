"""
generate_balance_table.py
=========================
Compute covariate balance between Black and White mortgage applicants
from the HMDA features panel. Outputs:
    outputs/tables/covariate_balance.csv

Columns: variable, black_mean, white_mean, std_diff, t_stat, p_value

Run once to populate Table 1 in the manuscript.
Usage:
    python scripts/generate_balance_table.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import polars as pl
from pathlib import Path
from scipy import stats

BASE_DIR    = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects')
DATA_DIR    = BASE_DIR / 'data'
TABLES_DIR  = BASE_DIR / 'outputs' / 'tables'
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# ── Variables to include in the balance table ────────────────────────────────
COVARIATE_LABELS = {
    'income':           'Applicant income ($000s)',
    'log_income':       'Log applicant income',
    'dti_midpoint':     'Debt-to-income ratio (%)',
    'ltv':              'Loan-to-value ratio (%)',
    'loan_amount_000s': 'Loan amount ($000s)',
    'purpose_purchase': 'Purchase loan (1=yes)',
    'property_value':   'Property value ($000s)',
    'aus_automated':    'Automated underwriting (1=yes)',
    'lender_size':      'Lender total originations (log)',
    'approved':         'Approval indicator (1=yes)',
    'year':             'Application year',
}

print("Loading features_panel.parquet via Polars lazy scan...")
lf = pl.scan_parquet(str(DATA_DIR / 'features_panel.parquet'))

# Sample up to 2M rows for speed
schema = lf.collect_schema()
print(f"Schema columns: {len(schema)}")

# Collect only the columns we need (plus 'black')
cols_needed = ['black'] + [c for c in COVARIATE_LABELS if c in schema.names()]
print(f"Columns to load: {cols_needed}")

df = lf.select(cols_needed).collect()
print(f"Loaded {len(df):,} rows")

df_pd = df.to_pandas()
black_mask = df_pd['black'] == 1
white_mask = df_pd['black'] == 0
n_black = int(black_mask.sum())
n_white = int(white_mask.sum())
print(f"Black applicants: {n_black:,}")
print(f"White applicants: {n_white:,}")

rows = []
print()
print("="*80)
print(f"{'Variable':<35} {'Black Mean':>12} {'White Mean':>12} {'Std.Diff':>10} {'p-value':>10}")
print("="*80)

for col, label in COVARIATE_LABELS.items():
    if col not in df_pd.columns:
        print(f"  {label:<33} -- column not found, skipping")
        continue

    b_vals = df_pd.loc[black_mask, col].dropna().values.astype(float)
    w_vals = df_pd.loc[white_mask, col].dropna().values.astype(float)

    if len(b_vals) == 0 or len(w_vals) == 0:
        continue

    b_mean = float(np.mean(b_vals))
    w_mean = float(np.mean(w_vals))
    b_std  = float(np.std(b_vals))
    w_std  = float(np.std(w_vals))

    # Standardized difference: (mean_B - mean_W) / pooled_SD
    pooled_sd = float(np.sqrt((b_std**2 + w_std**2) / 2))
    std_diff  = (b_mean - w_mean) / pooled_sd if pooled_sd > 1e-10 else 0.0

    # Welch t-test
    try:
        t_stat, p_val = stats.ttest_ind(b_vals, w_vals, equal_var=False)
    except Exception:
        t_stat, p_val = float('nan'), float('nan')

    print(f"  {label:<33} {b_mean:>12.4f} {w_mean:>12.4f} {std_diff:>10.4f} {p_val:>10.4e}")

    rows.append({
        'variable':   col,
        'label':      label,
        'black_mean': round(b_mean, 4),
        'white_mean': round(w_mean, 4),
        'std_diff':   round(std_diff, 4),
        't_stat':     round(float(t_stat), 3),
        'p_value':    float(p_val),
        'n_black':    int((~np.isnan(b_vals)).sum()),
        'n_white':    int((~np.isnan(w_vals)).sum()),
    })

balance_df = pd.DataFrame(rows)
out_path = TABLES_DIR / 'covariate_balance.csv'
balance_df.to_csv(out_path, index=False)
print()
print(f"Saved: {out_path}")
print(f"Rows  : {len(balance_df)}")
print()
print("Copy black_mean, white_mean, std_diff, p_value columns into Table 1 in the manuscript.")
