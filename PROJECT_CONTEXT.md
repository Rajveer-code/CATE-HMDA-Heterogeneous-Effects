# PROJECT CONTEXT — CATE-HMDA Research Program
# Rajveer Singh Pall | MSc Applications 2027
# Last updated: March 2026
#
# PASTE THIS ENTIRE FILE AT THE START OF ANY NEW CLAUDE SESSION.
# Say: "I am Rajveer. Continue helping me with my research project.
#       Here is the full context:" then paste this file.
# Claude will have everything it needs immediately.

---

## WHO I AM

**Name:** Rajveer Singh Pall
**Degree:** B.Tech Computer Science & Business Systems
**Institution:** Gyan Ganga Institute of Technology and Sciences, Jabalpur, Madhya Pradesh, India
**Goal:** MSc Data Science 2027 — ETH Zurich (primary), University of Cambridge, University of Oxford
**GitHub:** github.com/Rajveer-code
**Email:** rajveerpall04@gmail.com (linked to GitHub Rajveer-code account)
**LinkedIn:** linkedin.com/in/rajveer-singh-pall

**Hardware:** i7-13650HX (14 cores), RTX 4060 (8GB VRAM), 16GB RAM
**OS:** Windows 11, VS Code, Git Bash
**Project drive:** D: drive (265GB free)
**Conda environment:** cate_hmda (Python 3.11)
**Key libraries:** econml, lightgbm, shap, polars, pandas, numpy, scipy, matplotlib, pyarrow

---

## THE RESEARCH PROGRAM — FULL PICTURE

This is a two-paper research program built from the same HMDA dataset.
Both papers are authored by Rajveer Singh Pall alone.

### PAPER 1 (EXISTING — SUBMITTED)
**Title:** Persistent Racial Disparities in U.S. Mortgage Approval: Evidence from 42 Million Applications, 2020–2024
**Repository:** github.com/Rajveer-code/hmda-racial-disparities
**Status:** Under review — Journal of Real Estate Finance and Economics (JREFE)
**Dataset:** HMDA public loan-level data, 2020–2024, 42,323,519 applications, 5,500+ lenders

**Key findings:**
- Raw Black-White approval gap: 14.95 percentage points
- After DFL reweighting: 98.6% of gap unexplained by observable financial characteristics
- Within-lender FE (NB04): -10.6 pp penalty — 74.6% of gap is within-lender (not sorting)
- RDD at 80% LTV threshold: additional 2.0 pp penalty at PMI boundary, purchase loans only
- DiD (2022 Fed tightening): gap widened by 1.5 pp post-2022
- Triple difference: two channels are structurally independent (p=0.003)
- Credit score bounds: at least 9.89 pp unexplained even under most conservative assumptions
- Geographic range: state-level gaps from 3.6 pp to 23.5 pp
- Permutation inference: no permuted sample produced estimates as extreme

**16 notebooks:**
- NB01: Data cleaning (race codes: Black=3, White=5)
- NB02: Descriptive statistics
- NB03: DFL decomposition
- NB04: Within-lender fixed effects (Frisch-Waugh-Lovell)
- NB05: Robustness checks
- NB06: Regional analysis
- NB07: Credit score sensitivity (Manski bounds)
- NB08: Figure generation
- NB09: LTV RDD (80% threshold, local-linear, McCrary test)
- NB10: Tightening DiD (pre=2020-21, post=2022-24)
- NB11: Placebo and falsification tests
- NB12: Permutation inference
- NB13: Loan purpose heterogeneity
- NB14: Clustering robustness
- NB15: CCT optimal bandwidth
- NB16: HonestDiD sensitivity (Rambachan-Roth 2023)

**Paper limitation explicitly stated in conclusion:**
Heterogeneous effects across applicant characteristics are unexplored.
Project 1 (below) directly addresses this limitation.

---

### PROJECT 1 / PAPER 2 (IN PROGRESS)
**Title:** Heterogeneous Treatment Effects in Mortgage Lending
**Repository:** github.com/Rajveer-code/CATE-HMDA-Heterogeneous-Effects
**Location:** D:\CATE-HMDA-Heterogeneous-Effects
**Target:** arXiv preprint by end of Month 2 (May 2026)
**Journal target:** FAccT 2026 (ACM Fairness, Accountability, Transparency) or JASA

