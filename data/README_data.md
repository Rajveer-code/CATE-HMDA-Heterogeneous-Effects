# Data Acquisition

Raw data are NOT tracked by git due to file size (~15 GB total).

## Source

Home Mortgage Disclosure Act (HMDA) data, Consumer Financial Protection Bureau:
https://ffiec.cfpb.gov/data-browser/

## Download Instructions

1. Go to https://ffiec.cfpb.gov/data-browser/data/2024?category=nationwide
2. Select: Actions Taken = Application approved but not accepted, Loan originated, Application denied
3. Select years: 2020, 2021, 2022, 2023, 2024 (download separately)
4. Place in this directory as: hmda_2020.csv, hmda_2021.csv, etc.

## Key Variables Used

| Variable | HMDA Name | Description |
|----------|-----------|-------------|
| approved | action_taken | 1 = originated/approved, 0 = denied |
| black | derived_race | 1 = Black or African American applicant |
| income | applicant_income | Reported gross annual income ($000s) |
| ltv | loan_to_value_ratio | Loan amount / Property value |
| dti | debt_to_income_ratio | Total monthly debt / Gross monthly income |
| aus_type | automated_underwriting_system | AUS type used by lender |
| loan_purpose | loan_purpose | 1=Purchase, 2=Refi, 31=Home improvement |
| loan_type | loan_type | 1=Conventional, 2=FHA, 3=VA, 4=USDA |
