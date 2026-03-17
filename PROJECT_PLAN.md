# Heterogeneous Treatment Effects in Mortgage Lending
## Research Project Plan and Technical Roadmap

**Author:** Rajveer Singh Pall  
**Institution:** Gyan Ganga Institute of Technology and Sciences, Jabalpur, India  
**Project start:** March 2026  
**Target completion:** August 2026  

---

## 1. Project Overview

This project extends my published paper — *Persistent Racial Disparities in U.S. Mortgage Approval: Evidence from 42 Million Applications, 2020–2024* (under review, JREFE) — by estimating Conditional Average Treatment Effects (CATE) using Causal Forests and Double Machine Learning.

The published paper reports one number: a Black applicant faces an average 10.6 percentage point lower approval rate within the same lending institution. That is a powerful finding, but it is incomplete. This project answers the next question: **for which types of Black applicants is the discrimination largest, and why?**

This distinction matters enormously for policy. Regulating "the mortgage market" broadly is a different intervention from targeting the 200 specific lenders or applicant subgroups where discrimination is most concentrated.

---

## 2. Research Questions

1. Is the average −10.6 pp penalty uniform across all Black applicants, or does it mask severe heterogeneity?
2. Is discrimination largest for high-income applicants (consistent with taste-based animus) or lower-income applicants (consistent with structural risk aversion)?
3. Is the 2.0 pp discontinuity at the 80% LTV threshold concentrated in specific applicant subgroups?
4. Did the 2022 Fed tightening cycle widen the gap uniformly, or did it amplify existing disparities for the most vulnerable applicants?
5. Which observable characteristics most strongly predict where the penalty is largest?

---

## 3. Companion Paper — What Already Exists

**Repository:** github.com/Rajveer-code/hmda-racial-disparities  
**Status:** Under review — Journal of Real Estate Finance and Economics

**Data:** HMDA public loan-level data, 2020–2024  
42,323,519 applications across 5,500+ lending institutions

**Key established findings:**
- Raw Black-White approval gap: **14.95 percentage points**
- After DFL reweighting: **98.6%** of gap unexplained by observable financial characteristics
- Within-lender fixed effects: **−10.6 pp** penalty, representing **74.6%** of total gap
- RDD at 80% LTV: **+2.0 pp** additional penalty at PMI boundary (purchase loans only)
- DiD post-2022 tightening: **+1.5 pp** widening in within-lender differential
- Manski lower bound: **9.89 pp** unexplained even under most conservative credit-quality assumptions
- State-level range: 3.6 pp (lowest) to 23.5 pp (highest)

**Stated limitation in conclusion:**  
*"Heterogeneous effects across applicant characteristics are unexplored."*  
This project directly closes that gap.

---

## 4. Methodology

### 4.1 Double Machine Learning (Chernozhukov et al., 2018)

DML handles the high-dimensional covariate set (33 features) by:
1. Residualising the treatment (Black indicator) on all covariates using LightGBM
2. Residualising the outcome (approval) on all covariates using LightGBM
3. Regressing outcome residuals on treatment residuals

This eliminates confounding from all observable characteristics and produces a clean Average Treatment Effect estimate. 5-fold cross-fitting eliminates regularisation bias. Standard errors are HC3-robust, clustered at the lender (LEI) level for robustness.

**Advantage over Repo 1's FE approach:** DML captures non-linear relationships between covariates and outcome that linear Frisch-Waugh-Lovell demeaning misses — income squared effects, income × LTV interactions, etc.

### 4.2 Causal Forests (Wager & Athey, 2018)

Causal Forests grow trees that split on covariates to maximise heterogeneity in treatment effects — not prediction accuracy. Key properties:
- **Honest splitting:** the data used to determine splits is separate from the data used to estimate effects within leaves — prevents overfitting
- **500 trees:** standard in the literature, provides stable CATE estimates
- **Inference:** confidence intervals via bootstrap of little bags
- **Implementation:** econml's CausalForestDML with LightGBM nuisance models

Output: a CATE estimate for every individual applicant in the dataset.

