# Project Context for Claude Sessions

## Who I am
Rajveer Singh Pall, B.Tech CS, Gyan Ganga Institute of Technology and Sciences, Jabalpur India
MSc applicant 2027 — ETH Zurich, Cambridge, Oxford

## What exists
- Repo 1: github.com/Rajveer-code/hmda-racial-disparities
  16 notebooks, 42M HMDA applications, RDD + DiD + DFL, submitted JREFE
  Key result: -10.6pp within-lender racial approval penalty

- Repo 2 (Project 1): github.com/Rajveer-code/CATE-HMDA-Heterogeneous-Effects
  NB17 done: 42.3M rows, 33 features, features_panel.parquet
  NB18 done: overlap AUC=0.729, 98% common support, trim=[0.033,0.580]
  NB19 done: DML ATE=-9.39pp, sanity check passed, p<0.001
  NB21 running: CausalForestDML 500 trees

## 5-month plan
- Months 1-2: Finish NB21-NB26, paper draft, arXiv upload
- Month 3: Project 2 — lender-level analysis (which lenders drive the gap)
- Months 4-5: Polish, FAccT submission, SOP writing, interactive web tool

## Hardware
i7-13650HX, RTX 4060, 16GB RAM, D: drive (265GB free)
conda env: cate_hmda, Python 3.11

## Key numbers to remember
Raw gap: 14.90pp | DML ATE: -9.39pp | Repo1 FE: -10.6pp
NB18 AUC: 0.729 | Common support: 98% | DTI coverage: 98.2%