**The scientific question:**
The average treatment effect is -10.6 pp. But averages hide everything.
For which types of Black applicants is the discrimination largest?
Is it worse for high-income applicants (animus) or lower-income applicants (structural)?
Does it concentrate at specific lenders? Does it vary with AUS type?

**Methods:** Causal Forests (Wager & Athey, 2018) + Double Machine Learning (Chernozhukov et al., 2018)

---

## DATA FACTS

**Raw HMDA files:** C:\Users\Asus\Downloads\credit_fairness_economics\data\
- hmda_2020.csv (9.7 GB), hmda_2021.csv (10.0 GB), hmda_2022.csv (6.1 GB)
- hmda_2023.csv (4.4 GB), hmda_2024.csv (4.6 GB)
- Symlinked into D:\CATE-HMDA-Heterogeneous-Effects\data\

**Processed panels:** D:\CATE-HMDA-Heterogeneous-Effects\data\processed\
- panel_2020.csv through panel_2024.csv (from Repo 1, NB01)

**Key generated files:**
- data/features_panel.parquet — 42,296,010 rows, 37 columns (main feature matrix)
- data/all_years_merged.parquet — 43,441,950 rows, 22 columns (pre-feature-engineering)
- data/trim_bounds.json — {trim_lo: 0.0328, trim_hi: 0.5801, mean_auc: 0.7291}
- data/feature_sets.json — X_FULL (33), X_BASE (4), X_HETERO (9)
- data/dml_residuals.parquet — T_resid, Y_resid from NB19 (for NB20)
- data/cate_estimates.parquet — individual CATE estimates from NB21

---

## FEATURE SETS

**X_BASE (4 features — matches Repo 1 controls):**
income, loan_amount, property_value, ltv

**X_FULL (33 features — full CATE estimation set):**
income, loan_amount, property_value, ltv,
log_income, log_loan_amount, log_property_val,
dti_midpoint, dti_high, dti_missing,
purpose_purchase, purpose_refi, purpose_homeimprv,
type_conventional, type_fha, type_va, type_usda,
occ_primary, occ_second, occ_investment,
lender_small, lender_mid, lender_large,
aus_automated, aus_exempt,
high_minority_tract, low_minority_tract, tract_minority_pct,
applicant_age_mid,
near_pmi_threshold, above_pmi, post_tightening, year

NOTE: tract_minority_pct is all zeros (raw column was dropped before encoding in NB17).
This is a known limitation — noted in paper, will be fixed in Project 2 if needed.

**X_HETERO (9 features — effect modifiers for CATE plots):**
income, ltv, purpose_purchase, purpose_refi,
lender_small, lender_mid, lender_large,
post_tightening, near_pmi_threshold

---

## COMPLETED NOTEBOOKS — RESULTS AND STATUS

### NB17 — Feature Engineering ✅ COMPLETE
**Output:** features_panel.parquet
**Key results:**
- 42,296,010 rows after LTV filter (removed 1,145,940 with invalid LTV)
- 37 columns total, 33 in X_FULL
- DTI coverage: 98.2% of rows (1.8% imputed with median)
- DTI median: 38.0%, high DTI (≥43% QM threshold): 32.1%
- AUS automated (DU/LPA/TOTAL): 67.0% of applications
- AUS exempt/manual: 29.2%
- Site-built: 96.1%, Manufactured: 3.9%
- Applicant age median: 47.1 years
- Zero missing values in all key columns
- All 7 verification checks passed

**What to tell an interviewer:**
"I built the feature matrix for the causal ML models. The critical addition
beyond my published paper was debt-to-income ratio — the main missing control
that reviewers challenge in HMDA studies. DTI covers 98.2% of applications.
I also added automated underwriting system type, which lets me directly test
the Bartlett et al. (2022) finding that algorithmic lenders discriminate less."

### NB18 — Overlap Diagnostics ✅ COMPLETE
**Output:** trim_bounds.json, nb18_overlap_plot.png, nb18_overlap_by_year.png
**Key results:**
- Propensity model: LightGBM, 5-fold cross-fitted
- Cross-validated AUC: 0.7291 (good overlap — not extreme separability)
- Propensity score range: [0.0098, 0.8498]
- Trim bounds (1st-99th pct): [0.0328, 0.5801]
- Common support: 98.0% of sample retained
- Trimmed: 2.0% (40,000 of 2,000,000 rows)
- Approval gap within common support: 15.02 pp (LARGER than raw 14.90 pp)
- Year-by-year AUC: 0.735 (2020) declining to 0.712 (2024) — improving overlap
- All 5 verification checks passed