### 4.3 SHAP Attribution (Lundberg & Lee, 2017)

SHAP (SHapley Additive exPlanations) decomposes each applicant's CATE estimate into contributions from individual features. This answers: which covariates drive heterogeneity in the treatment effect? Is it primarily income? LTV? Automated underwriting system? Lender size?

### 4.4 Identification

All causal identification rests on the same selection-on-observables assumption as the DML estimator: conditional on the 33 observed covariates, treatment assignment (race) is as-good-as-random. The overlap assumption is verified empirically in NB18 (propensity score AUC = 0.729, 98% common support). The CATE estimates are valid within the common support region.

---

## 5. Data and Feature Engineering

### 5.1 Core data
Same HMDA dataset as Repo 1: 42.3M applications, 2020–2024.

### 5.2 New variables added (not in Repo 1)

| Variable | HMDA field | Why it matters |
|----------|-----------|----------------|
| Debt-to-income ratio | `debt_to_income_ratio` | Directly addresses Repo 1's missing-controls critique |
| Automated underwriting system | `aus_1` | Tests Bartlett et al. (2022) algorithmic vs human discretion channel |
| Applicant age | `applicant_age` | Tests age × race interaction |
| Construction method | `construction_method` | Site-built vs manufactured underwriting differences |
| Neighbourhood minority % | `tract_minority_population_percent` | Geographic discrimination mechanism |

### 5.3 Feature engineering decisions

- **DTI encoding:** HMDA reports DTI as string ranges ("30%-<36%") and raw integers (legacy lenders). Both formats parsed to numeric midpoints. The 43% QM (Qualified Mortgage) threshold is a regulatory cutpoint and is encoded as a binary flag.
- **AUS encoding:** Codes 1-4 (DU, LPA, TOTAL, GUS) = automated. Code 6 and 1111 = exempt/manual. The exempt category identifies lenders making decisions through pure human discretion.
- **Lender size tiers:** Derived from total application volume — small (<500), mid (500-5000), large (>5000).
- **Log transforms:** log(income), log(loan_amount), log(property_value) to handle right skew.

### 5.4 Final feature matrix
- **Rows:** 42,296,010 (after LTV filter removing implausible values)
- **Features in X_FULL:** 33
- **DTI coverage:** 98.2%
- **Missing values:** 0 in all key columns

---

## 6. Notebook Pipeline

### Completed

| Notebook | Purpose | Status | Key result |
|----------|---------|--------|------------|
| NB17 | Feature engineering | ✅ Done | 42.3M rows, 33 features, 0 missing |
| NB18 | Overlap diagnostics | ✅ Done | AUC=0.729, 98% common support |
| NB19 | Double ML baseline | ✅ Done | ATE=−9.39 pp, p<0.001 |
| NB21 | Causal Forest CATE | ⏳ Running | 500 trees, 1.5M sample |

### Remaining

| Notebook | Purpose | Estimated runtime | Key output |
|----------|---------|------------------|------------|
| NB22 | SHAP attribution | 15-20 min | Which features drive heterogeneity |
| NB23 | Disparity map | 10 min | Income × LTV × lender heatmap |
| NB24 | Subgroup RDD | 20-30 min | PMI boundary effect by subgroup |
| NB25 | Subgroup DiD | 20-30 min | Tightening effect by CATE quartile |
| NB26 | Paper figures | 15 min | All publication-ready figures |

---

## 7. Key Results So Far

### NB18 — Overlap
- Propensity model AUC: **0.7291** — moderate separability, substantial common support
- Common support: **98.0%** of sample — CATE estimates valid for nearly full population
- Approval gap within common support: **15.02 pp** — larger than raw gap, confirming financials do not explain disparity
- Trim bounds: [0.0328, 0.5801] — applied consistently in all downstream notebooks

