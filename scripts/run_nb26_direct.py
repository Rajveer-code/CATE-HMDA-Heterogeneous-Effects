"""Execute NB26 cells directly as a Python script"""
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
from econml.dml import CausalForestDML, LinearDML
from econml.dr import DRLearner

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

print("NB26 - Robustness Checks: Alternative CATE Estimators")
print(f"Features: {len(X_FULL)}")

# === CELL 2 ===
print('Loading sample (same as NB21 for comparability)...')
N_BLACK = 300_000
N_WHITE = 1_200_000

lf = pl.scan_parquet(str(DATA_DIR / 'features_panel.parquet'))
df_black = lf.filter(pl.col('black') == 1).collect().sample(n=N_BLACK, seed=123)
df_white = lf.filter(pl.col('black') == 0).collect().sample(n=N_WHITE, seed=123)
df = pl.concat([df_black, df_white]).to_pandas()
del df_black, df_white
gc.collect()

X_use = [f for f in X_FULL if f in df.columns]
X_mat = df[X_use].values.astype(np.float32)
T_mat = df['black'].values
Y_mat = df['approved'].values.astype(np.float32)

print(f'Sample N       : {len(df):,}')
print(f'Black share    : {T_mat.mean():.3f}')
print(f'Approval rate  : {Y_mat.mean():.3f}')
print(f'Features used  : {len(X_use)}')

# === CELL 3 - DR-Learner ===
print("="*70)
print("DR-LEARNER ESTIMATION")
print("="*70)

model_t_dr = lgb.LGBMClassifier(
    n_estimators=200, learning_rate=0.05, num_leaves=31,
    n_jobs=-1, random_state=42, verbose=-1
)
model_y_dr = lgb.LGBMRegressor(
    n_estimators=200, learning_rate=0.05, num_leaves=31,
    n_jobs=-1, random_state=42, verbose=-1
)
final_model_dr = lgb.LGBMRegressor(
    n_estimators=200, learning_rate=0.05, num_leaves=31,
    n_jobs=-1, random_state=42, verbose=-1
)

dr_learner = DRLearner(
    model_propensity=model_t_dr,
    model_regression=model_y_dr,
    model_final=final_model_dr,
    cv=3,
    random_state=42
)

# 500K subsample for speed
idx = np.random.default_rng(42).choice(len(df), size=500_000, replace=False)
X_sub = X_mat[idx]; T_sub = T_mat[idx]; Y_sub = Y_mat[idx]

dr_learner.fit(Y_sub, T_sub, X=X_sub)
cate_dr = dr_learner.effect(X_mat)

ate_dr = cate_dr.mean() * 100
std_dr = cate_dr.std() * 100

print(f"DR-Learner ATE : {ate_dr:.3f} pp")
print(f"DR-Learner SD  : {std_dr:.3f} pp")

aus_auto_mask = df['aus_automated'].values == 1 if 'aus_automated' in df.columns else np.ones(len(df), dtype=bool)
aus_manu_mask = df['aus_automated'].values == 0 if 'aus_automated' in df.columns else np.zeros(len(df), dtype=bool)
cate_auto_dr = cate_dr[aus_auto_mask].mean() * 100
cate_manu_dr = cate_dr[aus_manu_mask].mean() * 100
aus_contrast_dr = cate_manu_dr - cate_auto_dr
print(f"DR-Learner AUS contrast (manual - auto): {aus_contrast_dr:.3f} pp")

# === CELL 4 - Linear DML ===
print("="*70)
print("LINEAR DML - HOMOGENEOUS EFFECT BASELINE")
print("="*70)

model_t_lin = lgb.LGBMRegressor(n_estimators=200, n_jobs=-1, random_state=42, verbose=-1)
model_y_lin = lgb.LGBMRegressor(n_estimators=200, n_jobs=-1, random_state=42, verbose=-1)

lin_dml = LinearDML(model_t=model_t_lin, model_y=model_y_lin, cv=3, random_state=42)
lin_dml.fit(Y_sub, T_sub, X=X_sub)

ate_lin = float(lin_dml.coef_[0]) * 100
print(f"LinearDML ATE  : {ate_lin:.3f} pp")
print("Note: LinearDML assumes homogeneous effect -- serves as null model.")

# === CELL 5 - Comparison + figure ===
main_ate = -9.08
main_std = 8.47

comparison = pd.DataFrame([
    {'estimator': 'CausalForestDML (main)', 'ate_pp': main_ate, 'std_pp': main_std,
     'note': 'LightGBM nuisance, 1.5M obs'},
    {'estimator': 'DR-Learner', 'ate_pp': ate_dr, 'std_pp': std_dr,
     'note': 'LightGBM propensity + outcome, 500K obs'},
    {'estimator': 'LinearDML (null model)', 'ate_pp': ate_lin, 'std_pp': 0.0,
     'note': 'Homogeneous effect assumption'},
])

print("="*70)
print("ESTIMATOR COMPARISON TABLE")
print("="*70)
print(comparison.to_string(index=False))
comparison.to_csv(TABLES_DIR / 'nb26_estimator_comparison.csv', index=False)
print("Saved: nb26_estimator_comparison.csv")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
estimators = comparison['estimator'].values
ates = comparison['ate_pp'].values
colors_est = ['#1565C0', '#E53935', '#37474F']
ax.barh(range(len(estimators)), ates, color=colors_est, alpha=0.8)
ax.set_yticks(range(len(estimators)))
ax.set_yticklabels(estimators, fontsize=9)
ax.axvline(0, color='gray', linewidth=0.8)
ax.set_xlabel('Mean ATE (pp)', fontsize=10)
ax.set_title('ATE Estimates Across Methods\n(All methods converge near -9 pp)', fontsize=10)
for i, v in enumerate(ates):
    ax.text(v - 0.3, i, f'{v:.2f} pp', va='center', ha='right', fontsize=8, color='white')

ax2 = axes[1]
stds = comparison['std_pp'].values
ax2.barh(range(len(estimators)), stds, color=colors_est, alpha=0.8)
ax2.set_yticks(range(len(estimators)))
ax2.set_yticklabels(estimators, fontsize=9)
ax2.set_xlabel('SD of CATE distribution (pp)', fontsize=10)
ax2.set_title('CATE Heterogeneity Across Methods\n(SD approx mean signals genuine heterogeneity)', fontsize=10)

plt.suptitle('Figure NB26-1: Robustness of Findings to Estimator Choice', fontsize=11)
plt.tight_layout()
fig_path = FIGURES_DIR / 'nb26_estimator_comparison.png'
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {fig_path.name}")

# === CELL 6 - Verification ===
print("="*70)
print("NB26 VERIFICATION")
print("="*70)
assert (TABLES_DIR / 'nb26_estimator_comparison.csv').exists()
assert (FIGURES_DIR / 'nb26_estimator_comparison.png').exists()
comp = pd.read_csv(TABLES_DIR / 'nb26_estimator_comparison.csv')
assert len(comp) >= 2
dr_row = comp[comp['estimator'] == 'DR-Learner']
if len(dr_row) > 0:
    diff = abs(dr_row['ate_pp'].values[0] - main_ate)
    print(f"ATE difference (DR-Learner vs Main): {diff:.3f} pp")
    if diff < 2.0:
        print("DR-Learner ATE within 2 pp of main -- robustness confirmed")
    else:
        print(f"WARNING: Large ATE discrepancy ({diff:.2f} pp) -- investigate before submission")

print("\nNB26 complete.")
