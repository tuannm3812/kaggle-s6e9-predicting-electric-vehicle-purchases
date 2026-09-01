# Submission Manifest

Every leaderboard submission, recorded the moment it is scored, per
`docs/0_coding_standards.md`. One submission per accepted hypothesis.

| # | Date (UTC) | Sub id | Kernel / version | Model | OOF AUC (F1) | Public LB | Hypothesis → verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-01 13:19 | 55940961 | `ev-purchases-baseline-modeling` v2 | `e01_cat_2000x05` | 0.94177 (Kaggle run; 0.94176 local) | **0.94169** | CV tracks LB (EDA no-drift evidence) → **confirmed**: gap −0.00008, well inside fold std (~0.0007) |

## Notes

- Submitted via the kernel-version flow (`-k tuannm3812/ev-purchases-baseline-modeling -v 2`),
  so the score is tied to code Kaggle executed (master standard §11).
  Artifact pre-validated with `scripts/verify_submission.py` (286,571 rows,
  range [0.0000, 0.9893]).
- Quota use: 1 of 10 daily. Standing at submission time: rank 79
  of 157 teams (2026-09-01 — mutable, re-check live).
- Decision: champion stands. Next submission only after a new paired-gate
  promotion; the blend path is closed by the diversity bar
  (`docs/4_experiment_ledger.md`).