**What to tell an interviewer:**
"Before running the Causal Forest I verified the overlap assumption —
that Black and White applicants with similar financial profiles co-exist
in the data. The propensity score AUC of 0.73 means financial characteristics
can distinguish the groups with 73% accuracy, reflecting genuine financial
differences on average. But 98% of the sample falls in the common support
region, meaning CATE estimates are valid for essentially the full population.
Critically, the approval gap within common support is 15.02 pp — larger than
the raw gap — confirming that observable financial differences do not explain
the disparity."

### NB19 — Double ML Baseline ✅ COMPLETE
**Output:** nb19_dml_ate_results.csv, nb19_dml_by_year.csv, dml_residuals.parquet
**Key results:**
- Sample: 2,000,000 rows (400K Black, 1.6M White), seed=42
- Raw gap in sample: 14.95 pp
- Treatment model AUC: 0.7316 (consistent with NB18)
- Outcome model AUC: 0.8169 (LightGBM predicts approval well from financials)
- DML ATE (X_FULL, 33 features): -9.3851 pp
- SE (HC3-robust): 0.0712 pp
- t-statistic: -131.80, p-value: 0.00 (effectively zero)
- 95% CI: [-9.5247, -9.2456] pp
- DML ATE (X_BASE, 4 features): -13.17 pp
- Difference X_BASE vs X_FULL: 3.79 pp (explained by DTI + AUS + age)
- % unexplained by X_FULL: 62.8% of raw gap
- Sanity check vs Repo 1 (-10.6 pp): difference = 1.21 pp ✅ PASS
- Year-by-year: all years negative, -10.04 pp (2020) to -8.86 pp (2024)
- Monotonically growing: NO (slight improvement 2020→2024 with full controls)
- All 6 verification checks passed

**What to tell an interviewer:**
"Double ML extends the Frisch-Waugh-Lovell theorem to non-linear nuisance
models. Instead of linearly partialling out covariates, I used LightGBM
to remove all variation in both race and approval that is predictable from
financial characteristics. The residual regression then recovers the
unexplained racial penalty. With 33 controls including DTI and AUS type,
the penalty is -9.39 pp — within 1.21 pp of my published estimate, validating
the pipeline. DTI and AUS type together explain 3.79 pp of the gap but 62.8%
remains completely unexplained."

**Key scientific point:**
The X_BASE vs X_FULL comparison is itself a finding.
DTI explains some gap — but even with DTI, 9.39 pp survives.
This directly rebuts the 'missing controls' critique of the published paper.

### NB21 — Causal Forest CATE ⏳ CURRENTLY RUNNING
**Status:** Cell 4 training (500 trees, 45-75 min runtime)
**Expected outputs:** cate_estimates.parquet, nb21_cate_distribution.png, nb21_cate_by_subgroup.png
**What we expect:**
- Forest ATE should match NB19 within ~5 pp
- CATE std > 1 pp (meaningful heterogeneity)
- CATE by income quintile will answer: animus vs structural bias
- If Q5 CATE more negative: high-income Black face largest penalty = animus
- If Q1 CATE more negative: low-income face largest penalty = structural

---

## REMAINING NOTEBOOKS TO BUILD

### NB22 — SHAP Attribution
**Purpose:** Which covariates drive heterogeneity in CATE?
**Method:** shap.TreeExplainer on fitted Causal Forest
**Runtime:** ~15-20 minutes
**Expected outputs:** SHAP beeswarm plot, SHAP dependence plots
**Key question:** Is it income? LTV? AUS type? Lender size?

### NB23 — Disparity Map (FLAGSHIP VISUALISATION)
**Purpose:** Income × LTV × lender-tier heatmap of CATE estimates
**This is the most visually impressive output of the project**
**Runtime:** ~10 minutes
**Expected outputs:** Interactive Plotly heatmap, static PNG for paper

