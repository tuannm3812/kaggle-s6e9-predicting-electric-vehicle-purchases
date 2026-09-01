# Submission Manifest

Every leaderboard submission, recorded the moment it is scored, per
`docs/0_coding_standards.md`. One submission per accepted hypothesis.

| # | Date (UTC) | Sub id | Kernel / version | Model | OOF AUC (F1) | Public LB | Hypothesis → verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-09-01 13:19 | 55940961 | `ev-purchases-baseline-modeling` v2 | `e01_cat_2000x05` | 0.94177 (Kaggle run; 0.94176 local) | **0.94169** | CV tracks LB (EDA no-drift evidence) → **confirmed**: gap −0.00008, well inside fold std (~0.0007) |
| 2 | 2026-09-01 19:27 | 55946584 | `ev-purchases-baseline-modeling` v3 | `e02_cat_interactions` | 0.94204 (Kaggle run) | **0.94198** | subsidy crosses improve the champion (E02, paired-gate promoted) → **confirmed**: LB +0.00029 vs. OOF +0.00027; CV↔LB gap −0.00006 |

## Notes

- Submitted via the kernel-version flow (`-k tuannm3812/ev-purchases-baseline-modeling -v 2`),
  so the score is tied to code Kaggle executed (master standard §11).
  Artifact pre-validated with `scripts/verify_submission.py` (286,571 rows,
  range [0.0000, 0.9893]).
- Quota use: submission 2 left 8/10 on its day. Standing after
  submission 2: rank 83 of 227 teams (2026-09-02 — mutable,
  re-check live). Was 79/157 after submission 1.
- Decision: champion stands. Next submission only after a new paired-gate
  promotion; the blend path is closed by the diversity bar
  (`docs/4_experiment_ledger.md`).
