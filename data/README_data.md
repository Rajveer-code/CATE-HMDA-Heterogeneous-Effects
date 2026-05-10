# Data

Raw data files are **not tracked by git** due to file size (~15 GB total across five years). This document describes how to acquire and prepare the data required to reproduce all results.

---

## Source

**Home Mortgage Disclosure Act (HMDA) data**  
Consumer Financial Protection Bureau (CFPB)  
https://ffiec.cfpb.gov/data-browser/

HMDA requires most U.S. mortgage lenders to publicly report loan-level application data. The dataset covers applications for home purchase, refinance, and home improvement loans, with reported characteristics including applicant income, loan amount, property location, and disposition (originated, denied, withdrawn, etc.).

---

## Download Instructions

1. Navigate to https://ffiec.cfpb.gov/data-browser/data/2024?category=nationwide
2. Under **Actions Taken**, select: *Loan originated*, *Application approved but not accepted*, *Application denied*
3. Under **Race**, select: *White* and *Black or African American*
4. Download as CSV for each year: **2020, 2021, 2022, 2023, 2024**
5. Place the downloaded files in this directory as:
   ```
   data/hmda_2020.csv
   data/hmda_2021.csv
   data/hmda_2022.csv
   data/hmda_2023.csv
   data/hmda_2024.csv
   ```

Each annual file is approximately 2–5 GB. Files are listed in `.gitignore` and will not be accidentally committed.

---

## Key Variables

The following HMDA fields are used in this analysis:

| Constructed Variable | HMDA Field | Description |
|---|---|---|
| `approved` | `action_taken` | Binary: 1 = originated or approved-not-accepted, 0 = denied |
| `black` | `derived_race` | Binary: 1 = Black or African American applicant |
| `income` | `income` | Reported gross annual income (thousands USD) |
| `ltv` | `loan_to_value_ratio` | Loan amount ÷ property value (%) |
| `dti` | `debt_to_income_ratio` | Total monthly debt ÷ gross monthly income (%) |
| `aus_automated` | `aus_1` | Binary: 1 = automated underwriting system used |
| `purpose_purchase` | `loan_purpose` | Binary: 1 = home purchase loan |
| `loan_type` | `loan_type` | 1 = Conventional, 2 = FHA, 3 = VA, 4 = USDA/RHS |
| `log_income` | derived | Natural log of reported income |
| `log_loan` | derived | Natural log of loan amount |
| `lender_large` | derived | Binary: 1 = top-quartile lender by volume |

See `notebooks/NB17_feature_engineering.ipynb` for the complete feature construction pipeline (37 features total).

---

## Processed Data Files

After running `NB17_feature_engineering.ipynb`, the following files are created:

| File | Description | Size |
|---|---|---|
| `features_panel.parquet` | All 42.3M rows × 37 features (Parquet format) | ~4.5 GB |
| `cate_estimates.parquet` | Individual CATEs for the 1.5M estimation sample | ~150 MB |

These files are listed in `.gitignore` and must be regenerated locally.

---

## Sample Sizes by Year

| Year | Total Applications | Black Applicants | White Applicants |
|------|-------------------|------------------|------------------|
| 2020 | 11,246,880 | 537,120 | 10,709,760 |
| 2021 | 11,765,000 | 562,286 | 11,202,714 |
| 2022 | 7,623,920 | 363,996 | 7,259,924 |
| 2023 | 5,497,910 | 262,295 | 5,235,615 |
| 2024 | 6,162,300 | 274,303 | 5,887,997 |
| **Total** | **42,296,010** | **2,000,000** | **40,296,010** |

---

## Notes

- The 33 creditworthiness features used in the DML model are defined in `data/feature_sets.json` under the key `X_FULL`.
- Propensity score trim bounds [0.033, 0.580] are stored in `data/trim_bounds.json` and applied during estimation to ensure overlap.
- The estimation sample of 1.5 million observations is a stratified random sample (by year and race) drawn in `NB21_causal_forest_cate.ipynb` using `seed=123`.