### NB19 — Double ML
- DML ATE (33 controls, X_FULL): **−9.39 pp** (SE = 0.07 pp, p < 0.001)
- DML ATE (4 controls, X_BASE, matching Repo 1): **−13.17 pp**
- Gap explained by DTI + AUS + age: **3.79 pp**
- Gap remaining unexplained: **9.39 pp (62.8%** of raw gap)
- Sanity check vs Repo 1: difference = **1.21 pp** ✅ pipeline validated
- Year-by-year: negative in all 5 years, −10.04 pp (2020) to −8.86 pp (2024)
- Outcome model AUC: 0.817 — financials predict approval well, yet gap survives

**Scientific interpretation of X_BASE vs X_FULL:**  
The 3.79 pp difference between the two specifications is itself a finding. DTI, automated underwriting system type, and applicant age together explain 3.79 pp of the racial gap — but 9.39 pp survives even after conditioning on all of these. This directly and empirically rebuts the missing-controls critique of the published paper.

---

## 8. Expected Findings and Paper Narrative

### The CATE distribution (NB21)
We expect the CATE distribution to be wide — a standard deviation above 1 pp would indicate that the average of −9.39 pp masks substantial individual-level heterogeneity. This is the central empirical contribution: showing that the average treatment effect is not representative of the typical applicant's experience.

### The income gradient (NB21 subgroups)
The income quintile breakdown will answer whether discrimination is consistent with taste-based animus or statistical discrimination:
- If high-income (Q5) CATE is more negative than low-income (Q1): consistent with animus — applicants most financially comparable to White applicants face the largest penalty
- If low-income (Q1) CATE is more negative: consistent with structural risk aversion

### The AUS mechanism (NB21 + NB22)
If applicants whose lenders use automated underwriting face smaller CATE than those with manual/exempt underwriting, this directly replicates and extends Bartlett et al. (2022) in a causal framework — the first CATE-level test of the algorithmic discrimination channel.

### Subgroup quasi-experimental validation (NB24, NB25)
Re-examining the RDD and DiD from Repo 1 through the lens of CATE quartiles:
- Does the 2.0 pp PMI boundary effect concentrate in the highest-CATE quartile (most-penalised applicants)?
- Did the 2022 tightening cycle amplify disparities for already-vulnerable applicants or did it affect everyone equally?

---

## 9. Five-Month Timeline

### Month 1 — Analysis (March–April 2026)
Complete NB21 through NB26. One notebook per day.
Each notebook: run analysis, interpret output, commit, write LinkedIn post.

### Month 2 — Paper writing (April–May 2026)
Write full manuscript. Sections:
- Introduction: from average effect to heterogeneous effects
- Theoretical framework: Becker taste-based vs Phelps statistical discrimination, differential discretion
- Data: HMDA 2020–2024, feature engineering, overlap verification
- Methodology: DML framework, Causal Forest, SHAP attribution
- Results: ATE replication, CATE distribution, subgroup analysis, SHAP drivers, subgroup quasi-experimental validation
- Discussion: policy implications, targeted regulatory oversight
- Conclusion

Upload to arXiv. Submit to FAccT 2026 or JASA Applications track.

### Month 3 — Project 2 (May–June 2026)
**Topic:** Lender-level heterogeneity — which institutions drive the racial approval gap?

**Research questions:**
- Which lenders have the largest within-institution racial gaps?
- Are they large national banks or small community lenders?
- Are they concentrated in specific states or markets?
- Is lender market concentration (HHI) associated with larger gaps?
- Are individual lenders improving or worsening over time?

**Why this is a natural extension:**
Repo 1 decomposes the gap into within vs between-lender components.
Project 1 maps CATE across applicant characteristics.
Project 2 maps the gap across the institutional landscape.
Together the three papers form a complete picture: how large is the gap, who bears it most, and which institutions are responsible.

**Estimated scope:** 4-5 notebooks, 1 SSRN working paper

### Months 4-5 — Polish and applications (June–August 2026)
- Build interactive disparity map web tool (Plotly Dash, hosted on GitHub Pages)
- This tool visualises CATE estimates by income/LTV/lender interactively
- Linked on GitHub profile — allows non-specialists to explore the research
- Write tailored SOPs for ETH Zurich, Cambridge, Oxford
- Submit applications (deadlines typically December 2026 – January 2027)

