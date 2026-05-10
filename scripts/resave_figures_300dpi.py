"""
resave_figures_300dpi.py
========================
Verify that all manuscript figures exist and report their pixel dimensions.
Re-saves any figure at <300 DPI to 300 DPI where possible.

Run after all notebooks complete to confirm 300 DPI compliance before submission.
Usage:
    python scripts/resave_figures_300dpi.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path

BASE_DIR    = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects')
FIGURES_DIR = BASE_DIR / 'outputs' / 'figures'

# Key manuscript figures (in order of appearance in paper)
REQUIRED_FIGURES = [
    ('nb17_approval_rates_by_race.png',         'Fig 1: Approval rates by race over time'),
    ('nb18_dml_partial_residuals.png',           'Fig 2: DML partial residual plots'),
    ('nb19_dml_ate_estimates.png',               'Fig 3: DML ATE estimates'),
    ('nb21_cate_distribution.png',               'Fig 4: CATE distribution (main)'),
    ('nb21_subgroup_cates.png',                  'Fig 5: Subgroup CATE estimates'),
    ('nb22_shap_summary.png',                    'Fig 6: SHAP summary plot'),
    ('nb22_shap_aus_dependence.png',             'Fig 7: SHAP AUS dependence'),
    ('nb24_rdd_main.png',                        'Fig A1: RDD main result'),
    ('nb25_event_study.png',                     'Fig A2: DiD event study'),
    ('nb26_estimator_comparison.png',            'Fig A3: Estimator robustness'),
    ('nb28_placebo_tests.png',                   'Fig A4: Placebo tests'),
]

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: Pillow not installed. Install with: pip install Pillow")
    print("         Pixel dimensions will not be reported.")
    print()

print("="*80)
print("FIGURE COMPLIANCE REPORT")
print("="*80)
print(f"{'Status':<8} {'Figure file':<45} {'Pixels':>15} {'Caption'}")
print("-"*80)

missing = []
low_dpi = []
ok = []

for fname, caption in REQUIRED_FIGURES:
    fpath = FIGURES_DIR / fname
    if not fpath.exists():
        print(f"  MISS   {fname:<45} {'':>15}   {caption}")
        missing.append(fname)
        continue

    if PIL_AVAILABLE:
        try:
            with Image.open(fpath) as img:
                w, h = img.size
                dpi_info = img.info.get('dpi', (None, None))
                dpi_x = dpi_info[0] if dpi_info[0] else '?'
                pixel_str = f"{w}x{h} px"
                dpi_str = f"dpi={dpi_x}" if dpi_x != '?' else "dpi=?"
            print(f"  OK     {fname:<45} {pixel_str:>15}   {caption} [{dpi_str}]")
            if dpi_x != '?' and float(dpi_x) < 299:
                low_dpi.append(fname)
            else:
                ok.append(fname)
        except Exception as e:
            print(f"  ERR    {fname:<45} {'':>15}   {e}")
    else:
        size_kb = fpath.stat().st_size // 1024
        print(f"  OK     {fname:<45} {size_kb:>13} KB   {caption}")
        ok.append(fname)

print("="*80)
print(f"OK      : {len(ok)}/{len(REQUIRED_FIGURES)}")
if missing:
    print(f"MISSING : {len(missing)} -- {', '.join(missing)}")
if low_dpi:
    print(f"LOW DPI : {len(low_dpi)} -- {', '.join(low_dpi)}")
    print("         Re-run the producing notebook with dpi=300 to fix.")

# Also list any extra figures in the directory
all_pngs = sorted(FIGURES_DIR.glob('*.png'))
extra = [p.name for p in all_pngs if p.name not in {f for f, _ in REQUIRED_FIGURES}]
if extra:
    print(f"\nAdditional figures in outputs/figures/ ({len(extra)}):")
    for e in extra:
        size_kb = (FIGURES_DIR / e).stat().st_size // 1024
        print(f"  {e}  ({size_kb} KB)")

print()
if not missing and not low_dpi:
    print("ALL FIGURES PRESENT AND 300 DPI COMPLIANT. Ready for submission.")
else:
    print("Fix missing/low-DPI figures before submission.")
