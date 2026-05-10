"""Execute NB28 cells directly as a Python script"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# === CELL 1 ===
import pandas as pd
import numpy as np
import polars as pl
import lightgbm as lgb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, gc, warnings
from pathlib import Path
from econml.dml import CausalForestDML

warnings.filterwarnings('ignore')

BASE_DIR    = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects')
DATA_DIR    = BASE_DIR / 'data'
TABLES_DIR  = BASE_DIR / 'outputs' / 'tables'
FIGURES_DIR = BASE_DIR / 'outputs' / 'figures'
TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({'figure.dpi': 150, 'font.family': 'serif', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})

with open(DATA_DIR / 'feature_sets.json') as f:
    fs = json.load(f)
X_FULL = fs['X_FULL']

print("NB28 - Placebo Tests: Race Shuffle and Pseudo-Treatment")
print(f"Features in X_FULL: {len(X_FULL)}")

# === CELL 2 ===
print('\nLoading sample (N=300K, seed=777)...')
N_BLACK_P = 60_000
N_WHITE_P = 240_000

lf = pl.scan_parquet(str(DATA_DIR / 'features_panel.parquet'))
df_black = lf.filter(pl.col('black') == 1).collect().sample(n=N_BLACK_P, seed=777)
df_white = lf.filter(pl.col('black') == 0).collect().sample(n=N_WHITE_P, seed=777)
df = pl.concat([df_black, df_white]).to_pandas()
del df_black, df_white
gc.collect()

X_use = [f for f in X_FULL if f in df.columns]
X_mat = df[X_use].values.astype(np.float32)
T_mat = df['black'].values.astype(np.float32)
Y_mat = df['approved'].values.astype(np.float32)

print(f'Sample N       : {len(df):,}')
print(f'Black share    : {T_mat.mean():.3f}')
print(f'Approval rate  : {Y_mat.mean():.3f}')
print(f'Features used  : {len(X_use)}')

def build_cf():
    m_t = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1,
                             num_leaves=31, n_jobs=-1, random_state=42, verbose=-1)
    m_y = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1,
                             num_leaves=31, n_jobs=-1, random_state=42, verbose=-1)
    return CausalForestDML(
        model_t=m_t, model_y=m_y,
        n_estimators=200, min_samples_leaf=50,
        max_depth=5, max_features=0.8,
        cv=3, random_state=42, n_jobs=-1
    )

# === CELL 3 ===
print("\n" + "="*70)
print("STEP 1: REAL CATE ESTIMATION")
print("="*70)

cf_real = build_cf()
cf_real.fit(Y_mat, T_mat, X=X_mat)
cate_real = cf_real.effect(X_mat)
real_mean = cate_real.mean() * 100
real_std  = cate_real.std()  * 100

print(f"Real CATE -- Mean: {real_mean:.3f} pp  SD: {real_std:.3f} pp")
print(f"Fraction penalised (CATE < 0): {100*(cate_real < 0).mean():.1f}%")

print()
print("="*70)
print("STEP 2: RACE SHUFFLE PLACEBO (3 permutations)")
print("="*70)
rng = np.random.default_rng(42)
shuffle_results = []
inc_col = None  # initialize

for perm_i in range(3):
    T_shuffled = T_mat.copy()
    rng.shuffle(T_shuffled)
    cf_sh = build_cf()
    cf_sh.fit(Y_mat, T_shuffled, X=X_mat)
    cate_sh = cf_sh.effect(X_mat)
    sh_mean = cate_sh.mean() * 100
    sh_std  = cate_sh.std()  * 100
    print(f"  Permutation {perm_i+1}: Mean={sh_mean:+.3f} pp  SD={sh_std:.3f} pp")
    shuffle_results.append({'permutation': perm_i+1, 'mean_pp': sh_mean, 'std_pp': sh_std})
    del cf_sh; gc.collect()

avg_shuffle_mean = np.mean([r['mean_pp'] for r in shuffle_results])
avg_shuffle_std  = np.mean([r['std_pp']  for r in shuffle_results])
print(f"\nAvg shuffled CATE -- Mean: {avg_shuffle_mean:+.3f} pp  SD: {avg_shuffle_std:.3f} pp")
print(f"Real SD / Avg Shuffled SD = {real_std / avg_shuffle_std:.2f}x")
if real_std > 2 * avg_shuffle_std:
    print("PASS: Real CATE heterogeneity >> shuffled baseline -- genuine signal.")
else:
    print("WARNING: Real SD not much larger than shuffled SD -- investigate.")

# === CELL 4 ===
print("="*70)
print("STEP 3: PSEUDO-TREATMENT PLACEBO (White applicants only)")
print("="*70)

white_mask = df['black'].values == 0
df_white_only = df[white_mask].copy()
X_white = X_mat[white_mask]
Y_white = Y_mat[white_mask]

if 'income' in df_white_only.columns:
    inc_col = 'income'
elif 'log_income' in df_white_only.columns:
    inc_col = 'log_income'
else:
    inc_col = None

pseudo_mean, pseudo_std = 0.0, 0.0
if inc_col is not None:
    q25 = np.nanpercentile(df_white_only[inc_col].values, 25)
    q75 = np.nanpercentile(df_white_only[inc_col].values, 75)
    q1_mask = df_white_only[inc_col].values <= q25
    q4_mask = df_white_only[inc_col].values >= q75
    pseudo_mask = q1_mask | q4_mask

    X_ps = X_white[pseudo_mask]
    Y_ps = Y_white[pseudo_mask]
    T_ps = (df_white_only[inc_col].values[pseudo_mask] >= q75).astype(np.float32)

    print(f"  Income col       : {inc_col}")
    print(f"  Q1 threshold     : {q25:.2f}")
    print(f"  Q4 threshold     : {q75:.2f}")
    print(f"  Pseudo-treatment N: {len(X_ps):,}")
    print(f"  Pseudo-T mean    : {T_ps.mean():.3f}")

    cf_pseudo = build_cf()
    cf_pseudo.fit(Y_ps, T_ps, X=X_ps)
    cate_pseudo = cf_pseudo.effect(X_ps)
    pseudo_mean = cate_pseudo.mean() * 100
    pseudo_std  = cate_pseudo.std()  * 100

    print(f"\nPseudo-treatment CATE -- Mean: {pseudo_mean:+.3f} pp  SD: {pseudo_std:.3f} pp")
    print(f"Real SD / Pseudo SD = {real_std / pseudo_std:.2f}x")
    del cf_pseudo; gc.collect()
else:
    print("  No income column found -- skipping pseudo-treatment placebo.")

# === CELL 5 ===
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
labels_left = ['Real CATEs\n(race-on-approval)'] + [f'Shuffled #{r["permutation"]}' for r in shuffle_results]
if inc_col is not None:
    labels_left.append('Pseudo-treatment\n(income Q4 vs Q1)')
means_left = [real_mean] + [r['mean_pp'] for r in shuffle_results]
if inc_col is not None:
    means_left.append(pseudo_mean)
colors_left = ['#1565C0'] + ['#BDBDBD'] * 3
if inc_col is not None:
    colors_left.append('#37474F')

ax.barh(range(len(labels_left)), means_left, color=colors_left, alpha=0.85)
ax.axvline(0, color='gray', linewidth=0.8)
ax.set_yticks(range(len(labels_left)))
ax.set_yticklabels(labels_left, fontsize=9)
ax.set_xlabel('Mean CATE (pp)', fontsize=10)
ax.set_title('Mean CATE: Real vs Placebo\n(shuffled CATEs should be near zero)', fontsize=10)
for i, v in enumerate(means_left):
    ax.text(v - 0.1, i, f'{v:+.2f}', va='center', ha='right', fontsize=8)

ax2 = axes[1]
labels_right = labels_left[:]
stds_right = [real_std] + [r['std_pp'] for r in shuffle_results]
if inc_col is not None:
    stds_right.append(pseudo_std)
colors_right = colors_left[:]

ax2.barh(range(len(labels_right)), stds_right, color=colors_right, alpha=0.85)
ax2.set_yticks(range(len(labels_right)))
ax2.set_yticklabels(labels_right, fontsize=9)
ax2.set_xlabel('SD of CATE distribution (pp)', fontsize=10)
ax2.set_title('CATE Heterogeneity: Real vs Placebo\n(real SD should >> shuffled SD)', fontsize=10)
for i, v in enumerate(stds_right):
    ax2.text(v + 0.05, i, f'{v:.2f}', va='center', fontsize=8)

plt.suptitle('Figure NB28: Placebo Tests -- Race Shuffle and Pseudo-Treatment', fontsize=11)
plt.tight_layout()
fig_path = FIGURES_DIR / 'nb28_placebo_tests.png'
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {fig_path.name}")

placebo_df = pd.DataFrame([
    {'test': 'Real CATE', 'type': 'real', 'mean_pp': real_mean, 'std_pp': real_std,
     'permutation': 0, 'note': 'Actual race-on-approval CATEs from CausalForestDML'},
] + [
    {'test': f'Race shuffle #{r["permutation"]}', 'type': 'race_shuffle',
     'mean_pp': r['mean_pp'], 'std_pp': r['std_pp'], 'permutation': r['permutation'],
     'note': 'Random permutation of race indicator'}
    for r in shuffle_results
] + ([
    {'test': 'Pseudo-treatment (income Q4 vs Q1)', 'type': 'pseudo_treatment',
     'mean_pp': pseudo_mean, 'std_pp': pseudo_std, 'permutation': 0,
     'note': 'White applicants only; pseudo-treatment = top income quartile'}
] if inc_col is not None else []))

placebo_df.to_csv(TABLES_DIR / 'nb28_placebo_results.csv', index=False)
print(f"Saved: nb28_placebo_results.csv")

print("\n" + "="*70)
print("NB28 SUMMARY")
print("="*70)
print(f"Real CATE SD       : {real_std:.3f} pp")
print(f"Avg shuffled SD    : {avg_shuffle_std:.3f} pp")
print(f"Signal ratio       : {real_std / avg_shuffle_std:.2f}x")
if inc_col is not None:
    print(f"Pseudo-treatment SD: {pseudo_std:.3f} pp")
print("\nNB28 complete.")