### NB24 — Subgroup RDD
**Purpose:** Re-estimate 80% LTV discontinuity by income quintile
**Question:** Is the 2.0 pp PMI boundary effect concentrated in high-income applicants?
**Runtime:** ~20-30 minutes
**Connects to:** Repo 1 NB09 (the RDD result)

### NB25 — Subgroup DiD
**Purpose:** Re-estimate 2022 tightening effect by CATE quartile
**Question:** Did the 1.5 pp widening hit all applicants equally or concentrate?
**Runtime:** ~20-30 minutes
**Connects to:** Repo 1 NB10 (the DiD result)

### NB26 — Paper Figures
**Purpose:** Publication-ready versions of all figures
**Runtime:** ~15 minutes
**Output:** All figures at 300 DPI, LaTeX-compatible formatting

---

## 5-MONTH MASTER PLAN

### Month 1 (March-April 2026) — CURRENTLY IN PROGRESS
Complete NB21 → NB22 → NB23 → NB24 → NB25 → NB26
Pace: 1 notebook per day (have full days available)
Each notebook: run it, understand output deeply, commit, LinkedIn post

### Month 2 (April-May 2026) — Paper writing
Write full paper draft for Project 1
Structure: Introduction, Theory (Becker vs Phelps), Data, DML methodology,
Causal Forest methodology, Results (ATE → CATE distribution → subgroups →
SHAP → subgroup RDD/DiD), Discussion, Conclusion
Target length: 12,000-15,000 words
Upload to arXiv by end of Month 2
Submit to FAccT 2026 or JASA Applications track

### Month 3 (May-June 2026) — Project 2
**Topic:** Lender-level analysis — which specific lenders drive the gap?
**Using same HMDA data already downloaded**
**Key questions:**
- Which lenders have the largest within-institution racial gaps?
- Are they concentrated in specific states or regions?
- Are they improving or worsening over time?
- Are they large national banks or small community lenders?
- Does lender HHI (market concentration) predict gap size?
**Estimated notebooks:** 4-5 notebooks
**Target:** SSRN working paper + GitHub repo
**Why this is valuable:** Policy-relevant (regulatory targeting), uses existing data,
natural extension of both papers, adds lender-level heterogeneity angle

### Months 4-5 (June-August 2026) — Polish and applications
Build interactive disparity map web tool
- Plotly Dash or Observable — shows CATE by income/LTV/lender interactively
- Hosted on GitHub Pages or Heroku
- Linked prominently on GitHub profile and LinkedIn
- Shows non-specialists the research without reading the paper
Submit SOP drafts to advisors for review
Write research statements for each university (tailored)
Apply to ETH Zurich (deadline typically December)
Apply to Cambridge MPhil (deadline typically December)
Apply to Oxford StatML (deadline typically January)

---

## LINKEDIN STRATEGY

**Posting rhythm:** Once per week, Tuesday or Wednesday
**Every post:** one concrete finding, one image, under 300 words, no corporate language

**Posts completed:**
1. ✅ Project announcement (March 2026) — "I disappeared for 4 months, here's what I built"

**Upcoming posts:**
2. NB18 result — overlap diagnostics, propensity score plot image
3. NB19 result — DML ATE = -9.39 pp, residual plot image
4. NB21 result — CATE distribution histogram (THE viral post)
5. NB22 result — SHAP plot showing which features drive heterogeneity
6. NB23 result — disparity map image
7. Paper draft announced — link to arXiv preprint
8. Project 2 announced

**Post tone:** Direct, first-person, no buzzwords, leads with a human observation
not a technical claim. Explains why it matters before explaining what it is.

---

## GITHUB STATUS

**Rajveer-code profile:** https://github.com/Rajveer-code
**Primary email:** rajveerpall04@gmail.com (correctly linked, verified March 2026)
**Old account deleted:** rajveerpall05-glitch (deleted March 2026, was causing wrong attribution)
**Profile README:** Created with both research projects listed
**Pinned repos:** hmda-racial-disparities, CATE-HMDA-Heterogeneous-Effects, diabetes-xai-research
**Bio:** "Researcher · Causal inference & ML · Racial disparities in U.S. mortgage lending · 42M applications · MSc applicant 2027"

