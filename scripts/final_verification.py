"""
final_verification.py
=====================
Pre-submission checklist for the CATE-HMDA paper.
Runs ~25 existence checks across manuscript, tables, figures, notebooks, and
repo structure files. Prints checkmark/cross per item and a final pass/fail count.

Usage:
    python scripts/final_verification.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path

BASE_DIR = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects')
PASS = "[OK]  "
FAIL = "[MISS]"

checks = []

def check(label, path_or_bool, warning=None):
    """Record a check result."""
    if isinstance(path_or_bool, (str, Path)):
        result = Path(path_or_bool).exists()
    else:
        result = bool(path_or_bool)
    checks.append((result, label, warning))
    status = PASS if result else FAIL
    warn = f"  <-- {warning}" if (not result and warning) else ""
    print(f"  {status}  {label}{warn}")

# ── 1. Manuscript ─────────────────────────────────────────────────────────────
print()
print("="*70)
print("1. MANUSCRIPT")
print("="*70)
check("manuscript/CATE_HMDA_Revised.docx exists",
      BASE_DIR / 'manuscript' / 'CATE_HMDA_Revised.docx',
      "Copy from Downloads and rename")

# ── 2. Data files ─────────────────────────────────────────────────────────────
print()
print("="*70)
print("2. DATA FILES")
print("="*70)
check("data/features_panel.parquet",   BASE_DIR / 'data' / 'features_panel.parquet')
check("data/cate_estimates.parquet",   BASE_DIR / 'data' / 'cate_estimates.parquet')
check("data/feature_sets.json",        BASE_DIR / 'data' / 'feature_sets.json')
check("data/README_data.md",           BASE_DIR / 'data' / 'README_data.md')

# ── 3. Output tables (CSVs) ────────────────────────────────────────────────────
print()
print("="*70)
print("3. OUTPUT TABLES (required for manuscript)")
print("="*70)
tables = [
    ('nb19_annual_ate.csv',          'Annual DML estimates (Table 4k)'),
    ('nb21_subgroup_cates.csv',      'Subgroup CATEs (Table 3)'),
    ('nb24_mccrary_test.csv',        'McCrary density test (Sec 3.4)'),
    ('nb24_bandwidth_sensitivity.csv', 'RDD bandwidth sensitivity (Sec 3.4)'),
    ('nb24_placebo_thresholds.csv',  'RDD placebo thresholds (Sec 3.4)'),
    ('nb24_covariate_continuity.csv','RDD covariate continuity (Sec 3.4)'),
    ('nb25_pretrend_test.csv',       'DiD pre-trend test (Sec 4.2)'),
    ('nb26_estimator_comparison.csv','Estimator comparison (Sec 4.5)'),
    ('nb28_placebo_results.csv',     'Placebo test results (Sec 4.5)'),
    ('covariate_balance.csv',        'Covariate balance (Table 1)'),
]
for fname, note in tables:
    check(f"{fname}  ({note})", BASE_DIR / 'outputs' / 'tables' / fname)

# NB27 CSV is intentionally absent (needs real NB19 OLS values first)
nb27_csv = BASE_DIR / 'outputs' / 'tables' / 'nb27_sensitivity_analysis.csv'
print(f"  [INFO]  nb27_sensitivity_analysis.csv -- {'present' if nb27_csv.exists() else 'absent (expected: fill placeholders first)'}")

# ── 4. Output figures (PNGs) ───────────────────────────────────────────────────
print()
print("="*70)
print("4. OUTPUT FIGURES")
print("="*70)
figures = [
    'nb21_cate_distribution.png',
    'nb21_subgroup_cates.png',
    'nb22_shap_summary.png',
    'nb22_shap_aus_dependence.png',
    'nb24_rdd_main.png',
    'nb24_mccrary_density_test.png',
    'nb25_event_study.png',
    'nb26_estimator_comparison.png',
    'nb28_placebo_tests.png',
]
for fname in figures:
    check(fname, BASE_DIR / 'outputs' / 'figures' / fname)

# ── 5. Notebooks ──────────────────────────────────────────────────────────────
print()
print("="*70)
print("5. NOTEBOOKS (NB17-NB28)")
print("="*70)
for nb_num in range(17, 29):
    nb_files = list((BASE_DIR / 'notebooks').glob(f'NB{nb_num}_*.ipynb'))
    if nb_files:
        check(f"NB{nb_num}: {nb_files[0].name}", nb_files[0])
    else:
        check(f"NB{nb_num}: [not found]", False, "Create or rename notebook")

# ── 6. Repo files ─────────────────────────────────────────────────────────────
print()
print("="*70)
print("6. REPO STRUCTURE FILES")
print("="*70)
check(".gitignore",       BASE_DIR / '.gitignore')
check("environment.yml", BASE_DIR / 'environment.yml')
check("README.md",       BASE_DIR / 'README.md')
check("scripts/generate_balance_table.py",   BASE_DIR / 'scripts' / 'generate_balance_table.py')
check("scripts/resave_figures_300dpi.py",    BASE_DIR / 'scripts' / 'resave_figures_300dpi.py')
check("scripts/final_verification.py",       BASE_DIR / 'scripts' / 'final_verification.py')

# ── Summary ───────────────────────────────────────────────────────────────────
n_pass = sum(1 for ok, _, _ in checks if ok)
n_fail = sum(1 for ok, _, _ in checks if not ok)
n_total = len(checks)

print()
print("="*70)
print("SUMMARY")
print("="*70)
print(f"  PASS : {n_pass}/{n_total}")
print(f"  FAIL : {n_fail}/{n_total}")
print()

if n_fail == 0:
    print("ALL CHECKS PASSED. Repository is submission-ready.")
else:
    print(f"{n_fail} items need attention before submission:")
    for ok, label, warning in checks:
        if not ok:
            w = f" -- {warning}" if warning else ""
            print(f"  - {label}{w}")

# ── NB27 placeholder reminder ─────────────────────────────────────────────────
print()
print("REMINDER: NB27_sensitivity_analysis.ipynb contains PLACEHOLDER values.")
print("  Before submission, run NB19 with OLS output, then update:")
print("  - beta_uncontrolled (Cell 1)")
print("  - r2_uncontrolled   (Cell 1)")
print("  - r2_controlled     (Cell 1)")
print("  - t_stat_aus        (Cell 2)")
print("  - benchmark partial R2 values (Cell 2)")
print("  Then re-run NB27 to generate the final sensitivity figures and Table.")
