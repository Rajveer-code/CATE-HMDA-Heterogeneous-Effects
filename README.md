# Who Bears the Burden? Heterogeneous Racial Approval Differentials in U.S. Mortgage Lending

**Author:** Rajveer Singh Pall
**Institution:** Gyan Ganga Institute of Technology and Sciences
**Status:** Under review — Oxford Bulletin of Economics and Statistics

---

## Abstract

This paper estimates Conditional Average Treatment Effects (CATEs) of
Black racial identity on U.S. mortgage application approval using
42,296,010-observation HMDA data spanning 2020-2024. Using CausalForestDML
with LightGBM nuisance models, we find a mean approval penalty of -9.08
percentage points (pp), with substantial heterogeneity (SD = 8.47 pp).
SHAP attribution identifies automated underwriting system (AUS) type as
the strongest predictor of CATE variation (mean |SHAP| = 3.14 pp).
Results are validated against Double ML (ATE = -9.39 pp), an RDD at the
80% LTV threshold, and a Difference-in-Differences analysis of the 2022
Federal Reserve tightening.

---

## Repository Structure

```
CATE-HMDA-Heterogeneous-Effects/
|
+-- notebooks/
|   +-- NB17_feature_engineering.ipynb        # Feature construction from raw HMDA
|   +-- NB18_overlap_diagnostics.ipynb        # Propensity score and overlap checks
|   +-- NB19_double_ml_baseline.ipynb         # DML ATE estimation
|   +-- NB21_causal_forest_cate.ipynb         # Causal Forest CATE estimation
|   +-- NB22_shap_attribution.ipynb           # SHAP feature attribution
|   +-- NB23_disparity_map.ipynb              # Geographic disparity visualisation
|   +-- NB24_subgroup_rdd.ipynb               # RDD at 80% LTV threshold
|   +-- NB25_subgroup_did.ipynb               # DiD: 2022 tightening event study
|   +-- NB26_robustness_checks.ipynb          # Alternative estimators (DR-Learner, BART)
|   +-- NB27_sensitivity_analysis.ipynb       # Oster bounds, Cinelli-Hazlett robustness
|   +-- NB28_placebo_tests.ipynb              # Race shuffle + pseudo-treatment falsification
|
+-- outputs/
|   +-- figures/                              # All manuscript figures (PNG, 300 DPI)
|   +-- tables/                               # All manuscript tables (CSV)
|
+-- data/                                     # NOT tracked by git (see Data section)
|   +-- README_data.md                        # Data acquisition instructions
|
+-- manuscript/
|   +-- CATE_HMDA_Revised.docx               # Current manuscript version
|
+-- scripts/
|   +-- generate_balance_table.py             # Covariate balance table for Table 1
|   +-- resave_figures_300dpi.py              # Verify/report 300 DPI compliance
|   +-- final_verification.py                 # Pre-submission checklist
|
+-- environment.yml                           # Conda environment
+-- README.md
```

## Data

Data are from the Home Mortgage Disclosure Act (HMDA), publicly available
from the Consumer Financial Protection Bureau (CFPB):
https://ffiec.cfpb.gov/data-browser/

Download years 2020-2024. Place raw CSV files in `data/raw/` as:
- `data/hmda_2020.csv`
- `data/hmda_2021.csv`
- `data/hmda_2022.csv`
- `data/hmda_2023.csv`
- `data/hmda_2024.csv`

Then run notebooks in order: NB17 -> NB18 -> NB19 -> NB21 -> NB22 -> NB23 -> NB24 -> NB25 -> NB26 -> NB27 -> NB28.

## Execution Order

| Notebook | Purpose | Runtime | RAM Required |
|----------|---------|---------|-------------|
| NB17 | Feature engineering | ~30 min | 16 GB |
| NB18 | Overlap diagnostics | ~20 min | 16 GB |
| NB19 | DML baseline | ~40 min | 16 GB |
| NB21 | Causal Forest CATE | ~90 min | 16 GB |
| NB22 | SHAP attribution | ~25 min | 16 GB |
| NB23 | Disparity map | ~10 min | 8 GB |
| NB24 | Subgroup RDD | ~15 min | 8 GB |
| NB25 | Subgroup DiD | ~15 min | 8 GB |
| NB26 | Robustness checks | ~60 min | 16 GB |
| NB27 | Sensitivity analysis | ~10 min | 4 GB |
| NB28 | Placebo tests | ~30 min | 16 GB |

## Citation

If using this work, please cite:
> Pall, R.S. (2026). Who Bears the Burden? Heterogeneous Racial Approval
> Differentials in U.S. Mortgage Lending. Working paper.