---

## 10. Publication Targets

| Output | Target venue | Timeline |
|--------|-------------|----------|
| arXiv preprint (Project 1) | arXiv cs.LG / econ.GN | End of Month 2 |
| Conference paper | FAccT 2026 (ACM) | May 2026 submission |
| Journal paper | JASA Applications & Case Studies | Month 3 |
| SSRN working paper (Project 2) | SSRN | Month 3 |
| Interactive web tool | GitHub Pages | Month 4 |

---

## 11. Technical Stack

| Component | Tool |
|-----------|------|
| Causal Forest | econml CausalForestDML |
| Double ML | econml LinearDML, CausalForestDML |
| Nuisance models | LightGBM (via sklearn pipeline) |
| SHAP attribution | shap TreeExplainer |
| Fast CSV reading | Polars (Rust-based, multi-threaded) |
| Data pipeline | Pandas, PyArrow, Parquet |
| Visualisation | Matplotlib, Seaborn, Plotly |
| Statistical tests | SciPy, Statsmodels |
| Parallel compute | n_jobs=-1 (all 14 CPU cores) |

---

## 12. Repository Structure

```
CATE-HMDA-Heterogeneous-Effects/
├── README.md
├── PROJECT_PLAN.md          (this file)
├── environment.yml
├── requirements.txt
├── .gitignore
│
├── notebooks/
│   ├── NB17_feature_engineering.ipynb
│   ├── NB18_overlap_diagnostics.ipynb
│   ├── NB19_double_ml_baseline.ipynb
│   ├── NB21_causal_forest_cate.ipynb
│   ├── NB22_shap_attribution.ipynb
│   ├── NB23_disparity_map.ipynb
│   ├── NB24_subgroup_rdd.ipynb
│   ├── NB25_subgroup_did.ipynb
│   └── NB26_paper_figures.ipynb
│
├── data/
│   ├── README.md            (data download instructions)
│   ├── feature_sets.json    (X_FULL, X_BASE, X_HETERO definitions)
│   ├── trim_bounds.json     (NB18 overlap trim parameters)
│   └── processed/           (panel CSVs from Repo 1 — not committed)
│
├── outputs/
│   ├── tables/              (CSV results tables)
│   └── figures/             (PNG figures)
│
└── paper/
    └── CATE_HMDA_draft.tex
```

---

## 13. References

- Wager, S., & Athey, S. (2018). Estimation and inference of heterogeneous treatment effects using random forests. *JASA*, 113(523), 1228–1242.
- Chernozhukov, V. et al. (2018). Double/debiased machine learning. *Econometrics Journal*, 21(1), C1–C68.
- Bartlett, R., Morse, A., Stanton, R., & Wallace, N. (2022). Consumer-lending discrimination in the FinTech era. *Journal of Financial Economics*, 143(1), 30–56.
- Bhutta, N., Hizmo, A., & Ringo, D. (2025). How much does racial bias affect mortgage lending? *Journal of Finance*, 80(2).
- Bhutta, N., & Hizmo, A. (2021). Do minorities pay more for mortgages? *Review of Financial Studies*, 34(2), 763–789.
- Lundberg, S., & Lee, S. (2017). A unified approach to interpreting model predictions. *NeurIPS*, 30.
- Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. *Review of Economic Studies*, 90(5), 2555–2591.
- Munnell, A. et al. (1996). Mortgage lending in Boston: Interpreting HMDA data. *American Economic Review*, 86(1), 25–53.
- DiNardo, J., Fortin, N., & Lemieux, T. (1996). Labour market institutions and the distribution of wages. *Econometrica*, 64(5), 1001–1044.
- Calonico, S., Cattaneo, M., & Titiunik, R. (2014). Robust nonparametric confidence intervals for RDD. *Econometrica*, 82(6), 2295–2326.
- Becker, G. (1957). *The Economics of Discrimination*. University of Chicago Press.
- Phelps, E. (1972). The statistical theory of racism and sexism. *American Economic Review*, 62(4), 659–661.