**Commit convention:**
Every completed notebook = 1 commit with format:
"NB[XX] complete: [key result in one line]"
Example: "NB19 complete: DML ATE=-9.39pp, sanity check passed (Repo1 diff=1.21pp), p<0.001"

---

## INTERVIEW PREPARATION — KEY NUMBERS TO KNOW COLD

Memorise these. You will be asked about them.

| Fact | Number |
|------|--------|
| Total applications | 42,323,519 |
| Years covered | 2020–2024 |
| Number of lenders | 5,500+ |
| Raw Black-White gap | 14.95 pp |
| Gap unexplained by DFL | 98.6% |
| Within-lender share | 74.6% |
| Within-lender FE (Repo 1) | -10.6 pp |
| RDD effect at 80% LTV | +2.0 pp additional |
| DiD effect post-2022 | +1.5 pp widening |
| NB18 propensity AUC | 0.729 |
| Common support | 98.0% |
| DML ATE (X_FULL) | -9.39 pp |
| DML ATE (X_BASE) | -13.17 pp |
| DTI explains | 3.79 pp |
| % gap unexplained by DML | 62.8% |
| DTI coverage in data | 98.2% |

---

## KEY PAPERS TO CITE (know these authors and years)

- Wager & Athey (2018) — Causal Forests, JASA
- Chernozhukov et al. (2018) — Double ML, Econometrics Journal
- Bartlett et al. (2022) — FinTech lending discrimination, Journal of Financial Economics
- Bhutta & Hizmo (2021) — Mortgage pricing discrimination, Review of Financial Studies
- Bhutta, Hizmo & Ringo (2025) — Human vs algorithmic credit decisions, Journal of Finance
- Munnell et al. (1996) — Boston Fed HMDA study, American Economic Review
- DiNardo, Fortin & Lemieux (1996) — DFL decomposition, Econometrica
- Rambachan & Roth (2023) — HonestDiD, Review of Economic Studies
- Calonico, Cattaneo & Titiunik (2014) — CCT bandwidth, Econometrica
- Becker (1957) — Taste-based discrimination (theoretical framework)
- Phelps (1972) — Statistical discrimination (theoretical framework)
- Lundberg & Lee (2017) — SHAP values, NeurIPS

---

## TECHNICAL DECISIONS MADE AND WHY

**Why Polars instead of pandas for CSV reading:**
pandas reads CSV single-threaded; Polars uses all 14 CPU cores via Rust.
Result: 3 minutes total extraction vs 6+ minutes with pandas chunks.

**Why stratified sampling (not full 42M rows):**
16GB RAM cannot hold 42M rows + model in memory simultaneously.
2M stratified sample (Black/White ratio preserved) gives consistent estimates.
This is standard practice — DML/Causal Forest ATEs are consistent on samples.

**Why LightGBM as nuisance model (not logistic regression):**
LightGBM captures non-linear relationships and interactions automatically.
Logistic regression would miss income² effects, income×LTV interactions, etc.
Result: outcome model AUC 0.817 vs ~0.72 for logistic regression.

**Why 5-fold cross-fitting:**
Eliminates regularisation bias — each row's residual is computed by a model
that never trained on that row. Standard requirement for DML consistency.

**Why HC3 standard errors:**
Heteroskedasticity-robust. With 2M observations the SE is tiny anyway (0.07 pp)
but HC3 is the correct choice for a binary outcome in an LPM regression.

**Why 1st-99th percentile trimming (not Crump 0.1-0.9):**
Crump would trim 25.1% of sample. 1st-99th trims only 2.0%.
With 98% overlap, aggressive trimming is unnecessary and loses information.
Crump bounds reported as robustness check.

**Known limitation — tract_minority_pct all zeros:**
The raw column was dropped before encoding in NB17 (memory management issue).
All other 32 features are correct. This variable is set to zero for all rows.
Noted as limitation. Can be fixed in Project 2 or a robustness appendix.

---

## HOW TO START A NEW CLAUDE SESSION

1. Open new Claude conversation
2. Paste this entire file
3. Say: "I am Rajveer. Continue helping me with my CATE-HMDA project.
         I just finished [NB_XX] and the output was [paste Cell 10 output].
         Help me with NB_YY next."
4. Claude will have full context immediately.

Keep this file updated after each completed notebook by adding the results
to the COMPLETED NOTEBOOKS section.
